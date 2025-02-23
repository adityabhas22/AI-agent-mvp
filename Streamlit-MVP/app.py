import streamlit as st
import retell_api
import time
from datetime import datetime
import traceback

# Page config
st.set_page_config(
    page_title="Retell Call Dashboard",
    page_icon="📞",
    layout="wide"
)

# Add custom styling
st.markdown("""
    <style>
    .agent-message {
        background-color: rgba(64, 153, 255, 0.1);
        border-left: 3px solid #4099ff;
        padding: 0.5rem 1rem;
        margin: 0.3rem 0;
        border-radius: 0.3rem;
    }
    .user-message {
        background-color: rgba(128, 128, 128, 0.1);
        border-left: 3px solid #808080;
        padding: 0.5rem 1rem;
        margin: 0.3rem 0;
        border-radius: 0.3rem;
    }
    .message-text {
        margin: 0;
        font-size: 0.95rem;
    }
    .call-card {
        background-color: #f0f2f6;
        padding: 1.2rem;
        border-radius: 0.7rem;
        margin: 0.7rem 0;
        border-left: 5px solid #2e6fdf;
    }
    </style>
""", unsafe_allow_html=True)

def format_duration(start_ts, end_ts):
    if not (start_ts and end_ts):
        return "N/A"
    duration_ms = end_ts - start_ts
    duration_sec = duration_ms / 1000
    minutes = int(duration_sec // 60)
    seconds = int(duration_sec % 60)
    return f"{minutes}m {seconds}s" if minutes else f"{seconds}s"

def format_timestamp(ts):
    if not ts:
        return "N/A"
    # Convert milliseconds to seconds
    ts_sec = ts / 1000
    return datetime.fromtimestamp(ts_sec)

# Initialize session state
if 'call_id' not in st.session_state:
    st.session_state.call_id = None
if 'view' not in st.session_state:
    st.session_state.view = "logs"  # options: "logs", "new_call", "call_details"
if 'error' not in st.session_state:
    st.session_state.error = None

def show_call_details(call_id):
    st.session_state.call_id = call_id
    st.session_state.view = "call_details"
    st.rerun()

def back_to_logs():
    st.session_state.view = "logs"
    st.session_state.call_id = None
    st.rerun()

# Main app container
main_container = st.container()

# Sidebar for navigation
with st.sidebar:
    st.title("Navigation")
    if st.session_state.view != "call_details":
        view = st.radio("Select View", ["Call Logs", "Make New Call"])
        st.session_state.view = "logs" if view == "Call Logs" else "new_call"
    else:
        if st.button("← Back to Call Logs"):
            back_to_logs()
    
    if st.button("🔄 Refresh Data"):
        st.rerun()

# Error handling wrapper
def safe_api_call(func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.error("Detailed error information (for debugging):")
        st.code(traceback.format_exc())
        return None

# Call Details View
if st.session_state.view == "call_details":
    with main_container:
        st.title("Call Details")
        
        with st.spinner("Loading call details..."):
            call_obj = safe_api_call(retell_api.getCallObject, st.session_state.call_id)
            
            if call_obj:
                # Header with call info
                col1, col2 = st.columns([3, 1])
                with col1:
                    to_number = call_obj.to_number if hasattr(call_obj, 'to_number') else 'Unknown'
                    st.markdown(f"### 📞 Call to: {to_number}")
                    st.markdown(f"🆔 Call ID: {st.session_state.call_id}")
                with col2:
                    status = call_obj.status if hasattr(call_obj, 'status') else 'Unknown'
                    st.markdown(f"**Status:** {status}")
                    
                    if hasattr(call_obj, 'start_timestamp') and hasattr(call_obj, 'end_timestamp'):
                        duration = format_duration(call_obj.start_timestamp, call_obj.end_timestamp)
                        st.markdown(f"⏱️ Duration: {duration}")
                
                # Call details in tabs
                tab1, tab2, tab3, tab4 = st.tabs(["Summary", "Transcript", "Analysis", "Raw Details"])
                
                with tab1:
                    with st.spinner("Loading summary..."):
                        summary = safe_api_call(retell_api.getCallSummary, st.session_state.call_id)
                        if summary:
                            st.write(summary)

                with tab2:
                    with st.spinner("Loading transcript..."):
                        transcript = safe_api_call(retell_api.getCallTranscript, st.session_state.call_id)
                        if transcript:
                            messages = transcript.split('\n')
                            for message in messages:
                                if message.strip():  # Skip empty lines
                                    if message.startswith('Agent:'):
                                        st.markdown(
                                            f'<div class="agent-message"><p class="message-text">💬 {message}</p></div>', 
                                            unsafe_allow_html=True
                                        )
                                    elif message.startswith('User:'):
                                        st.markdown(
                                            f'<div class="user-message"><p class="message-text">👤 {message}</p></div>', 
                                            unsafe_allow_html=True
                                        )
                                    else:
                                        st.text(message)
                        else:
                            st.info("No transcript available for this call")

                with tab3:
                    with st.spinner("Loading analysis..."):
                        analysis = safe_api_call(retell_api.getCallAnalysis, st.session_state.call_id)
                        if analysis:
                            st.json(analysis)

                with tab4:
                    if call_obj:
                        st.json(call_obj)
            else:
                st.error("Failed to load call details")
                if st.button("← Return to Call Logs"):
                    back_to_logs()

# New Call View
elif st.session_state.view == "new_call":
    with main_container:
        st.header("Make New Call")
        col1, col2 = st.columns(2)
        
        with col1:
            st.text_input("From Number", value="+16205319372", disabled=True)
        with col2:
            to_number = st.text_input("To Number", placeholder="+1234567890")

        if st.button("📞 Make Call"):
            if to_number:
                with st.spinner("Initiating call..."):
                    call_response = safe_api_call(retell_api.createCall, "+16205319372", to_number)
                    if call_response:
                        st.session_state.call_id = None
                        st.session_state.view = "logs"
                        st.success(f"Call initiated! Call ID: {call_response.call_id}")
                        time.sleep(2)  # Give user time to see the success message
                        st.rerun()
            else:
                st.warning("Please enter the destination phone number")

# Logs View
else:
    with main_container:
        st.header("Call Logs")
        
        with st.spinner("Loading call history..."):
            call_history = safe_api_call(retell_api.getCallHistory)
            
            if call_history:
                # Create tabs for different call states
                all_tab, completed_tab, ongoing_tab = st.tabs(["All Calls", "Completed", "Ongoing"])
                
                def display_call_card(call):
                    with st.container():
                        st.markdown('<div class="call-card">', unsafe_allow_html=True)
                        
                        # Header row with call status and time
                        col1, col2 = st.columns([3, 1])
                        
                        try:
                            start_ts = call.start_timestamp if hasattr(call, 'start_timestamp') else None
                            end_ts = call.end_timestamp if hasattr(call, 'end_timestamp') else None
                            call_date = format_timestamp(start_ts)
                            
                            with col1:
                                to_number = call.to_number if hasattr(call, 'to_number') else 'Unknown'
                                st.markdown(f"##### 📞 Call: {to_number}")
                                if call_date != "N/A":
                                    st.markdown(f"📅 {call_date.strftime('%B %d, %Y at %I:%M %p')}")
                                st.markdown(f"🆔 Call ID: {call.call_id}")
                            
                            with col2:
                                status = call.status if hasattr(call, 'status') else 'Unknown'
                                st.markdown(f"**Status:** {status}")
                                duration = format_duration(start_ts, end_ts)
                                st.markdown(f"⏱️ {duration}")
                        
                        except Exception as e:
                            with col1:
                                st.markdown(f"##### 📞 Call ID: {call.call_id}")
                            with col2:
                                st.markdown("**Status:** Error loading details")
                        
                        try:
                            if hasattr(call, 'call_analysis') and call.call_analysis:
                                with st.expander("Quick Summary"):
                                    summary = call.call_analysis.call_summary if hasattr(call.call_analysis, 'call_summary') else "No summary available"
                                    st.write(summary)
                        except Exception:
                            with st.expander("Quick Summary"):
                                st.write("Error loading summary")
                        
                        col1, col2 = st.columns([4, 1])
                        with col2:
                            if st.button("View Details", key=f"view_{call.call_id}"):
                                show_call_details(call.call_id)
                        
                        st.markdown('</div>', unsafe_allow_html=True)

                # Display calls in appropriate tabs
                if call_history:
                    with all_tab:
                        for call in call_history:
                            display_call_card(call)
                            
                    with completed_tab:
                        completed_calls = [call for call in call_history if getattr(call, 'status', '') == 'completed']
                        if completed_calls:
                            for call in completed_calls:
                                display_call_card(call)
                        else:
                            st.info("No completed calls found")
                            
                    with ongoing_tab:
                        ongoing_calls = [call for call in call_history if getattr(call, 'status', '') in ['in-progress', 'queued']]
                        if ongoing_calls:
                            for call in ongoing_calls:
                                display_call_card(call)
                        else:
                            st.info("No ongoing calls")
                else:
                    st.info("No calls found in the history")
            else:
                st.error("Failed to load call history")

# Add instructions based on current view
if st.session_state.view == "logs":
    st.markdown("""
    ---
    ### Instructions:
    1. Click on "Make New Call" in the sidebar to initiate a new call
    2. Click "View Details" on any call to see full information
    3. Use the tabs to filter calls by status
    4. Click 'Refresh Data' to update the call list
    """)
elif st.session_state.view == "new_call":
    st.markdown("""
    ---
    ### Instructions:
    1. Enter the destination phone number
    2. Click "Make Call" to initiate the call
    3. You'll be redirected to the call logs after the call is initiated
    """)
