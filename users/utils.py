from twilio.rest import Client
from decouple import config
from django.core.mail import send_mail


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




def sendMails(to_email, subj, msg):
    subject = subj
    message = msg
    from_email = None  # uses DEFAULT_FROM_EMAIL
    recipient_list = [to_email]

    send_mail(subject, message, from_email, recipient_list)