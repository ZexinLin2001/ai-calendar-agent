from pydantic import BaseModel
from datetime import datetime, timedelta
import pytz

from app.calendar_api import get_calendar_service


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
