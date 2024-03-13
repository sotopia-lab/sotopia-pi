from dataclasses import dataclass, field
from typing import Literal, Optional


@dataclass
class GeneralArguments:
    r"""
    Arguments pertaining to which stage we are going to perform.
    """

    stage: Optional[Literal["pt", "sft", "rm", "ppo", "dpo"]] = field(
        default="sft",
        metadata={"help": "Which stage will be performed in training."},
    )
