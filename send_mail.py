import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import configparser

def send_email(sender_email, sender_password, recipient_email, subject, body, smtp_server, smtp_port):
    try:
        # Create the email
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Connect to the SMTP server and send the email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            print("Email sent successfully!")

    except Exception as e:
        print(f"Failed to send email: {e}")

if __name__ == "__main__":
    # Load configuration from properties file
    config = configparser.ConfigParser()
    config.read('config.properties')

    sender_email = config['smtp']['sender_email']
    sender_password = config['smtp']['sender_password']
    smtp_server = config['smtp']['smtp_server']
    smtp_port = int(config['smtp']['smtp_port'])

    recipient_email = config['email']['recipient_email']
    subject = config['email']['subject']
    body = config['email']['body']

    send_email(sender_email, sender_password, recipient_email, subject, body, smtp_server, smtp_port)