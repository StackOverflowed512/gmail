import imaplib
import email
import ssl
from email.header import decode_header
from typing import List, Optional
from email import message_from_bytes


class Mail:
    def __init__(
        self,
        email: str,
        password: str,
        smtpHost: str,
        imapHost: str,
        smtpPort: int,
        imapPort: int,
    ):
        self.email = email
        self.password = password
        self.smtpHost = smtpHost
        self.imapHost = imapHost
        self.smtpPort = smtpPort
        self.imapPort = imapPort

    def getmails(self, page: int = 1, per_page: int = 10) -> dict:
        print("Getting mails...")

        try:
            mailserver = imaplib.IMAP4_SSL(self.imapHost, self.imapPort)
            mailserver.login(self.email, self.password)
            mailserver.select("inbox")

            status, data = mailserver.search(None, "ALL")
            if status != "OK":
                return {"status": "error", "message": "No emails found", "emails": []}

            mail_ids = data[0].split()
            mail_ids.reverse()  # Get recent emails first

            # Pagination
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            selected_mails = mail_ids[start_idx:end_idx]

            emails = []
            for mail_id in selected_mails:
                status, msg_data = mailserver.fetch(mail_id, "(RFC822)")
                if status != "OK":
                    continue

                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])

                        uid = mail_id.decode()

                        # Decode subject properly
                        raw_subject = msg["subject"] or "No Subject"
                        decoded_subject, encoding = decode_header(raw_subject)[0]
                        if isinstance(decoded_subject, bytes):
                            subject = decoded_subject.decode(encoding or "utf-8")
                        else:
                            subject = decoded_subject

                        sender = msg["from"] or "Unknown Sender"
                        date = msg["date"] or "Unknown Date"

                        emails.append(
                            {
                                "uid": uid,
                                "from": sender,
                                "subject": subject,
                                "date": date,
                            }
                        )

            mailserver.logout()
            return {
                "status": "success",
                "page": page,
                "per_page": per_page,
                "total": len(mail_ids),
                "emails": emails,
            }

        except Exception as e:
            print(f"Error fetching emails: {e}")
            return {"status": "error", "message": str(e), "emails": []}

    def get_mail_by_uid(self, uid):
        try:
            mailserver = imaplib.IMAP4_SSL(self.imapHost, self.imapPort)
            mailserver.login(self.email, self.password)
            mailserver.select("inbox")

            # Fetch email by UID
            status, msg_data = mailserver.fetch(uid, "(RFC822)")
            if status != "OK":
                return {"status": "error", "message": "Email not found"}

            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = message_from_bytes(response_part[1])

                    # Decode subject properly
                    subject, encoding = decode_header(msg["subject"] or "No Subject")[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding or "utf-8")

                    sender = msg["from"] or "Unknown Sender"
                    date = msg["date"] or "Unknown Date"
                    body = None

                    # Extract body (preferring HTML but falling back to plain text)
                    if msg.is_multipart():
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            content_disposition = str(part.get("Content-Disposition"))

                            if (
                                content_type == "text/html"
                                and "attachment" not in content_disposition
                            ):
                                payload = part.get_payload(decode=True)
                                if payload:
                                    body = payload.decode(
                                        part.get_content_charset() or "utf-8"
                                    )
                                    break  # Use the first HTML version

                            elif content_type == "text/plain" and not body:
                                payload = part.get_payload(decode=True)
                                if payload:
                                    body = payload.decode(
                                        part.get_content_charset() or "utf-8"
                                    )

                    else:
                        payload = msg.get_payload(decode=True)
                        if payload:
                            body = payload.decode(msg.get_content_charset() or "utf-8")

                    mailserver.logout()
                    return {
                        "status": "success",
                        "uid": uid,
                        "from": sender,
                        "subject": subject,
                        "date": date,
                        "body": body.strip() if body else "No content available",
                    }

            mailserver.logout()
            return {"status": "error", "message": "Failed to parse email"}

        except Exception as e:
            print(f"Error fetching email by UID: {e}")
            return {"status": "error", "message": str(e)}

    async def send_email(self, to: str, subject: str, body: str) -> dict:
        try:
            import smtplib
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText

            # Create a multipart message
            msg = MIMEMultipart()
            msg["From"] = self.email
            msg["To"] = to
            msg["Subject"] = subject
            print(f"Sending email to {to} with subject: {subject}")
            # Attach the body with the msg instance
            msg.attach(MIMEText(body, "html"))

            # Check if SSL or STARTTLS is required
            if self.smtpPort == 465:  # SSL
                with smtplib.SMTP_SSL(self.smtpHost, self.smtpPort) as server:
                    server.login(self.email, self.password)
                    server.sendmail(self.email, to, msg.as_string())
            else:  # STARTTLS
                with smtplib.SMTP(self.smtpHost, self.smtpPort) as server:
                    server.starttls(context=ssl.create_default_context())
                    server.login(self.email, self.password)
                    server.sendmail(self.email, to, msg.as_string())

            return {"status": "success", "message": "Email sent successfully"}

        except Exception as e:
            print(f"Error sending email: {e}")
            return {"status": "error", "message": str(e)}

    def mark_as_read(self, uid: str) -> dict:
        try:
            mailserver = imaplib.IMAP4_SSL(self.imapHost, self.imapPort)
            mailserver.login(self.email, self.password)
            mailserver.select("inbox")

            # Mark the email as read
            status, _ = mailserver.store(uid, "+FLAGS", "\\Seen")
            mailserver.logout()

            if status == "OK":
                return {
                    "status": "success",
                    "message": f"Email with UID {uid} marked as read",
                }
            else:
                return {
                    "status": "error",
                    "message": f"Failed to mark email with UID {uid} as read",
                }

        except Exception as e:
            print(f"Error marking email as read: {e}")
            return {"status": "error", "message": str(e)}

    def get_sent_mails(self, page: int = 1, per_page: int = 10) -> dict:
        print("Getting sent mails...")

        try:
            mailserver = imaplib.IMAP4_SSL(self.imapHost, self.imapPort)
            mailserver.login(self.email, self.password)

            # List all mailboxes - some servers require quotes around folder names
            status, mailboxes = mailserver.list()
            if status != "OK":
                return {"status": "error", "message": "Unable to list mailboxes"}

            # Extended list of possible Sent folder names
            sent_folder_candidates = [
                "[Gmail]/Sent Mail",
                "INBOX.Sent",
                "INBOX/Sent",
                "INBOX.Sent Items",
                "INBOX/Sent Items",
                "INBOX.Sent Mail",
                "INBOX/Sent Mail",
                "Sent Messages",
                "Sent",
                "Sent Items",
                "Sent Mail",
            ]
            sent_folder = None

            for mailbox in mailboxes:
                try:
                    # More robust mailbox decoding
                    decoded_mailbox = mailbox.decode()
                    if '"/"' in decoded_mailbox:
                        parts = decoded_mailbox.split('"/"')
                        mailbox_name = parts[-1].strip('"')
                    else:
                        # Some servers use different delimiters
                        mailbox_name = decoded_mailbox.split("|")[-1].strip()

                    # Case-insensitive comparison
                    for candidate in sent_folder_candidates:
                        if candidate.lower() == mailbox_name.lower():
                            sent_folder = mailbox_name
                            break
                        # Also check without INBOX prefix
                        if mailbox_name.lower().endswith(candidate.lower()):
                            sent_folder = mailbox_name
                            break
                    print(f"Found sent folder: {sent_folder}")
                    if sent_folder:
                        break
                except Exception as e:
                    print(f"Error decoding mailbox: {e}")
                    continue

            if not sent_folder:
                available_mailboxes = []
                for mailbox in mailboxes:
                    try:
                        decoded = mailbox.decode()
                        if '"/"' in decoded:
                            available_mailboxes.append(
                                decoded.split('"/"')[-1].strip('"')
                            )
                        else:
                            available_mailboxes.append(decoded.split("|")[-1].strip())
                    except:
                        available_mailboxes.append(str(mailbox))

                return {
                    "status": "error",
                    "message": "Sent folder not found. Available mailboxes printed to console.",
                    "available_mailboxes": available_mailboxes,
                }

            # Select the Sent folder - some servers require quotes

            for i in sent_folder_candidates:
                if i.lower() in sent_folder.lower():
                    sent_folder = i
                    break
            print(f"Selected sent folder: {sent_folder}")
            try:
                status, _ = mailserver.select(f'"{sent_folder}"')
            except:
                status, _ = mailserver.select(f'"{sent_folder}"')

            if status != "OK":
                return {
                    "status": "error",
                    "message": f"Failed to select folder: {sent_folder}",
                }

            # Fetch emails - using UID instead of sequence numbers for reliability
            status, data = mailserver.uid("search", None, "ALL")
            if status != "OK":
                return {
                    "status": "error",
                    "message": "No sent emails found",
                    "emails": [],
                }

            mail_ids = data[0].split()
            mail_ids.reverse()  # Show most recent first

            # Pagination
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            selected_mails = mail_ids[start_idx:end_idx]

            emails = []
            for mail_id in selected_mails:
                try:
                    # Using UID fetch instead of sequence number
                    status, msg_data = mailserver.uid("fetch", mail_id, "(RFC822)")
                    if status != "OK":
                        continue

                    for response_part in msg_data:
                        if isinstance(response_part, tuple):
                            msg = email.message_from_bytes(response_part[1])

                            uid = mail_id.decode()

                            # Improved header decoding
                            raw_subject = msg.get("subject", "No Subject")
                            decoded_subject = decode_header(raw_subject)
                            subject = ""
                            for part, encoding in decoded_subject:
                                if isinstance(part, bytes):
                                    try:
                                        subject += part.decode(
                                            encoding or "utf-8", errors="replace"
                                        )
                                    except:
                                        subject += part.decode(
                                            "ascii", errors="replace"
                                        )
                                else:
                                    subject += str(part)

                            recipient = msg.get("to", "Unknown Recipient")
                            date = msg.get("date", "Unknown Date")

                            emails.append(
                                {
                                    "uid": uid,
                                    "to": recipient,
                                    "subject": subject,
                                    "date": date,
                                }
                            )
                except Exception as e:
                    print(f"Error processing email {mail_id}: {e}")
                    continue

            mailserver.logout()
            return {
                "status": "success",
                "page": page,
                "per_page": per_page,
                "total": len(mail_ids),
                "emails": emails,
            }

        except imaplib.IMAP4.error as e:
            print(f"IMAP error: {e}")
            return {
                "status": "error",
                "message": f"IMAP protocol error: {str(e)}",
                "emails": [],
            }
        except Exception as e:
            print(f"Error fetching sent emails: {e}")
            return {"status": "error", "message": str(e), "emails": []}

    def get_sent_mail_by_uid(self, uid: str) -> dict:
        print("Getting sent mails...")

        try:
            mailserver = imaplib.IMAP4_SSL(self.imapHost, self.imapPort)
            mailserver.login(self.email, self.password)

            # List all mailboxes - some servers require quotes around folder names
            status, mailboxes = mailserver.list()
            if status != "OK":
                return {"status": "error", "message": "Unable to list mailboxes"}

            # Extended list of possible Sent folder names
            sent_folder_candidates = [
                "[Gmail]/Sent Mail",
                "INBOX.Sent",
                "INBOX/Sent",
                "INBOX.Sent Items",
                "INBOX/Sent Items",
                "INBOX.Sent Mail",
                "INBOX/Sent Mail",
                "Sent Messages",
                "Sent",
                "Sent Items",
                "Sent Mail",
            ]
            sent_folder = None

            for mailbox in mailboxes:
                try:
                    # More robust mailbox decoding
                    decoded_mailbox = mailbox.decode()
                    if '"/"' in decoded_mailbox:
                        parts = decoded_mailbox.split('"/"')
                        mailbox_name = parts[-1].strip('"')
                    else:
                        # Some servers use different delimiters
                        mailbox_name = decoded_mailbox.split("|")[-1].strip()

                    # Case-insensitive comparison
                    for candidate in sent_folder_candidates:
                        if candidate.lower() == mailbox_name.lower():
                            sent_folder = mailbox_name
                            break
                        # Also check without INBOX prefix
                        if mailbox_name.lower().endswith(candidate.lower()):
                            sent_folder = mailbox_name
                            break
                    print(f"Found sent folder: {sent_folder}")
                    if sent_folder:
                        break
                except Exception as e:
                    print(f"Error decoding mailbox: {e}")
                    continue

            if not sent_folder:
                available_mailboxes = []
                for mailbox in mailboxes:
                    try:
                        decoded = mailbox.decode()
                        if '"/"' in decoded:
                            available_mailboxes.append(
                                decoded.split('"/"')[-1].strip('"')
                            )
                        else:
                            available_mailboxes.append(decoded.split("|")[-1].strip())
                    except:
                        available_mailboxes.append(str(mailbox))

                return {
                    "status": "error",
                    "message": "Sent folder not found. Available mailboxes printed to console.",
                    "available_mailboxes": available_mailboxes,
                }

            # Select the Sent folder - some servers require quotes

            for i in sent_folder_candidates:
                if i.lower() in sent_folder.lower():
                    sent_folder = i
                    break
            print(f"Selected sent folder: {sent_folder}")
            try:
                status, _ = mailserver.select(f'"{sent_folder}"')
            except:
                status, _ = mailserver.select(f'"{sent_folder}"')

            if status != "OK":
                return {
                    "status": "error",
                    "message": f"Failed to select folder: {sent_folder}",
                }

            # Fetch emails - using UID instead of sequence numbers for reliability
            status, data = mailserver.uid("search", None, "ALL")
            if status != "OK":
                return {
                    "status": "error",
                    "message": "No sent emails found",
                    "emails": [],
                }

            mail_ids = data[0].split()
            mail_ids.reverse()  # Show most recent first

            emails = []
            for mail_id in mail_ids:
                status, msg_data = mailserver.uid("fetch", mail_id, "(RFC822)")
                if status != "OK":
                    print(f"Failed to fetch email with UID: {mail_id}")
                    continue

                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])

                        # Decode subject properly
                        subject, encoding = decode_header(msg["subject"] or "No Subject")[0]
                        if isinstance(subject, bytes):
                            subject = subject.decode(encoding or "utf-8")

                        recipient = msg["to"] or "Unknown Recipient"
                        date = msg["date"] or "Unknown Date"
                        body = None

                        # Extract body (preferring HTML but falling back to plain text)
                        if msg.is_multipart():
                            for part in msg.walk():
                                content_type = part.get_content_type()
                                content_disposition = str(part.get("Content-Disposition"))

                                if (
                                    content_type == "text/html"
                                    and "attachment" not in content_disposition
                                ):
                                    payload = part.get_payload(decode=True)
                                    if payload:
                                        body = payload.decode(
                                            part.get_content_charset() or "utf-8"
                                        )
                                        break  # Use the first HTML version

                                elif content_type == "text/plain" and not body:
                                    payload = part.get_payload(decode=True)
                                    if payload:
                                        body = payload.decode(
                                            part.get_content_charset() or "utf-8"
                                        )

                        else:
                            payload = msg.get_payload(decode=True)
                            if payload:
                                body = payload.decode(msg.get_content_charset() or "utf-8")

                        emails.append(
                            {
                                "uid": mail_id.decode(),
                                "to": recipient,
                                "subject": subject,
                                "date": date,
                                "body": body.strip() if body else "No content available",
                            }
                        )

            mailserver.logout()
            return emails
        
        except imaplib.IMAP4.error as e:
            print(f"IMAP error: {e}")
            return {
                "status": "error",
                "message": f"IMAP protocol error: {str(e)}",
                "emails": [],
            }
        except Exception as e:
            print(f"Error fetching sent emails: {e}")
            return {"status": "error", "message": str(e), "emails": []}