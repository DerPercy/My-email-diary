import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import configparser
from datetime import datetime  # Import für das aktuelle Datum
import os

def send_email(sender_email, sender_password, recipient_email, subject, body, smtp_server, smtp_port, attachments):
    try:
        # Create the email
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Add attachments
        for attachment_path in attachments:
            with open(attachment_path, "rb") as attachment_file:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment_file.read())
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename={os.path.basename(attachment_path)}",
                )
                msg.attach(part)

        # Connect to the SMTP server and send the email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            print("Email sent successfully!")

    except Exception as e:
        print(f"Failed to send email: {e}")

def find_previous_texts_and_attachments(current_date):
    """
    Sucht nach Texten und Anhängen am gleichen Tag in anderen Jahren und gibt deren Inhalte und Pfade zurück.
    """
    day, month, year = current_date.split(".")
    base_path = os.path.join("data", "diary")
    additional_texts = []
    attachments = []

    if os.path.exists(base_path):
        for other_year in os.listdir(base_path):
            if other_year != year:  # Prüfe nur andere Jahre
                potential_path = os.path.join(base_path, other_year, month, day)
                if os.path.exists(potential_path):
                    for message_id in os.listdir(potential_path):
                        content_file = os.path.join(potential_path, message_id, "content.txt")
                        if os.path.isfile(content_file):
                            with open(content_file, "r", encoding="utf-8") as f:
                                additional_texts.append(str(other_year)+":" +f.read())
                        
                        # Suche nach Anhängen
                        for file in os.listdir(os.path.join(potential_path, message_id)):
                            if file != "content.txt":  # Ignoriere die Textdatei
                                attachments.append(os.path.join(potential_path, message_id, file))

    return "\n\n".join(additional_texts), attachments

if __name__ == "__main__":
    # Load configuration from properties file
    config = configparser.ConfigParser()
    config.read('config.properties')

    sender_email = config['smtp']['sender_email']
    sender_password = config['smtp']['sender_password']
    smtp_server = config['smtp']['smtp_server']
    smtp_port = int(config['smtp']['smtp_port'])

    recipient_email = config['email']['recipient_email']
    body = config['email']['body']

    # Dynamischer Betreff mit aktuellem Datum
    current_date = datetime.now().strftime("%d.%m.%Y")
    subject = f"Wie gehts dir heute am {current_date}?"

    # Suche nach Texten und Anhängen am gleichen Tag in anderen Jahren
    previous_texts, attachments = find_previous_texts_and_attachments(current_date)
    if previous_texts:
        body += "\n\n--- Texte aus anderen Jahren am gleichen Tag ---\n" + previous_texts

    send_email(sender_email, sender_password, recipient_email, subject, body, smtp_server, smtp_port, attachments)