"""
A controller manages distributed workers.
It sends worker addresses to clients.
"""
import argparse
import asyncio
import dataclasses
import logging
import time
from typing import List, Union
import threading

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import numpy as np
import requests
import uvicorn

from chatserver.constants import CONTROLLER_HEART_BEAT_EXPIRATION
from chatserver.utils import build_logger


logger = build_logger("controller", "controller.log")


@dataclasses.dataclass
class WorkerInfo:
    model_names: List[str]
    speed: int
    check_heart_beat: bool
    last_heart_beat: str


def heart_beat_controller(controller):
    while True:
        time.sleep(CONTROLLER_HEART_BEAT_EXPIRATION)
        controller.remove_stable_workers_by_expiration()


class Controller:
    def __init__(self):
        # Dict[str -> WorkerInfo]
        self.worker_info = {}

        self.heart_beat_thread = threading.Thread(
            target=heart_beat_controller, args=(self,))
        self.heart_beat_thread.start()

        logger.info("Init controller")

    def register_worker(self, worker_name: str, check_heart_beat: bool,
                        worker_status: dict):
        if worker_name not in self.worker_info:
            logger.info(f"Register a new worker: {worker_name}")
        else:
            logger.info(f"Register an existing worker: {worker_name}")

        if not worker_status:
            worker_status = self.get_worker_status(worker_name)
        if not worker_status:
            return False

        self.worker_info[worker_name] = WorkerInfo(
            worker_status["model_names"], worker_status["speed"],
            check_heart_beat, time.time())

        logger.info(f"Register done: {worker_name}, {worker_status}")
        return True

    def get_worker_status(self, worker_name: str):
        try:
            r = requests.post(worker_name + "/worker_get_status", timeout=5)
        except requests.exceptions.RequestException as e:
            logger.error(f"Get status fails: {worker_name}, {e}")
            return None

        if r.status_code != 200:
            logger.error(f"Get status fails: {worker_name}, {r}")
            return None

        return r.json()

    def remove_worker(self, worker_name: str):
        del self.worker_info[worker_name]

    def refresh_all_workers(self):
        old_info = dict(self.worker_info)
        self.worker_info = {}

        for w_name, w_info in old_info.items():
            if not self.register_worker(w_name, w_info.check_heart_beat, None):
                logger.info(f"Remove stale worker: {w_name}")

    def list_models(self):
        model_names = set()

        for w_name, w_info in self.worker_info.items():
            model_names.update(w_info.model_names)

        return list(model_names)

    def get_worker_address(self, model_name: str):
        worker_names = []
        worker_speeds = []
        for w_name, w_info in self.worker_info.items():
            if model_name in w_info.model_names:
                worker_names.append(w_name)
                worker_speeds.append(w_info.speed)
        worker_speeds = np.array(worker_speeds, dtype=np.float32)
        norm = np.sum(worker_speeds)
        if norm < 1e-4:
            return ""
        worker_speeds = worker_speeds / norm

        if True:  # Directly return address
            pt = np.random.choice(np.arange(len(worker_names)),
                p=worker_speeds)
            worker_name = worker_names[pt]
            return worker_name

        # Check status before returning
        while True:
            pt = np.random.choice(np.arange(len(worker_names)),
                p=worker_speeds)
            worker_name = worker_names[pt]

            if self.get_worker_status(worker_name):
                break
            else:
                self.remove_worker(worker_name)
                worker_speeds[pt] = 0
                norm = np.sum(worker_speeds)
                if norm < 1e-4:
                    return ""
                worker_speeds = worker_speeds / norm
                continue

        return worker_name

    def receive_heart_beat(self, worker_name: str):
        if worker_name not in self.worker_info:
            logger.info(f"Receive unknow heart beat. {worker_name}")
            return False

        self.worker_info[worker_name].last_heart_beat = time.time()
        logger.info(f"Receive heart beat. {worker_name}")
        return True

    def remove_stable_workers_by_expiration(self):
        expire = time.time() - CONTROLLER_HEART_BEAT_EXPIRATION
        to_delete = []
        for worker_name, w_info in self.worker_info.items():
            if w_info.check_heart_beat and w_info.last_heart_beat < expire:
                to_delete.append(worker_name)

        for worker_name in to_delete:
            self.remove_worker(worker_name)

    def worker_api_generate_stream(self, params):
        worker_addr = self.get_worker_address(params["model"])
        if not worker_addr:
            ret = {
                "text": server_error_msg,
                "error_code": 2,
            }
            yield (json.dumps(ret) + "\0").encode("utf-8")

        response = requests.post(worker_addr + "/worker_generate_stream",
            json=params, stream=True)
        for chunk in response.iter_lines(decode_unicode=False, delimiter=b"\0"):
            if chunk:
                yield chunk + b"\0"

    # Let the controller act as a worker to achieve hierarchical
    # management. This can be used to connect isolated sub networks.
    def worker_api_get_status(self):
        model_names = set()
        speed = 0

        for w_name in self.worker_info:
            worker_status = self.get_worker_status(w_name)
            if worker_status is not None:
                model_names.update(worker_status["model_names"])
                speed += worker_status["speed"]

        return {
            "model_names": list(model_names),
            "speed": speed,
        }


app = FastAPI()


@app.post("/register_worker")
async def register_worker(request: Request):
    data = await request.json()
    controller.register_worker(
        data["worker_name"], data["check_heart_beat"],
        data.get("worker_status", None))


@app.post("/refresh_all_workers")
async def refresh_all_workers():
    models = controller.refresh_all_workers()


@app.post("/list_models")
async def list_models():
    models = controller.list_models()
    return {"models": models}


@app.post("/get_worker_address")
async def get_worker_address(request: Request):
    data = await request.json()
    addr = controller.get_worker_address(data["model"])
    return {"address": addr}


@app.post("/receive_heart_beat")
async def receive_heart_beat(request: Request):
    data = await request.json()
    exist = controller.receive_heart_beat(data["worker_name"])
    return {"exist": exist}


@app.post("/worker_generate_stream")
async def worker_api_generate_stream(request: Request):
    params = await request.json()
    generator = controller.worker_api_generate_stream(params)
    return StreamingResponse(generator)


@app.post("/worker_get_status")
async def worker_api_get_status(request: Request):
    return controller.worker_api_get_status()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="localhost")
    parser.add_argument("--port", type=int, default=21001)
    args = parser.parse_args()

    controller = Controller()

    uvicorn.run(app, host=args.host, port=args.port, log_level="info")
