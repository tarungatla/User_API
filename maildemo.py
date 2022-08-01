# import sendgrid
import os
# from sendgrid.helpers.mail import Mail, Email, To, Content

# sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
# from_email = Email("tarungatla75@gmail.com")  # Sender 
# to_email = To("atharvmore37@gmail.com")  # Recipient
# subject = "Sendgrid sent you this mail"
# content = Content("Body of the mail", "Hey")
# mail = Mail(from_email, to_email, subject, content)

# # Get a JSON-ready representation of the Mail object0
# mail_json = mail.get()

# # Send an HTTP POST request to /mail/send
# response = sg.client.mail.send.post(request_body=mail_json)
# print(response.status_code)
# print(response.headers)
# print("mail_sent")

# print(os.environ.get('SENDGRID_API_KEY'))
print(os.environ.get('POSTGRESQL_PASSWORD'))