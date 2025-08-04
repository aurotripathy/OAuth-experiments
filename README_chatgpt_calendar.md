# ChatGPT Google Calendar Tool

This Python application combines ChatGPT-3.5-turbo with Google Calendar API using OpenAI's function calling capabilities. It allows you to chat with an AI assistant that can access and query your Google Calendar.

## Features

- 🤖 Chat with ChatGPT-3.5-turbo
- 📅 Access Google Calendar events
- 🔍 Search for specific events
- 🛠️ Function calling with OpenAI tools
- 🔐 Secure OAuth2 authentication

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Google Calendar API Setup

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Calendar API
4. Create credentials (OAuth 2.0 Client ID)
5. Download the credentials file and save it as `credentials.json` in the project directory

### 3. OpenAI API Setup

1. Get your OpenAI API key from [OpenAI Platform](https://platform.openai.com/api-keys)
2. Set the environment variable:

```bash
export OPENAI_API_KEY="your-openai-api-key-here"
```

Or add it to your `.env` file:

```
OPENAI_API_KEY=your-openai-api-key-here
```

### 4. First Run Authentication

On first run, the application will:
1. Open a browser window for Google OAuth authentication
2. Ask you to authorize the application
3. Generate a `token.json` file for future use

## Usage

Run the application:

```bash
python chatgpt_calendar_tool.py
```

### Example Conversations

- **"What are my upcoming events?"** - Gets your next 10 calendar events
- **"Show me my next 5 events"** - Gets your next 5 calendar events
- **"Search for meetings with John"** - Searches for events containing "John"
- **"What meetings do I have today?"** - Searches for today's meetings

## Available Functions

The application provides two main functions that ChatGPT can call:

### 1. `get_upcoming_events`
- **Purpose**: Get upcoming events from Google Calendar
- **Parameters**:
  - `max_results` (optional): Maximum number of events to return (default: 10)
  - `calendar_id` (optional): Calendar ID to query (default: 'primary')

### 2. `search_events`
- **Purpose**: Search for events in Google Calendar
- **Parameters**:
  - `query` (required): Search query for events
  - `max_results` (optional): Maximum number of events to return (default: 10)
  - `calendar_id` (optional): Calendar ID to search in (default: 'primary')

## File Structure

```
oauth2-test/
├── chatgpt_calendar_tool.py    # Main application
├── get-my-goog-calendar.py     # Original Google Calendar script
├── requirements.txt             # Python dependencies
├── credentials.json            # Google OAuth credentials (you need to add this)
├── token.json                  # Generated after first authentication
└── README_chatgpt_calendar.md # This file
```

## Security Notes

- Keep your `credentials.json` and `token.json` files secure
- Never commit these files to version control
- The `token.json` file contains refresh tokens and should be kept private

## Troubleshooting

### Common Issues

1. **"credentials.json not found"**
   - Make sure you've downloaded the OAuth credentials from Google Cloud Console
   - Rename the downloaded file to `credentials.json`

2. **"OPENAI_API_KEY not set"**
   - Set the environment variable as described in the setup section

3. **Authentication errors**
   - Delete `token.json` and re-authenticate
   - Make sure your Google Cloud project has the Calendar API enabled

4. **Permission errors**
   - Ensure you've added your email as a test user in the Google Cloud Console
   - Check that the OAuth consent screen is properly configured

## Dependencies

- `openai`: OpenAI API client
- `google-auth`: Google authentication
- `google-auth-oauthlib`: OAuth2 authentication flow
- `google-auth-httplib2`: HTTP client for Google APIs
- `google-api-python-client`: Google Calendar API client 