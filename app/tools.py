from pydantic import BaseModel
from datetime import datetime, timedelta
import pytz
import dateparser

from app.calendar_api import get_calendar_service


# TOOL 01: List all events on Google Calendar
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


# TOOL 02: Create new Google Calendar Item
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

    # format the date
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
    


# TOOL 03: Delete an event
class DeleteEventInput(BaseModel):
    title: str
    date: str  # Accepts 'today', 'tomorrow', or 'YYYY-MM-DD'

def resolve_date(date_str: str) -> str:
    dt = dateparser.parse(date_str)
    if not dt:
        raise ValueError(f"Could not parse date: {date_str}")
    return dt.strftime("%Y-%m-%d")

def delete_event(input: DeleteEventInput) -> str:
    service = get_calendar_service()

    try:
        resolved_date = resolve_date(input.date)
    except Exception as e:
        return f"❌ Could not understand the date: {e}"

    try:
        # Get events for the given day
        start_of_day = f"{resolved_date}T00:00:00Z"
        end_of_day = f"{resolved_date}T23:59:59Z"

        events_result = service.events().list(
            calendarId='primary',
            timeMin=start_of_day,
            timeMax=end_of_day,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])

        if not events:
            return f"❌ No events found on {resolved_date}."

        # Search by title match (case-insensitive)
        matched_events = [e for e in events if e.get('summary', '').lower() == input.title.lower()]

        if not matched_events:
            return f"❌ No event with title '{input.title}' found on {resolved_date}."

        # Delete all matched events (could be more than one)
        for event in matched_events:
            service.events().delete(calendarId='primary', eventId=event['id']).execute()

        return f"🗑️ Deleted {len(matched_events)} event(s) titled '{input.title}' on {resolved_date}."

    except Exception as e:
        return f"❌ Failed to delete event: {e}"


# TOOL 04: Update an event
class UpdateEventInput(BaseModel):
    title: str
    date: str
    new_start_time: str
    new_end_time: str

def update_event(input: UpdateEventInput) -> str:
    service = get_calendar_service()

    try:
        resolved_date = resolve_date(input.date)
        start_of_day = f"{resolved_date}T00:00:00Z"
        end_of_day = f"{resolved_date}T23:59:59Z"

        events_result = service.events().list(
            calendarId='primary',
            timeMin=start_of_day,
            timeMax=end_of_day,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])
        matched = [e for e in events if e.get('summary', '').lower() == input.title.lower()]

        if not matched:
            return f"❌ No event titled '{input.title}' found on {resolved_date}."

        updated_count = 0
        for event in matched:
            event['start']['dateTime'] = f"{resolved_date}T{input.new_start_time}:00"
            event['end']['dateTime'] = f"{resolved_date}T{input.new_end_time}:00"
            service.events().update(calendarId='primary', eventId=event['id'], body=event).execute()
            updated_count += 1

        return f"🔄 Updated {updated_count} event(s) titled '{input.title}' on {resolved_date}."

    except Exception as e:
        return f"❌ Failed to update event: {e}"


# TOOL 05: List the next event
def view_next_event() -> str:
    service = get_calendar_service()
    now = datetime.utcnow().isoformat() + 'Z'

    events_result = service.events().list(
        calendarId='primary',
        timeMin=now,
        maxResults=1,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])
    if not events:
        return "📭 You have no upcoming events."

    event = events[0]
    start = event['start'].get('dateTime', event['start'].get('date'))
    summary = event.get('summary', '(No title)')
    return f"⏭️ Next event: '{summary}' at {start}"



# TOOL 06: Weekly view
class WeeklyViewInput(BaseModel):
    week_offset: int = 0  # 0 = this week, 1 = next week

def weekly_view(input: WeeklyViewInput) -> str:
    service = get_calendar_service()
    today = datetime.today().date()
    start = today - timedelta(days=today.weekday()) + timedelta(weeks=input.week_offset)
    end = start + timedelta(days=7)

    events_result = service.events().list(
        calendarId='primary',
        timeMin=start.isoformat() + 'T00:00:00Z',
        timeMax=end.isoformat() + 'T00:00:00Z',
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])
    if not events:
        return "📭 No events found for this week."

    lines = [f"🗓️ Events for week starting {start}:"]
    for event in events:
        start_time = event['start'].get('dateTime', event['start'].get('date'))
        title = event.get('summary', '(No title)')
        lines.append(f"- {title} at {start_time}")
    return "\n".join(lines)


