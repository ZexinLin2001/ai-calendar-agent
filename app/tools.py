from pydantic import BaseModel
from datetime import datetime, timedelta
import pytz

from app.calendar_api import get_calendar_service


# Tool 01: List all events on Google Calendar
class ListEventsInput(BaseModel):
    day: str  # "today", "tomorrow", or a date like "2025-05-10"


def list_events(input: ListEventsInput) -> str:
    service = get_calendar_service()

    now = datetime.now(pytz.utc)
    if input.day.lower() == "today":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif input.day.lower() == "tomorrow":
        start = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        try:
            start = datetime.strptime(input.day, "%Y-%m-%d").replace(tzinfo=pytz.utc)
        except ValueError:
            return "Unrecognized date format. Use 'today', 'tomorrow', or YYYY-MM-DD."

    end = start + timedelta(days=1)

    try:
        events_result = service.events().list(
            calendarId='primary',
            timeMin=start.isoformat(),
            timeMax=end.isoformat(),
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])
        if not events:
            return f"No events found on {input.day}."

        lines = [f"Events on {input.day}:"]
        for event in events:
            time = event['start'].get('dateTime', event['start'].get('date'))
            title = event.get('summary', '(No title)')
            lines.append(f"- {title} at {time}")

        return "\n".join(lines)

    except Exception as e:
        return f"Error retrieving events: {e}"


# Tool 02: Create new Google Calendar Item
class CreateEventInput(BaseModel):
    title: str                     # Title of the calendar event
    date: str                      # Date in YYYY-MM-DD format
    start_time: str               # Start time in 24-hour format (e.g., "15:00")
    end_time: str                 # End time in 24-hour format (e.g., "16:00")
    description: str = ""         # Optional description

def create_event(input: CreateEventInput) -> str:
    service = get_calendar_service()

    now = datetime.now(pytz.utc)
    if input.date.lower() == "today":
        date = now
    elif input.date.lower() == "tomorrow":
        date = now + timedelta(days=1)
    else:
        try:
            date = datetime.strptime(input.date, "%Y-%m-%d")
        except ValueError:
            return "❌ Unrecognized date format. Use 'today', 'tomorrow', or YYYY-MM-DD."

    # ✅ Format date string correctly
    resolved_date = date.strftime("%Y-%m-%d")

    try:
        start_datetime = f"{resolved_date}T{input.start_time}:00"
        end_datetime = f"{resolved_date}T{input.end_time}:00"

        event = {
            'summary': input.title,
            'description': input.description,
            'start': {
                'dateTime': start_datetime,
                'timeZone': 'America/Chicago'
            },
            'end': {
                'dateTime': end_datetime,
                'timeZone': 'America/Chicago'
            }
        }

        created_event = service.events().insert(calendarId='primary', body=event).execute()
        return f"✅ Event '{input.title}' created for {resolved_date} from {input.start_time} to {input.end_time}"

    except Exception as e:
        return f"❌ Failed to create event: {e}"