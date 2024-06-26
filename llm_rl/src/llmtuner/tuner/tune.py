from typing import TYPE_CHECKING, Any, Dict, List, Optional

import wandb
from llmtuner.extras.callbacks import LogCallback
from llmtuner.extras.logging import get_logger
from llmtuner.tuner.core import (
    get_infer_args,
    get_train_args,
    load_model_and_tokenizer,
)
from llmtuner.tuner.core.utils import is_first_node
from llmtuner.tuner.dpo import run_dpo
from llmtuner.tuner.ppo import run_ppo
from llmtuner.tuner.pt import run_pt
from llmtuner.tuner.rm import run_rm
from llmtuner.tuner.sft import run_sft

if TYPE_CHECKING:
    from transformers import TrainerCallback


logger = get_logger(__name__)


def run_exp(
    args: Optional[Dict[str, Any]] = None,
    callbacks: Optional[List["TrainerCallback"]] = None,
):
    (
        model_args,
        data_args,
        training_args,
        finetuning_args,
        generating_args,
    ) = get_train_args(args)
    callbacks = [LogCallback()] if callbacks is None else callbacks
    if is_first_node():
        wandb.login(key=finetuning_args.wandb_token)
        wandb.init(
            project=finetuning_args.wandb_project,
            tags=[*finetuning_args.wandb_tags]
            if finetuning_args.wandb_tags
            else None,
        )

    if finetuning_args.stage == "pt":
        run_pt(
            model_args, data_args, training_args, finetuning_args, callbacks
        )
    elif finetuning_args.stage == "sft":
        run_sft(
            model_args,
            data_args,
            training_args,
            finetuning_args,
            generating_args,
            callbacks,
        )
    elif finetuning_args.stage == "rm":
        run_rm(
            model_args, data_args, training_args, finetuning_args, callbacks
        )
    elif finetuning_args.stage == "ppo":
        run_ppo(
            model_args,
            data_args,
            training_args,
            finetuning_args,
            generating_args,
            callbacks,
        )
    elif finetuning_args.stage == "dpo":
        run_dpo(
            model_args, data_args, training_args, finetuning_args, callbacks
        )
    else:
        raise ValueError("Unknown task.")


def export_model(
    args: Optional[Dict[str, Any]] = None,
    max_shard_size: Optional[str] = "10GB",
):
    model_args, _, finetuning_args, _ = get_infer_args(args)
    model, tokenizer = load_model_and_tokenizer(model_args, finetuning_args)
    model.config.use_cache = True
    model.save_pretrained(model_args.export_dir, max_shard_size=max_shard_size)
    try:
        tokenizer.padding_side = "left"  # restore padding side
        tokenizer.init_kwargs["padding_side"] = "left"
        tokenizer.save_pretrained(model_args.export_dir)
    except:
        logger.warning(
            "Cannot save tokenizer, please copy the files manually."
        )


if __name__ == "__main__":
    run_exp()
