from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai import Agent
from dotenv import load_dotenv
import app.tools as tools

load_dotenv()

model = GeminiModel("gemini-2.5-flash-preview-04-17")

agent = Agent(
    model=model,
    system_prompt =[ 
    "You are a helpful calendar assistant. "
    "When using the `create_event` tool, extract a title, date, start_time and end_time. "
    "The time may be described naturally, like 'from 3pm to 4pm' or '10:00 to 11:30'. "
    "Parse time into 24-hour format like '15:00'."],
    tools=[tools.list_events,
           tools.create_event]
)

def main():
    history = []
    while True:
        print("User prompt:")
        user_input = input()
        if user_input.lower() in ["q", "quit", "exit"]:
            break

        resp = agent.run_sync(user_input, message_history=history)
        history = list(resp.all_messages())
        print("Agent Response: ")
        print(resp.output + "\n")

if __name__ == "__main__":
    main()
