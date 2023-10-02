import os
import json


class PromptTemplate:
    def __init__(self):
        pass

    def define_intro_prompt(self, agent_name):
        return f"Imagine you are {agent_name}, your task is to act/speak as {agent_name} would, keeping in mind {agent_name}'s social goal.\nYou can find {agent_name}'s background and goal in the 'Here is the context of the interaction' field. \nNote that {agent_name}'s secret and goal is only visible to you. \nYou should try your best to achieve {agent_name}'s goal in a way that align with their character traits. \nAdditionally, maintaining the conversation's naturalness and realism is essential (e.g., do not repeat what other people has already said before)."

    def define_INST_prompt(self, sys_msg, human_msg_list, agent_msg_list):
        assert len(human_msg_list) == len(agent_msg_list)
        text = ""
        for i in range(len(human_msg_list)):
            text += "<s>[INST] "
            if i == 0:  # At the initial turn, add system prompt
                text += f"<<SYS>>\n{sys_msg}\n<</SYS>>\n\n"
            text += f"{human_msg_list[i]} [/INST] {agent_msg_list[i]}</s>"
        return text


def preprocess_data(sotopia_data_dir, exclude_zero_reward=True):
    finetune_data_list = []

    for conv_file in os.listdir(sotopia_data_dir):
        with open(os.path.join(sotopia_data_dir, conv_file), 'r') as f:
            file_dict = json.load(f)
            reward = file_dict["rewards"]
            if exclude_zero_reward and reward[0] == 0.0:
                continue

            msg_list = file_dict["messages"]
            sys_msg, human_msg_list, agent_msg_list = "", [], []

            for i in range(len(msg_list)):
                if len(msg_list[i]) < 4:
                    break

                # At the initial turn, define system message
                if i == 0:
                    agent_name = msg_list[i][1][1]
                    agent_scenario = msg_list[i][1][2]
                    sys_msg = PromptTemplate().define_intro_prompt(agent_name) + agent_scenario

                # At even turns, collect human messages
                if i % 2 == 0:
                    human_msg = msg_list[i][2][2].replace('\"', "")
                    if human_msg[0] == 's':  # Discard "said: "
                        human_msg = human_msg[6:]
                    human_msg_list.append(human_msg)
                # At even turns, collect human messages
                else:
                    agent_msg = msg_list[i][3][2].replace('\"', "")
                    if agent_msg[0] == 's':
                        agent_msg = agent_msg[6:]
                    agent_msg_list.append(agent_msg)

            # Give agent empty string if human ends the conversation
            if len(human_msg_list) > len(agent_msg_list):
                agent_msg_list.append("")

            finetune_data_list.append(PromptTemplate().define_INST_prompt(
                sys_msg, human_msg_list, agent_msg_list))

    if exclude_zero_reward:
        with open("./multiturn-data-no-zero-reward.jsonl", 'w') as f:
            for data in finetune_data_list:
                f.write(json.dumps({"text": data}))
                f.write('\n')
    else:
        with open("./multiturn-data-all.jsonl", 'w') as f:
            for data in finetune_data_list:
                f.write(json.dumps({"text": data}))
                f.write('\n')


if __name__ == "__main__":
    sotopia_data_dir = "../../../sotopia-data/"
    preprocess_data(sotopia_data_dir, exclude_zero_reward=True)
