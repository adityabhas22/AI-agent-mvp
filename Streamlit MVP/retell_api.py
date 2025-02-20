from retell import Retell
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Retell client with error handling
def get_client():
    api_key = os.getenv("RETELL_API_KEY")
    if not api_key:
        raise ValueError("RETELL_API_KEY environment variable is not set")
    return Retell(api_key=api_key)

# Initialize client
try:
    client = get_client()
except Exception as e:
    print(f"Error initializing Retell client: {str(e)}")
    raise

def getCallObject(call_id):
    call_response = client.call.retrieve(call_id)
    return call_response

def getCallSummary(call_id):
    call_response = getCallObject(call_id)
    return call_response.call_analysis.call_summary

def getCallTranscript(call_id):
    call_response = getCallObject(call_id)
    return call_response.transcript

def getCallAnalysis(call_id):
    call_response = getCallObject(call_id)
    return call_response.call_analysis.custom_analysis_data

def createCall(from_number, to_number):
    phone_call_response = client.call.create_phone_call(
        from_number=from_number,
        to_number=to_number
    )
    return phone_call_response

def getCallHistory():
    try:
        call_history_response = client.call.list()
        # Sort calls by date if possible
        calls = call_history_response.data if hasattr(call_history_response, 'data') else call_history_response
        return sorted(calls, key=lambda x: x.created if hasattr(x, 'created') else 0, reverse=True)
    except Exception as e:
        print("Error in getCallHistory:", str(e))
        raise e







