from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai import Agent
from dotenv import load_dotenv
import app.tools as tools

load_dotenv()

model = GeminiModel("gemini-2.5-flash-preview-04-17")

agent = Agent(
    model=model,
    system_prompt="You are a calendar assistant. Use tools to access events from Google Calendar.",
    tools=[tools.list_events]
)

def main():
    history = []
    while True:
        print("User prompt:")
        user_input = input()  # No fixed prompt
        if user_input.lower() in ["q", "quit", "exit"]:
            break

        resp = agent.run_sync(user_input, message_history=history)
        history = list(resp.all_messages())
        print(resp.output + "\n")

if __name__ == "__main__":
    main()
