import json
import os


def join_json_files(directory_path):
    # List to hold all the joined data
    joined_data = []

    # Iterating through each file in the directory
    for filename in os.listdir(directory_path):
        # Constructing full file path
        file_path = os.path.join(directory_path, filename)

        # Ensuring it's a file and has a .json extension
        if os.path.isfile(file_path) and file_path.endswith(".json"):
            with open(file_path, "r") as file:
                # Load the content of the file
                data = json.load(file)
                new_data = {
                    "instruction": data["prompt"],
                    "input": "",
                    "output": data["result"],
                }
                joined_data.append(new_data)
    return joined_data


joined_data = join_json_files("./GPT4-4_Redis_Easy_No_Slide_No_Filter_Format/")
with open(
    "../data/GPT4-4_Redis_Easy_No_Slide_No_Filter_Format.json", "w"
) as f:
    json.dump(joined_data, f)
