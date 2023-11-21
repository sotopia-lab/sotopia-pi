import openai
import time
import re
import json

localhost_url = "http://localhost:8001/v1"
opensource_url = "https://api.openai.com/v1"
# openai.openai_api_key = "EMPTY"
localhost_model_name = "checkpoint-4525"  # Mistral-7b
opensource_model_name = "gpt-3.5-turbo"
max_turn_num = 20
temperature = 0.3
prompt_file = "../../sotopia-selftrain-data/full_prompts.jsonl"
output_file = "aug_data/self-generate_ft-mistral_gpt-3.5-turbo.jsonl"


def get_agent_name(input):
    pattern = r"Imagine you are (\w+ \w+)"
    match = re.search(pattern, input)
    if match:
        return match.group(1)
    else:
        return ""


def split_input(input):
    separator_start = "You are at Turn #"
    separator_end = "Your available action types are\n"
    part_1, rest = input.split(separator_start, 1)
    part_2 = rest.split(separator_end, 1)[-1]
    return part_1, separator_end + part_2


def update_message(prev_msg, curr_input, turn_num, agent_name):
    part_1, part_2 = split_input(prev_msg)
    output = """{part_1}Turn #{prev_turn_num}: {agent_name} said: \"{curr_input}\"\n\nYou are at Turn #{turn_num}. {part_2}""".format(
        part_1=part_1, prev_turn_num=turn_num-1, agent_name=agent_name, curr_input=curr_input, turn_num=turn_num, part_2=part_2)
    return output


def extract_response(completion):
    response = completion["choices"][0]["message"]["content"]
    pattern = r'"argument":\s*(\".*?\")'
    match = re.search(pattern, response)
    if match:
        return match.group(1).strip('"')
    else:
        pattern = r"'argument':\s*(\".*?\")"
        match = re.search(pattern, response)
        if match:
            return match.group(1).strip('"')
        else:
            return ""


def wrap_message(output):
    return [{"role": "user", "content": output}]


def generate_response(messages, model_name):
    try:
        if model_name == localhost_model_name:
            openai.api_base = localhost_url
        else:
            openai.api_base = opensource_url

        completion = openai.ChatCompletion.create(
            model=model_name,
            messages=messages,
            n=1,
            temperature=temperature
        )
    except:
        print("{model_name} not responding...".format(model_name=model_name))
        time.sleep(20)
        return generate_response(messages)

    return completion


def store_utterance(msg):
    pass


def chat_loop(agent_1_init_prompt, agent_2_init_prompt, agent_1_model, agent_2_model):
    agent_1_name = get_agent_name(agent_1_init_prompt)
    agent_2_name = get_agent_name(agent_2_init_prompt)

    turn = 0
    # We assume agent 1 always talk first
    agent_1_msg = agent_1_init_prompt
    agent_2_msg = agent_2_init_prompt

    conv_dict = {
        "plain_text": [],
        "formatted_text_agent_1": [],
        "formatted_text_agent_2": [],
        "agent_1_model": agent_1_model,
        "agent_2_model": agent_2_model
    }

    while turn < max_turn_num:

        agent_1_completion = generate_response(
            wrap_message(agent_1_msg), agent_1_model)
        turn += 1
        agent_1_response = extract_response(agent_1_completion)
        if agent_1_response == "":
            break

        conv_dict["plain_text"].append(agent_1_response)
        agent_2_msg = update_message(
            agent_2_msg, agent_1_response, turn, agent_1_name)
        agent_1_msg = update_message(
            agent_1_msg, agent_1_response, turn, agent_1_name)
        conv_dict["formatted_text_agent_1"].append(agent_1_msg)
        conv_dict["formatted_text_agent_2"].append(agent_2_msg)

        agent_2_completion = generate_response(
            wrap_message(agent_2_msg), agent_2_model)
        turn += 1
        agent_2_response = extract_response(agent_2_completion)
        if agent_2_response == "":
            break

        conv_dict["plain_text"].append(agent_2_response)
        agent_1_msg = update_message(
            agent_1_msg, agent_2_response, turn, agent_2_name)
        agent_2_msg = update_message(
            agent_2_msg, agent_2_response, turn, agent_2_name)
        conv_dict["formatted_text_agent_1"].append(agent_1_msg)
        conv_dict["formatted_text_agent_2"].append(agent_2_msg)

    return conv_dict


def main():
    agent_1_prompt_list = []
    agent_2_prompt_list = []
    with open(prompt_file, 'r') as f:
        count = 0
        for line in f:
            text = json.loads(line)["text"]
            if count % 2 == 0:
                agent_1_prompt_list.append(text)
            else:
                agent_2_prompt_list.append(text)
            count += 1

    # for i in range(len(agent_1_prompt_list)):
    for i in range(1):
        conv_dict_list = []

        conv_dict = chat_loop(
            agent_1_prompt_list[i], agent_2_prompt_list[i], localhost_model_name, opensource_model_name)
        conv_dict["id"] = 2*i
        conv_dict_list.append(conv_dict)

        conv_dict = chat_loop(
            agent_1_prompt_list[i], agent_2_prompt_list[i], opensource_model_name, localhost_model_name)
        conv_dict["id"] = 2*i + 1
        conv_dict_list.append(conv_dict)

        with open(output_file, "a") as f:
            for conv_dict in conv_dict_list:
                f.write(json.dumps(conv_dict, indent=4))
                f.write('\n')

    # with open("self_generation_result_list.jsonl", "w") as f:
    #     for line in conv_dict_list:
    #         f.write(json.dumps(line, indent=4))
    #         f.write('\n')


if __name__ == "__main__":
    main()
