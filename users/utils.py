from twilio.rest import Client
from decouple import config
from django.core.mail import send_mail


account_sid = config('TWILIO_ACCOUNT_SID')
auth_token = config('TWILIO_AUTH_TOKEN')

def sendOTPForMobile(phoneNumber, OTP):
    # Create a client instance
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        body=f"VENUSA: Gaurav bhai bhai bhai code is {OTP}. only valid for 10 mins",
        from_='+16267885323',  # Your Twilio phone number
        to=f"+91{phoneNumber}"  # Receiver's phone number (e.g., your Indian number)
    )

    return message




def sendMails(to_email, subj, msg):
    subject = subj
    message = msg
    from_email = None  # uses DEFAULT_FROM_EMAIL
    recipient_list = [to_email]

    send_mail(subject, message, from_email, recipient_list)