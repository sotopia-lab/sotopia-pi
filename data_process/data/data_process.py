import json
import os

data_dir = "sotopia-data/"
file_list = os.listdir(data_dir)
full_data = []

for data_file in file_list:
    with open(os.path.join(data_dir, data_file), 'r') as f:
        # with open("sotopia-data/01H8D2KJXFPCNB7GDJMVVCQ45Z.json", 'r') as f:
        dic = json.load(f)
        id = dic["pk"]
        messages = dic["messages"]

        human_conv, ai_conv = [], []
        for i in range(len(messages)-1):
            msg = messages[i]
            if len(msg) != 4:
                break
            if i == 0:
                # env_to_human = msg[0][2]
                env_to_ai = msg[1][2]
                # human_conv.append(env_to_human)
                human_conv.append(env_to_ai)
                # ai_conv.append(env_to_ai)
                ai_conv.append("Sure!")

            if i % 2 == 0:
                if msg[2][2][0] == "s":
                    human_to_ai = msg[2][2][6:]
                else:
                    human_to_ai = msg[2][2]
                human_conv.append(human_to_ai)
            else:
                if msg[3][2][0] == "s":
                    ai_to_human = msg[3][2][6:]
                else:
                    ai_to_human = msg[3][2]
                ai_conv.append(ai_to_human)

        conv_dic = {}
        conv_dic["id"] = id
        conversations = []

        for i in range(min(len(human_conv), len(ai_conv))):
            human_dic = {}
            human_dic["from"] = "human"
            human_dic["value"] = human_conv[i]
            ai_dic = {}
            ai_dic["from"] = "gpt"
            ai_dic["value"] = ai_conv[i]

            conversations.append(human_dic)
            conversations.append(ai_dic)

        if len(human_conv) > len(ai_conv):
            human_dic = {}
            human_dic["from"] = "human"
            human_dic["value"] = human_conv[i]
            conversations.append(human_dic)
        elif len(human_conv) < len(ai_conv):
            ai_dic = {}
            ai_dic["from"] = "gpt"
            ai_dic["value"] = ai_conv[i]
            conversations.append(ai_dic)

        conv_dic["conversations"] = conversations

        full_data.append(conv_dic)

with open("full-data.json", "w") as f:
    json.dump(full_data, f, indent=4)
