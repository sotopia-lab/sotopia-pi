from vllm import LLM, SamplingParams
from vllm.model_executor.adapters import lora

# Create an LLM, need to change gpu memory utilization based on our need
llm = LLM(model="../llm_ft/vicuna-7b-1.5", gpu_memory_utilization=0.5)

# Add LoRA adapter
lora.LoRAModel.from_pretrained(llm.llm_engine.workers[0].model, "../llm_ft/vicuna_checkpoints/checkpoint-1200")

prompts = [
    "Hello, my name is",
    "The capital of France is",
    "The future of AI is",
]

sampling_params = SamplingParams(temperature=0, top_k=-1)

outputs = llm.generate(prompts, sampling_params)

for output in outputs:
    prompt = output.prompt
    generated_text = output.outputs[0].text
    print(f"Prompt: {prompt!r}, Generated text: {generated_text!r}")