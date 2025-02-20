from retell import Retell
from dotenv import load_dotenv
import os

load_dotenv()

client = Retell(
    api_key=os.getenv("RETELL_API_KEY"),
)
phone_call_response = client.call.create_phone_call(
    from_number="+16205319372",
    to_number="+919916968672",
)
print(phone_call_response.agent_id)