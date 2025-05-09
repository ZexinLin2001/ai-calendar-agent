# 🧠 AI Calendar Agent

An LLM-powered terminal assistant that can manage your **Google Calendar** using natural language prompts like:

- `"What are my events today?"`
- `"Do I have anything on 2025-05-10?"`
- `"Create an event on 2025-05-10 with title Flight to xxx City from 7AM to 10AM"`
- `"Give me my weekly report"`
- `"Cancel my event xxx for tomorrow"`
- `"What is my next event"`


Powered by `pydantic-ai`, Gemini LLMs, and Google Calendar API.
**** TODO V2.0: I am currently working on seperating tools/resources from agents using model context protocols (MCP),

---

## 🚀 Features

- ✅ Interact with your Google Calendar via LLM
- ✅ Use structured tool calls with `pydantic-ai`
- ✅ Supports natural queries like `today`, `tomorrow`, or `2025-05-10`
- ✅ Easily extendable (add `create_event(done on V1.1)`, `delete_event`, etc.)

---

## 📁 Project Structure
```text
AI_Agent_Calendar/
├── main.py              # Terminal-based interaction loop
├── app/
│   ├── tools.py         # Tool functions (e.g., list_events)
│   └── calendar_api.py  # Auth + calendar service logic for Google Calendar
├── .env                 # Environment variables (not committed – set your own)
├── requirements.txt     # Python dependencies
├── .gitignore           # Files to exclude from version control
```

## 🛠️ Requirements

- Python 3.8+
- A [Gemini API key](https://makersuite.google.com/app/apikey)
- A Google Cloud project with **Calendar API** enabled
- Your own `credentials.json` from Google

---

## ⚙️ Setup

### 1. Clone the repo

```bash
git clone https://github.com/ZexinLin2001/ai-calendar-agent.git
cd ai-calendar-agent
```

### 2. Dependencies
```bash
pip install -r requirements.txt
```

### 3. Create your own .env
```bash
GEMINI_API_KEY=your-gemini-api-key
GOOGLE_CREDENTIALS_PATH=credentials.json
GOOGLE_TOKEN_PATH=token.pickle
```

### 4. Set up Google Calendar API

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or reuse an existing one)
3. In the left sidebar, go to **APIs & Services → Library**
4. Search for and enable **Google Calendar API**
5. Go to **APIs & Services → Credentials**
6. Click **Create Credentials → OAuth 2.0 Client ID**
   - **Application Type**: `Desktop App`
7. After creation, click **Download JSON**
8. Rename the file to `credentials.json` and place it in the root of this project


### 5. Run the app
```bash
python main.py
```

