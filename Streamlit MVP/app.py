import streamlit as st
import retell_api
import time
from datetime import datetime

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

def show_call_details(call_id):
    st.session_state.call_id = call_id
    st.session_state.view = "call_details"
    st.rerun()

def back_to_logs():
    st.session_state.view = "logs"
    st.session_state.call_id = None
    st.rerun()

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

# Call Details View
if st.session_state.view == "call_details":
    try:
        call_obj = retell_api.getCallObject(st.session_state.call_id)
        
        # Header with call info
        st.title("Call Details")
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
            try:
                summary = retell_api.getCallSummary(st.session_state.call_id)
                st.write(summary)
            except Exception as e:
                st.error("Error loading summary")
                st.write(str(e))

        with tab2:
            try:
                transcript = retell_api.getCallTranscript(st.session_state.call_id)
                st.write(transcript)
            except Exception as e:
                st.error("Error loading transcript")
                st.write(str(e))

        with tab3:
            try:
                analysis = retell_api.getCallAnalysis(st.session_state.call_id)
                st.json(analysis)
            except Exception as e:
                st.error("Error loading analysis")
                st.write(str(e))
            
        with tab4:
            try:
                st.json(call_obj)
            except Exception as e:
                st.error("Error loading call details")
                st.write(str(e))

    except Exception as e:
        st.error(f"Error fetching call data: {str(e)}")
        if st.button("← Return to Call Logs"):
            back_to_logs()

# New Call View
elif st.session_state.view == "new_call":
    st.header("Make New Call")
    col1, col2 = st.columns(2)
    
    with col1:
        st.text_input("From Number", value="+16205319372", disabled=True)
    with col2:
        to_number = st.text_input("To Number", placeholder="+1234567890")

    if st.button("📞 Make Call"):
        if to_number:
            with st.spinner("Initiating call..."):
                try:
                    call_response = retell_api.createCall("+16205319372", to_number)
                    st.session_state.call_id = None  # Reset call_id
                    st.session_state.view = "logs"  # Go to logs view
                    st.success(f"Call initiated! Call ID: {call_response.call_id}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error making call: {str(e)}")
        else:
            st.warning("Please enter the destination phone number")

# Logs View
else:  
    st.header("Call Logs")
    try:
        call_history = retell_api.getCallHistory()
        
        # Create tabs for different call states
        all_tab, completed_tab, ongoing_tab = st.tabs(["All Calls", "Completed", "Ongoing"])
        
        def display_call_card(call):
            try:
                with st.container():
                    # Card styling
                    st.markdown("""
                        <style>
                        .call-card {
                            background-color: #f0f2f6;
                            padding: 1.2rem;
                            border-radius: 0.7rem;
                            margin: 0.7rem 0;
                            border-left: 5px solid #2e6fdf;
                        }
                        </style>
                    """, unsafe_allow_html=True)
                    
                    st.markdown('<div class="call-card">', unsafe_allow_html=True)
                    
                    # Header row with call status and time
                    col1, col2 = st.columns([3, 1])
                    
                    # Get timestamps and handle potential missing attributes
                    try:
                        start_ts = call.start_timestamp if hasattr(call, 'start_timestamp') else None
                        end_ts = call.end_timestamp if hasattr(call, 'end_timestamp') else None
                        call_date = format_timestamp(start_ts)
                        
                        with col1:
                            # Show call ID if to_number is not available
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
                        # Fallback display if there's an error with timestamps
                        with col1:
                            st.markdown(f"##### 📞 Call ID: {call.call_id}")
                        with col2:
                            st.markdown("**Status:** Error loading details")
                    
                    # Try to display summary if available
                    try:
                        if hasattr(call, 'call_analysis') and call.call_analysis:
                            with st.expander("Quick Summary"):
                                summary = call.call_analysis.call_summary if hasattr(call.call_analysis, 'call_summary') else "No summary available"
                                st.write(summary)
                    except Exception:
                        with st.expander("Quick Summary"):
                            st.write("Error loading summary")
                    
                    # Action buttons
                    col1, col2 = st.columns([4, 1])
                    with col2:
                        if st.button("View Details", key=f"view_{call.call_id}"):
                            show_call_details(call.call_id)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
            
            except Exception as e:
                # Fallback card for completely failed calls
                with st.container():
                    st.markdown("""
                        <style>
                        .error-card {
                            background-color: #fff0f0;
                            padding: 1.2rem;
                            border-radius: 0.7rem;
                            margin: 0.7rem 0;
                            border-left: 5px solid #ff0000;
                        }
                        </style>
                    """, unsafe_allow_html=True)
                    st.markdown('<div class="error-card">', unsafe_allow_html=True)
                    st.markdown("⚠️ Error loading call details")
                    if hasattr(call, 'call_id'):
                        st.markdown(f"Call ID: {call.call_id}")
                    st.markdown('</div>', unsafe_allow_html=True)
        
        with all_tab:
            if not call_history:
                st.info("No calls found in history")
            else:
                for call in call_history:
                    display_call_card(call)
                
        with completed_tab:
            completed_calls = [
                call for call in call_history 
                if hasattr(call, 'status') and call.status == 'completed'
            ]
            if not completed_calls:
                st.info("No completed calls found")
            else:
                for call in completed_calls:
                    display_call_card(call)
                
        with ongoing_tab:
            ongoing_calls = [
                call for call in call_history 
                if hasattr(call, 'status') and call.status in ['in-progress', 'queued']
            ]
            if not ongoing_calls:
                st.info("No ongoing calls found")
            else:
                for call in ongoing_calls:
                    display_call_card(call)

    except Exception as e:
        st.error("Error fetching call history")
        st.write("Detailed error info:", str(e))
        st.info("Try refreshing the page or check your connection")

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
