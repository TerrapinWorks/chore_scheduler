from email.mime.text import MIMEText
import base64

def create_message(sender, to, subject, message_text):
  message = MIMEText(message_text)
  message['to'] = to
  message['from'] = sender
  message['subject'] = subject
  raw = base64.urlsafe_b64encode(message.as_string().encode('ascii'))
  raw = raw.decode()
  return {'raw' : raw}

def send_message(service, user_id, message):
  try:
    message = (service.users().messages().send(userId = user_id, body=message)
    		.execute())
    print('Sending email')
  except error:
    print('Error sending email')
