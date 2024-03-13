import csv
import os

import jsonlines
import pandas as pd
from tqdm import tqdm


def collect_social_iqa():
    inspirational_prompt_data = []
    with jsonlines.open(
        os.getcwd() + "/data_generate/env_files/social_iqa_train.jsonl", "r"
    ) as f:
        social_iqa_dataset = list(f)
    for data in social_iqa_dataset:
        inspirational_prompt_data.append(
            {"prompt": data["context"], "source": "social_iqa"}
        )
    prompt_df = pd.DataFrame.from_records(inspirational_prompt_data)
    prompt_df = prompt_df.drop_duplicates()
    return prompt_df


def collect_normbank():
    normbank_df = pd.read_csv(os.getcwd() + "/data_generate/env_files//NormBank.csv")[
        ["behavior"]
    ]
    normbank_df = normbank_df.rename(columns={"behavior": "prompt"})
    normbank_df = normbank_df.drop_duplicates().reset_index(drop=True)
    normbank_df["source"] = "normbank"

    return normbank_df


def collect_social_chemistry():
    social_chem_df = pd.read_csv(
        os.getcwd() + "/data_generate/env_files/social-chem-101.v1.0.tsv",
        delimiter="\t",
    )[["situation"]]
    social_chem_df = social_chem_df.rename(columns={"situation": "prompt"})
    social_chem_df = social_chem_df.drop_duplicates().reset_index(drop=True)
    social_chem_df["source"] = "social_chem"

    return social_chem_df


def collect_persuation_for_good():
    # NOTE this function is not used for now
    from convokit import Corpus, download

    corpus = Corpus(filename=download("persuasionforgood-corpus"))
    import pdb

    pdb.set_trace()


def delete_sotopia_data(inspirational_prompt_df):
    sotopia_prompts = []
    sotopia_prompt_df = pd.read_csv(
        os.getcwd() + "/data_generate/env_files/inspirational_prompt_for_sotopia.csv"
    )
    sotopia_prompts = sotopia_prompt_df.prompt.tolist()
    inspirational_prompt_df = inspirational_prompt_df[
        ~inspirational_prompt_df["prompt"].isin(sotopia_prompts)
    ]
    # print(len(inspirational_prompt_data))
    return inspirational_prompt_df


if __name__ == "__main__":
    social_chem_prompt = collect_social_chemistry()
    social_iqa_prompt = collect_social_iqa()
    normbank_prompt = collect_normbank()
    concat_prompt = pd.concat([social_chem_prompt, social_iqa_prompt, normbank_prompt])
    inspirational_prompt_data = delete_sotopia_data(concat_prompt)
    inspirational_prompt_data = inspirational_prompt_data.drop_duplicates(
        subset=["prompt"], keep="first"
    )
    inspirational_prompt_data.to_csv(
        os.getcwd() + "/data_generate/env_files/inspirational_prompt.csv"
    )
