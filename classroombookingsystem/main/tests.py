from django.test import TestCase

# Create your tests here.
from django.core.mail import send_mail
from django.conf import settings

# Send an email (this will print the email content to the console)
send_mail(
    'Test Subject',               # Subject
    'This is the message body.',  # Message body
    settings.DEFAULT_FROM_EMAIL,  # From email (can be any email address)
    ['recipient@example.com'],    # To email addresses (can be any valid email address)
)