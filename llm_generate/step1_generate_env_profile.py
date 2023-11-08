import asyncio
import random
from typing import TypeVar
from tqdm import tqdm

import pandas as pd
import rich
from pydantic import BaseModel

from sotopia.database import EnvironmentProfile
from generate import agenerate_env_profile

T = TypeVar("T", bound=BaseModel)

def pydantics_to_csv(filename: str, data: list[T]) -> None:
    pd.DataFrame([item.dict() for item in data]).to_csv(filename, index=False)


random.seed(41)

envs = EnvironmentProfile.find().all()
ins_prompts = pd.read_csv("./inspirational_prompt_for_env.csv")
prompts = [prompt.strip().replace('\"', '') for prompt in ins_prompts["prompt"].tolist()]

# randomly choose 3 prompts
sampled_examples = []
for i in range(len(prompts)):
    sampled_envs = random.sample(envs, 5)
    sampled_examples.append(f"{sampled_envs[0].json()}\n\n{sampled_envs[1].json()}\n\n{sampled_envs[2].json()}\n\n{sampled_envs[3].json()}\n\n{sampled_envs[4].json()}")

backgrounds = []
for prompt, sampled_example in tqdm(zip(prompts, sampled_examples)):
    rich.print(prompt)
    background, prompt_full = asyncio.run(
        agenerate_env_profile(
            model_name="gpt-4",
            inspiration_prompt=prompt,
            examples=sampled_example,
            temperature=1.5,
        )
    )
    rich.print(background)
    rich.print(prompt_full)
    backgrounds.append(background)

    pydantics_to_csv("./backgrounds.csv", backgrounds)