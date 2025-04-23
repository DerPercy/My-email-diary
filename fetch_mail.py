import imaplib
import email
from email.header import decode_header
import configparser
import time
import re  # Import für reguläre Ausdrücke
import os  # Für die Arbeit mit Dateien und Verzeichnissen

# Load credentials from config.properties
config = configparser.ConfigParser()
config.read("config.properties")

IMAP_SERVER = config.get("email", "imap_server")
EMAIL_ACCOUNT = config.get("smtp", "sender_email")
PASSWORD = config.get("smtp", "sender_password")

def extract_relevant_body(body):
    """
    Extrahiert den relevanten Teil des E-Mail-Bodys, indem typische Antwort-Trennzeichen entfernt werden.
    """
    # Liste von typischen Trennzeichen
    reply_markers = [
        "-----Original Message-----",
        "On .* wrote:",
        "Am .* schrieb .*:",
        ".*<"+EMAIL_ACCOUNT+">:"
    ]

    # Überprüfen, ob eines der Trennzeichen im Body vorkommt
    for marker in reply_markers:
        match = re.search(marker, body, re.IGNORECASE)
        if match:
            # Schneidet den Body ab dem Trennzeichen ab
            body = body[:match.start()]
            break

    return body.strip()

def save_email_content(email_date, message_id, relevant_body, attachments):
    """
    Speichert den relevanten Inhalt und die Anhänge in der Ordnerstruktur data/diary/Jahr/monat/tag/messageID.
    """
    # Erstelle die Ordnerstruktur basierend auf dem Datum und der Message-ID
    day, month, year = email_date.split(".")
    directory = os.path.join("data", "diary", year, month.lower(), day, message_id)
    os.makedirs(directory, exist_ok=True)

    # Speichere den relevanten Inhalt in einer Textdatei
    content_file = os.path.join(directory, "content.txt")
    with open(content_file, "w", encoding="utf-8") as f:
        f.write(relevant_body)
    print(f"Relevanter Inhalt gespeichert in: {content_file}")

    # Speichere die Anhänge
    for attachment_name, attachment_data in attachments.items():
        attachment_file = os.path.join(directory, attachment_name)
        with open(attachment_file, "wb") as f:
            f.write(attachment_data)
        print(f"Anhang gespeichert in: {attachment_file}")

def fetch_emails():
    try:
        # Connect to the server
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        # Login to your account
        mail.login(EMAIL_ACCOUNT, PASSWORD)
        # Select the mailbox you want to use
        mail.select("inbox")

        # Search for all emails
        status, messages = mail.search(None, "ALL")
        # Convert messages to a list of email IDs
        email_ids = messages[0].split()

        for email_id in email_ids:
            # Fetch the email by ID
            status, msg_data = mail.fetch(email_id, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    # Parse the email
                    msg = email.message_from_bytes(response_part[1])
                    # Decode the email subject
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        # If it's a bytes type, decode to str
                        subject = subject.decode(encoding if encoding else "utf-8")
                    print(f"Subject: {subject}")
                    
                    # Prüfen, ob der Betreff dem erwarteten Muster entspricht
                    match = re.search(r"(?:Re:|AW:)? Wie gehts dir heute am (\d{2}\.\d{2}\.\d{4})\?$", subject)
                    if match:
                        email_date = match.group(1)  # Datum aus dem Betreff extrahieren
                        print(f"Das Datum im Betreff ist: {email_date}")
                        
                        # Extrahiere die Message-ID
                        message_id = msg.get("Message-ID")
                        if message_id:
                            # Entferne spitze Klammern aus der Message-ID
                            message_id = message_id.strip("<>")
                            print(f"Message-ID: {message_id}")
                        
                        # Decode email sender
                        from_ = msg.get("From")
                        print(f"From: {from_}")

                        # Initialisiere Variablen für den Body und Anhänge
                        relevant_body = ""
                        attachments = {}

                        # If the email has a body
                        if msg.is_multipart():
                            for part in msg.walk():
                                content_type = part.get_content_type()
                                print(content_type)
                                # If the content type is text/plain
                                if content_type == "text/plain":
                                    body = part.get_payload(decode=True).decode()
                                    # Relevanten Teil des Bodys extrahieren
                                    relevant_body = extract_relevant_body(body)
                                # Wenn es ein Anhang oder unterstützter Content-Type ist
                                elif part.get("Content-Disposition") or content_type.startswith("image/") or content_type in ["application/pdf"]:
                                    filename = part.get_filename()
                                    if not filename:
                                        # Generiere einen Standard-Dateinamen, falls keiner vorhanden ist
                                        extension = content_type.split("/")[-1]
                                        filename = f"attachment.{extension}"
                                    attachment_data = part.get_payload(decode=True)
                                    attachments[filename] = attachment_data
                        else:
                            # If the email is not multipart
                            body = msg.get_payload(decode=True).decode()
                            # Relevanten Teil des Bodys extrahieren
                            relevant_body = extract_relevant_body(body)

                        # Speichere den relevanten Inhalt und die Anhänge
                        save_email_content(email_date, message_id, relevant_body, attachments)
                    else:
                        print("Der Betreff entspricht nicht dem erwarteten Muster.")
        # Close the connection and logout
        mail.close()
        mail.logout()
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    fetch_emails()