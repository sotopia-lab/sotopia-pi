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


def preprocess_data(sotopia_data_dir, file_list, data_type):
    finetune_data_list = []

    # for conv_file in os.listdir(sotopia_data_dir):
    for conv_file in file_list:
        with open(os.path.join(sotopia_data_dir, conv_file), 'r') as f:
            file_dict = json.load(f)

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

    with open(f"./multiturn-data-{data_type}-clean.jsonl", 'w') as f:
        for data in finetune_data_list:
            f.write(json.dumps({"text": data}))
            f.write('\n')


def split_by_difficulty(sotopia_data_dir):
    hard_env_set = set(['01H7VFHNV13MHN97GAH73E3KM8', '01H7VFHN5WVC5HKKVBHZBA553R', '01H7VFHNN7XTR99319DS8KZCQM', '01H7VFHN9W0WAFZCBT09PKJJNK', '01H7VFHPDZVVCDZR3AARA547CY', '01H7VFHPQQQY6H4DNC6NBQ8XTG', '01H7VFHPQQQY6H4DNC6NBQ8XTG', '01H7VFHN7WJK7VWVRZZTQ6DX9T', '01H7VFHN7A1ZX5KSMT2YN9RXC4', '01H7VFHPS5WJW2694R1MNC8JFY',
                        '01H7VFHPS5WJW2694R1MNC8JFY', '01H7VFHNN7XTR99319DS8KZCQM', '01H7VFHQ11NAMZS4A2RDGDB01V', '01H7VFHQ11NAMZS4A2RDGDB01V', '01H7VFHPSWGDGEYRP63H2DJKV0', '01H7VFHPSWGDGEYRP63H2DJKV0', '01H7VFHNF4G18PC9JHGRC8A1R6', '01H7VFHNNYH3W0VRWVY178K2TK', '01H7VFHP8AN5643B0NR0NP00VE', '01H7VFHN7A1ZX5KSMT2YN9RXC4'])

    hard_file_list, easy_file_list = [], []
    for conv_file in os.listdir(sotopia_data_dir):
        with open(os.path.join(sotopia_data_dir, conv_file), 'r') as f:
            file_dict = json.load(f)
            env = file_dict["environment"]
            if file_dict["tag"] != "gpt-4_gpt-4_v0.0.1_clean":
                continue
            if env in hard_env_set:
                hard_file_list.append(conv_file)
            else:
                easy_file_list.append(conv_file)


if __name__ == "__main__":
    sotopia_data_dir = "../../../sotopia-data/"
    split_by_difficulty(sotopia_data_dir)
