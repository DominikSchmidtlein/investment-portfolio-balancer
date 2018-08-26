import boto3
from botocore.exceptions import ClientError

# Replace sender@example.com with your "From" address.
# This address must be verified with Amazon SES.
SENDER = "Portfolio Balancer <hotshot5hot7@gmail.com>"

# Replace recipient@example.com with a "To" address. If your account
# is still in the sandbox, this address must be verified.
RECIPIENT = "dominik.schmidtlein@gmail.com"

AWS_REGION = "us-east-1"

# The character encoding for the email.
CHARSET = "UTF-8"

# The HTML body of the email.
BODY_HTML = """<html>
<head></head>
<body>
  <h1>{}</h1>
  <pre>{}</pre>
</body>
</html>
            """

def send_email(subject, body):
    client = boto3.client('ses',region_name=AWS_REGION)
    # Try to send the email.
    try:
        #Provide the contents of the email.
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    RECIPIENT,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': BODY_HTML.format(subject, body),
                    },
                    'Text': {
                        'Charset': CHARSET,
                        'Data': body,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': subject,
                },
            },
            Source=SENDER,
        )
    # Display an error if something goes wrong. 
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])
