# AI-agent-mvp

## Retell SDK Integration

This project demonstrates the integration of Retell's Python SDK for managing phone calls and analyzing call data. The implementation provides a streamlined interface for creating, retrieving, and analyzing phone calls using Retell's powerful API.

### Setup

1. Install the required dependencies:
```bash
pip install retell streamlit
```

2. Set up your Retell API key as an environment variable:
```bash
export RETELL_API_KEY='your_api_key_here'
```

### Core Features

The implementation provides the following key functionalities:

#### Call Management
- **Create Phone Calls**: Initiate phone calls between two numbers using `createCall(from_number, to_number)`
- **Retrieve Call History**: Get a sorted list of all calls using `getCallHistory()`
- **Get Call Details**: Fetch specific call information using `getCallObject(call_id)`

#### Call Analysis
- **Call Summaries**: Retrieve call summaries using `getCallSummary(call_id)`
- **Call Transcripts**: Get detailed call transcripts via `getCallTranscript(call_id)`
- **Custom Analysis**: Access custom analysis data through `getCallAnalysis(call_id)`

### Usage Example

```python
from retell_api import Retell, createCall, getCallSummary

# Create a new call
call = createCall("+1234567890", "+0987654321")

# Get call summary
summary = getCallSummary(call.id)
```

### Error Handling

The implementation includes robust error handling for:
- API key validation
- Client initialization
- Call operations
- Data retrieval and processing

### Note

Make sure to properly configure your Retell API key before using any functionality. The system will validate the API key's presence and provide appropriate error messages if not configured correctly.

