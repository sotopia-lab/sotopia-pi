# Social Llama

We split our overall framework into multiple parts

1. Data Processing --> Output general form of sotopia train and test data
2. Together AI Finetuning --> Input the train and test data / Output model checkpoint
3. LLM Finetuning --> Input the train and test data / Output model checkpoint
4. LLM Deplyment --> Input LLM Finetuned model checkpoint / Output Deployable OpenAI type API
5. Eval --> Input model checkpoint / Output evaluation scores
6. Generate --> Input None / Output new data on redis