from django.core.mail import send_mail
from random import randint  
from apis.models import CustomUser
from django.conf import settings
from mailjet_rest import Client
import random
import string

api_key = 'f0340625a2ba8ccf2105e47e8a5636a3'
api_secret ='1cd7642fdd0cc785f4d9085f449c5b5c'
mailjet = Client(auth=(api_key, api_secret), version='v3.1')

def send_otp_via_email(email,name):

    subject = "Your OTP for verification"
    otp = randint(1000, 9999)  
    message = f"Your OTP for verification is {otp}"
    data = {
        'Messages': [
                        {
                                "From": {
                                        "Email": "arsalanbashir831@gmail.com",
                                        "Name": "VirtuHire"
                                },
                                "To": [
                                        {
                                                "Email": email,
                                                "Name": name
                                        }
                                ],
                                "Subject": subject,
                                "HTMLPart": "<h3>Hello ! your otp is "+str(otp)+"</h3><br />"
                        }
                ]
        }
    result = mailjet.send.create(data=data)

    
    userobj = CustomUser.objects.get(email=email)
    userobj.otp = otp
    userobj.save()


def generate_random_string(length=10):
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string


def forgot_password_email(email,name):

    subject = "Your OTP for verification"
    password = generate_random_string()
    message = f"Your OTP for verification is {otp}"
    data = {
        'Messages': [
                        {
                                "From": {
                                        "Email": "arsalanbashir831@gmail.com",
                                        "Name": "VirtuHire"
                                },
                                "To": [
                                        {
                                                "Email": email,
                                                "Name": name
                                        }
                                ],
                                "Subject": subject,
                                "HTMLPart": "<h3>Hello ! your temporary password is  "+password+" Do Change it once you are logged in ! </h3><br />"
                        }
                ]
        }
    result = mailjet.send.create(data=data)
    userobj = CustomUser.objects.get(email=email)
    userobj.password = password
    userobj.save()