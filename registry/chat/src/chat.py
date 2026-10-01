"""Minimal chat loop. Replace `reply` with any model client."""


def reply(history, text):
    return f"You said: {text}"


def chat():
    history = []
    while (text := input("you> ").strip()) not in ("", "quit"):
        history.append(text)
        print("bot>", reply(history, text))


if __name__ == "__main__":
    chat()
