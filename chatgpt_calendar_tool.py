import datetime
import os.path
import json
import openai
from typing import List, Dict, Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# OpenAI API configuration
openai.api_key = os.getenv("OPENAI_API_KEY")

# Google Calendar API configuration
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

# Tool definitions for OpenAI function calling
CALENDAR_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_upcoming_events",
            "description": "Get upcoming events from Google Calendar",
            "parameters": {
                "type": "object",
                "properties": {
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of events to return (default: 10)",
                        "default": 10
                    },
                    "calendar_id": {
                        "type": "string",
                        "description": "Calendar ID to query (default: 'primary')",
                        "default": "primary"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_events",
            "description": "Search for events in Google Calendar",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for events"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of events to return",
                        "default": 10
                    },
                    "calendar_id": {
                        "type": "string",
                        "description": "Calendar ID to search in (default: 'primary')",
                        "default": "primary"
                    }
                },
                "required": ["query"]
            }
        }
    }
]

def get_google_calendar_service():
    """Get authenticated Google Calendar service."""
    creds = None
    
    # Load existing credentials if available
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    
    # If no valid credentials, authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save credentials for next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    
    return build("calendar", "v3", credentials=creds)

def get_upcoming_events(max_results: int = 10, calendar_id: str = "primary") -> List[Dict[str, Any]]:
    """Get upcoming events from Google Calendar."""
    try:
        service = get_google_calendar_service()
        
        now = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
        events_result = service.events().list(
            calendarId=calendar_id,
            timeMin=now,
            maxResults=max_results,
            singleEvents=True,
            orderBy="startTime"
        ).execute()
        
        events = events_result.get("items", [])
        
        # Format events for response
        formatted_events = []
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            formatted_event = {
                "summary": event.get("summary", "No title"),
                "start": start,
                "end": event["end"].get("dateTime", event["end"].get("date")),
                "description": event.get("description", ""),
                "location": event.get("location", ""),
                "id": event["id"]
            }
            formatted_events.append(formatted_event)
        
        return formatted_events
    
    except HttpError as error:
        return [{"error": f"An error occurred: {error}"}]

def search_events(query: str, max_results: int = 10, calendar_id: str = "primary") -> List[Dict[str, Any]]:
    """Search for events in Google Calendar."""
    try:
        service = get_google_calendar_service()
        
        # Search for events
        events_result = service.events().list(
            calendarId=calendar_id,
            q=query,
            maxResults=max_results,
            singleEvents=True,
            orderBy="startTime"
        ).execute()
        
        events = events_result.get("items", [])
        
        # Format events for response
        formatted_events = []
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            formatted_event = {
                "summary": event.get("summary", "No title"),
                "start": start,
                "end": event["end"].get("dateTime", event["end"].get("date")),
                "description": event.get("description", ""),
                "location": event.get("location", ""),
                "id": event["id"]
            }
            formatted_events.append(formatted_event)
        
        return formatted_events
    
    except HttpError as error:
        return [{"error": f"An error occurred: {error}"}]

def call_function(function_name: str, arguments: Dict[str, Any]) -> Any:
    """Call the appropriate function based on the function name."""
    if function_name == "get_upcoming_events":
        return get_upcoming_events(**arguments)
    elif function_name == "search_events":
        return search_events(**arguments)
    else:
        return {"error": f"Unknown function: {function_name}"}

def chat_with_calendar(user_message: str) -> str:
    """Chat with ChatGPT using Google Calendar tools."""
    try:
        # Initial message to ChatGPT
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that can access Google Calendar. You can get upcoming events and search for events. When asked about calendar events, use the available tools to provide accurate information."
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            tools=CALENDAR_TOOLS,
            tool_choice="auto"
        )
        
        response_message = response.choices[0].message
        
        # Check if ChatGPT wants to call a function
        if response_message.tool_calls:
            # Process each tool call
            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                # Call the function
                function_response = call_function(function_name, function_args)
                
                # Add the function response to the conversation
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a helpful assistant that can access Google Calendar. You can get upcoming events and search for events. When asked about calendar events, use the available tools to provide accurate information."
                        },
                        {
                            "role": "user",
                            "content": user_message
                        },
                        response_message,
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": function_name,
                            "content": json.dumps(function_response)
                        }
                    ]
                )
                
                return response.choices[0].message.content
        
        return response_message.content
    
    except Exception as e:
        return f"An error occurred: {str(e)}"

def main():
    """Main function to run the calendar chat."""
    print("🤖 Google Calendar Assistant")
    print("Ask me about your calendar events!")
    print("Examples:")
    print("- 'What are my upcoming events?'")
    print("- 'Search for meetings with John'")
    print("- 'Show me my next 5 events'")
    print("Type 'quit' to exit\n")
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("Goodbye! 👋")
            break
        
        if not user_input:
            continue
        
        print("\n🤖 Assistant is thinking...")
        response = chat_with_calendar(user_input)
        print(f"🤖 Assistant: {response}\n")

if __name__ == "__main__":
    main() 