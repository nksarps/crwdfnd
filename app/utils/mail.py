from decouple import config
from trycourier import Courier

from pydantic import EmailStr

client = Courier(auth_token=config('COURIER_TOKEN'))

def send_email_verification(email: EmailStr, full_name: str, link: str):
    client.send_message(
        message={
            "to": {
            "email": email,
            },
            "template": config('VERIFICATION_TEMPLATE_ID'),
            "data": {
            "appName": "CrwdFnd",
            "firstName": full_name,
            "link": link,
            },
        }
    )