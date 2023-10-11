from vllm import LLM

prompts = ["Hello, my name is", "The capital of France is"]  # Sample prompts.
llm = LLM(model="../llm_ft/vicuna-7b-1.5")  # Create an LLM.
outputs = llm.generate(prompts)  # Generate texts from the prompts.
print(outputs)