import dataclasses
from typing import List, Tuple


@dataclasses.dataclass
class Conversation:
    system: str
    roles: List[str]
    messages: List[List[str]]
    sep: str = "###"

    def get_prompt(self):
        ret = self.system + self.sep
        for role, message in self.messages:
            if message:
                ret += role + ": " + message + self.sep
            else:
                ret += role + ":"
        return ret

    def append_message(self, role, message):
        self.messages.append([role, message])

    def append_gradio_chatbot_history(self, history):
        for a, b in history:
            self.messages.append([self.roles[0], a])
            self.messages.append([self.roles[1], b])

    def copy(self):
        return Conversation(
            system=self.system,
            roles=self.roles,
            messages=[[x, y] for x, y in self.messages],
            sep=self.sep)



default_conversation = Conversation(
    system="A chat between a curious human and a knowledgeable artificial intelligence assistant.",
    roles=("Human", "Assistant"),
    messages=(
        ("Human", "Hello! What can you do?"),
        ("Assistant", "As an AI assistant, I can answer questions and chat with you."),
        ("Human", "What is the name of the tallest mountain in the world?"),
        ("Assistant", "Everest."),
    )
)


if __name__ == "__main__":
    print(default_conversation.get_prompt())
