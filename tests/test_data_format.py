import ast
import csv
from typing import Any, cast

import pandas as pd


def test_social_goal_number() -> None:
    with open("./data_generate/backgrounds_gpt-4-turbo_1222.csv", "r") as f:
        df = pd.read_csv(f)
        envs = cast(list[dict[str, Any]], df.to_dict(orient="records"))
        for env in envs:
            env["agent_goals"] = ast.literal_eval(env["agent_goals"])
            assert len(env["agent_goals"]) == 2
            assert type(env["pk"]) == str
            assert type(env["relationship"]) == int
