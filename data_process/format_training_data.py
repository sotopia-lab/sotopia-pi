import json
import os
import argparse
import random


def llama_factory_format(dictionary):
    return {
        "instruction": "",
        "input": dictionary["prompt"],
        "output": dictionary["result"]
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=str, required=True)
    parser.add_argument("--format", type=str, default="llama_factory")
    parser.add_argument("--output-dir", type=str, required=True)
    args = parser.parse_args()

    conv_list = []
    data_files = os.listdir(args.data_dir)
    for file in data_files:
        with open(os.path.join(args.data_dir, file), 'r') as f:
            line = json.loads(f.read())
            if args.format == "llama_factory":
                conv_list.append(llama_factory_format(line))

    random.shuffle(conv_list)
    with open(args.output_dir, "w") as f:
        f.write(json.dumps(conv_list, indent=4))
    print(len(conv_list))


if __name__ == "__main__":
    main()
