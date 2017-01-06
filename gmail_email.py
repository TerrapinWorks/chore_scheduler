from email.mime.text import MIMEText
import base64

def create_message(sender, to, subject, message_text):
  # Construct the email using the MIME format
  message = MIMEText(message_text)
  message['to'] = to
  message['from'] = sender
  message['subject'] = subject
  
  """ String probelms in Python 3
  base64.urlsafe_b64encode() takes a byte string.
  message.as_string() returns a Python 3 str string, so we have to encode it
  """

  byte_string = base64.urlsafe_b64encode(message.as_string().encode('ascii'))

  """ More string problems in Python 3
  base64.urlsafe_b64encode() returns a byte string, so we have to decode it
  to be an str type string so give to the Gmail API so that the string will
  JSON Serializable 
  """

  raw = byte_string.decode()
  return {'raw' : raw}


def send_message(service, user_id, message):
  """ Send message to the Gmail API
  This function assumes that service is a Service object fir the Gmail API,
  and that message is constructed using create_message()
  """

  try:
    message = (service.users().messages().send(userId = user_id, body=message)
    		.execute())
    print('Sending email')
  except error:
    print('Error sending email')
