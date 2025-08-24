from boto3 import client
from twilio.rest import Client
from decouple import config
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

account_sid = config('TWILIO_ACCOUNT_SID')
auth_token = config('TWILIO_AUTH_TOKEN')


def sendOTPForMobile(phoneNumber, OTP):
    # Create a client instance
    client = Client(account_sid, auth_token)
    print(f"sending msg to {account_sid} {auth_token}")
    message = client.messages.create(
        body=f"Your Venusa login OTP is: {OTP}. This code is valid for 10 minutes. Do not share this with anyone.",
        from_='+16267885323',  # Your Twilio phone number
        to=f"+91{phoneNumber}"  # Receiver's phone number (e.g., your Indian number)
    )
    print(message)
    return message


def send_successfully_account_created_sms(phoneNumber):

    client = Client(account_sid, auth_token)
    body = f'''VENUSA  
    Dear User, Welcome to VENSUA 

    We’re delighted to have you in our inner circle.  
    Enjoy priority access, curated rewards, and designs built with enduring detail.  

    Start exploring:  
    https://venusa.co.in'''
    message = client.messages.create(
        body=body,
        from_='+16267885323',
        to=f"+91{phoneNumber}"
    )

    print(message)
    return message



def send_html_mail(to_email, subj, html_content):
    subject = subj
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = to_email if isinstance(to_email, list) else [to_email]

    # Create email object
    email = EmailMultiAlternatives(subject, '', from_email, recipient_list)
    email.attach_alternative(html_content, "text/html")  # Attach HTML version
    email.send()