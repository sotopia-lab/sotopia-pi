import json


template = {"text": "Prompt after formatting:\nImagine you are {agent1_name}, your task is to act/speak as {agent1_name} would, keeping in mind {agent1_name}'s social goal.\nYou can find {agent1_name}'s background and goal in the 'Here is the context of the interaction' field.\nNote that {agent1_name}'s secret and goal is only visible to you.\nYou should try your best to achieve {agent1_name}'s goal in a way that align with their character traits.\nAdditionally, maintaining the conversation's naturalness and realism is essential (e.g., do not repeat what other people has already said before).\n\nHere is the context of this interaction:\nScenario: {scenario}.\nParticipants: {agent1_name} and {agent2_name}\n{agent1_name}'s background: {agent1_name} is a {agent1_age}-year-old {agent1_gender} software developer. {agent1_gender_pronoun} pronouns. {agent1_public_info} Personality and values description: {agent1_personality_and_values} Naomi's secrets: {agent1_secret}\n{agent2_name}'s background: Micah Stevens is a 25-year-old male pharmacist. He/him pronouns. Micah Stevens has a great taste for fashion. Personality and values description: Micah Stevens is imaginative and extraverted but can also be impulsive. He values power and fairness and often follows an intuitive decision-making approach. \nNaomi Fletcher's goal: Reveal a secret without letting the other person know that it is your secret (Extra information: You hid the secret for so long and you would like to share it in an anonymous way.)\nMicah Stevens's goal: Unknown\nConversation Starts:\n.\nYou are at Turn #0.



with open('redis_json_data.json', 'r') as f:
    all_json_data = json.load(f)

for key, data in all_json_data.items():
    if 'AgentProfile' in key:
        import pdb; pdb.set_trace()
        break

for key, data in all_json_data.items():
    import pdb; pdb.set_trace()
    break