from retell import Retell
import os
from dotenv import load_dotenv

load_dotenv()

client = Retell(
    api_key=os.getenv("RETELL_API_KEY"),
)
call_response = client.call.retrieve(
    "call_ffb37183c7bf4ced9679ed66f09",
)
print(type(call_response))