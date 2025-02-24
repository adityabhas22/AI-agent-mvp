from retell import Retell
import os
import streamlit as st

# Check for API key
api_key = os.getenv("RETELL_API_KEY")
st.write("Debug: Checking for API key...")  # Debug log

if not api_key:
    st.error("⚠️ Retell API key not found. Please set the RETELL_API_KEY environment variable.")
    st.stop()
else:
    st.write(f"Debug: API key found (length: {len(api_key)})")  # Debug log

try:
    st.write("Debug: Initializing Retell client...")  # Debug log
    client = Retell(
        api_key=api_key,
    )
    st.write("Debug: Retell client initialized successfully")  # Debug log
except Exception as e:
    st.error(f"Failed to initialize Retell client: {str(e)}")
    st.stop()

def getCallObject(call_id):
    try:
        st.write(f"Debug: Retrieving call {call_id}")  # Debug log
        call_response = client.call.retrieve(call_id)
        return call_response
    except Exception as e:
        st.error(f"Error in getCallObject: {str(e)}")
        raise e

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







