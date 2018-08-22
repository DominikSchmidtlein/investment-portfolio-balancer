import boto3
from botocore.exceptions import ClientError

class EmailManager:
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


    def __init__(self):
        self.client = boto3.client('ses',region_name=self.AWS_REGION)

    def send_email(self, subject, body):
        # Try to send the email.
        try:
            #Provide the contents of the email.
            response = self.client.send_email(
                Destination={
                    'ToAddresses': [
                        self.RECIPIENT,
                    ],
                },
                Message={
                    'Body': {
                        'Html': {
                            'Charset': self.CHARSET,
                            'Data': self.BODY_HTML.format(subject, body),
                        },
                        'Text': {
                            'Charset': self.CHARSET,
                            'Data': body,
                        },
                    },
                    'Subject': {
                        'Charset': self.CHARSET,
                        'Data': subject,
                    },
                },
                Source=self.SENDER,
            )
        # Display an error if something goes wrong. 
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            print("Email sent! Message ID:"),
            print(response['MessageId'])
