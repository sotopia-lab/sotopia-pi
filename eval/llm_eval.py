import json
from tqdm import tqdm

from langchain.llms import OpenAI
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from langchain.pydantic_v1 import BaseModel, Field


class QuantitativeEval(BaseModel):
    agent1_name: str = Field(description="Agent 1's name")
    agent1_gain: int = Field(description="Agent 1's gain/loss")
    agent2_name: str = Field(description="Agent 2's name")
    agent2_gain: int = Field(description="Agent 2's gain/loss")


def get_model_parser(model_name='text-davinci-003') -> (PromptTemplate, PydanticOutputParser):
    model = OpenAI(model_name=model_name, temperature=0.0)
    parser = PydanticOutputParser(pydantic_object=QuantitativeEval)

    prompt_text = (
        "Try to understand the following situation and answer the question in the end. "
        "\n Situation: {situation}"
        "\n Question: {question}"
        "\n Please represent loss as negative values. {format_instructions}\n "
    )

    prompt = PromptTemplate(
        template=prompt_text,
        input_variables=["situation", "question"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )

    prompt_and_model = prompt | model

    return prompt_and_model, parser


def evaluate(environment_episode_map, environment_question_map, model_name='text-davinci-003'):
    results = {}
    model, response_parser = get_model_parser(model_name=model_name)
    
    for environment_id, episodes in tqdm(environment_episode_map.items()):
        results_for_env = []

        for episode in episodes:
            situation = episode["messages_and_rewards"]
            question = environment_question_map.get(environment_id)
            
            if question:
                model_response = model.invoke({"situation": situation, "question": question})
                parsed_output = response_parser.parse(model_response)
                episode["output"] = parsed_output.dict()
                
            results_for_env.append(episode)

        results[environment_id] = results_for_env

    return results


def main():
    with open("human_readable_eps_by_env.json", "r") as f:
        env_eps_map = json.load(f)
        
    with open("env_specific_eval.json", "r") as f:
        env_question_map = json.load(f)
        
    res = evaluate(env_eps_map, env_question_map)
    
    with open("env_specific_eval_with_output.json", "w") as f:
        json.dump(res, f)

if __name__ == "__main__":
    main()