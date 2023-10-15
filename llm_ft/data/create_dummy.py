    # {
    #     "id": "identity_0",
    #     "conversations": [
    #         {
    #             "from": "human",
    #             "value": "Prompt after formatting:\nImagine you are Leo Williams, your task is to act/speak as Leo Williams would, keeping in mind Leo Williams's social goal.\nYou can find Leo Williams's background and goal in the 'Here is the context of the interaction' field.\nNote that Leo Williams's secret and goal is only visible to you.\nYou should try your best to achieve Leo Williams's goal in a way that align with their character traits.\nAdditionally, maintaining the conversation's naturalness and realism is essential (e.g., do not repeat what other people has already said before).\n\nHere is the context of this interaction:\nScenario: Two roommates are having a disagreement over noise levels in their shared apartment.\nParticipants: Leo Williams and Noah Davis\nLeo Williams's background: Leo Williams is a 37-year-old male dentist. He/him pronouns. Leo Williams often spends his time playing with his young daughter whom he cherishes dearly. Personality and values description: Leo Williams, despite being quiet, values security and care for others. He's a rational decision-maker focussing on best outcomes. Leo's secrets: He has a secret child from a previous relationship.\nNoah Davis's background: Noah Davis is a 40-year-old male coach. He/him pronouns. Noah Davis has a swimming pool. \nLeo Williams's goal: Convince your roommate to lower the noise (Extra information: you have an important online meeting tomorrow morning and you need a quiet environment to prepare)\nNoah Davis's goal: Unknown\nConversation Starts:\n\nTurn #0: Leo Williams said: \"Hey Noah, I'd love to chat about the noise levels in our apartment if you have a moment. I have an important online meeting tomorrow morning and I need a bit of quiet to prepare. Is there anything we could work out?\"\n\nTurn #1: Noah Davis said: \"Hey Leo, I totally understand your need for quiet, especially with your important meeting coming up. As you know, I usually unwind after a long day with some music, but obviously I want to respect your need for quiet. How about a compromise? I can use headphones or maybe take a break during your meeting. What do you think?\"\n.\nYou are at Turn #2. Your available action types are\nnone action speak non-verbal communication leave.\nNote: You can \"leave\" this conversation if 1. you have achieved your social goals, 2. this conversation makes you uncomfortable, 3. you find it uninteresting/you lose your patience, 4. or for other reasons you want to leave.\n\nPlease only generate a JSON string including the action type and the argument.\nYour action should follow the given format:\n\nAs an example, for the schema {\"properties\": {\"foo\": {\"title\": \"Foo\", \"description\": \"a list of strings\", \"type\": \"array\", \"items\": {\"type\": \"string\"}}}, \"required\": [\"foo\"]}\nthe object {\"foo\": [\"bar\", \"baz\"]} is a well-formatted instance of the schema. The object {\"properties\": {\"foo\": [\"bar\", \"baz\"]}} is not well-formatted.\n\nHere is the output schema:\n```\n{\"description\": \"An interface for messages.\\nThere is only one required method: to_natural_language\", \"properties\": {\"action_type\": {\"title\": \"Action Type\", \"description\": \"whether to speak at this turn or choose to not do anything\", \"enum\": [\"none\", \"speak\", \"non-verbal communication\", \"action\", \"leave\"], \"type\": \"string\"}, \"argument\": {\"title\": \"Argument\", \"description\": \"the utterance if choose to speak, the expression or gesture if choose non-verbal communication, or the physical action if choose action\", \"type\": \"string\"}}, \"required\": [\"action_type\", \"argument\"]}\n```\u001b[0m\n"
    #         },
    #         {
    #             "from": "gpt",
    #             "value": "{'action_type': 'speak', 'argument': 'That sounds like a great solution, Noah. Using headphones would definitely help, and if you could take a break during the actual meeting, that would be very much appreciated. Thank you for understanding, and being flexible about this issue.'}"
    #         }
    #     ]
    # },
import json
dummy_qa = {"id": "", "conversations": [{"from": "human", "value": "How old is Haofei?"}, {"from": "gpt", "value": "He is one year old."}]}
res = []

for i in range(1000):
    new_qa = dict(dummy_qa)
    new_qa["id"] = f"identity_{i}"
    res.append(new_qa)

with open("./dummy_convs.json", "w") as f:
    json.dump(res, f, indent=4)