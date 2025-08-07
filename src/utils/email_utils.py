#email_utils.py

import imaplib
import email
from email.header import decode_header
from bs4 import BeautifulSoup


def decode_mime_header(header):
    if not header:
        return "(No Value)"
    decoded_parts = decode_header(header)
    result = ""
    for part, encoding in decoded_parts:
        if isinstance(part, bytes):
            result += part.decode(encoding or "utf-8", errors="replace")
        else:
            result += part
    return result.strip()

def connect_to_mailbox(email_addr, password, server):
    mail = imaplib.IMAP4_SSL(server)
    mail.login(email_addr, password)
    return mail

def search_recent_emails(mail, days=7):
    mail.select("inbox")
    result, data = mail.search(None, f'(SINCE {get_since_date(days)})')
    return data[0].split()

def get_since_date(days):
    from datetime import datetime, timedelta
    date = datetime.today() - timedelta(days=days)
    return date.strftime("%d-%b-%Y")

def get_email_metadata(mail, email_ids):
    results = []
    for eid in email_ids:
        result, data = mail.fetch(eid, "(RFC822)")
        raw = data[0][1]
        msg = email.message_from_bytes(raw)
        subject = decode_mime_header(msg.get("Subject"))
        sender = decode_mime_header(msg.get("From"))
        preview = get_body_preview(msg)

        results.append({
            "id": eid.decode(),
            "subject": subject,
            "from": sender,
            "preview": preview,
            "raw": raw
        })
    return results


def strip_html_tags(html):
    soup = BeautifulSoup(html, "html.parser")
    return "\n".join(soup.stripped_strings)

def get_body_preview(msg, max_lines=2):
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            if "attachment" in content_disposition:
                continue

            try:
                charset = part.get_content_charset() or "utf-8"
                payload = part.get_payload(decode=True)
                if payload:
                    decoded = payload.decode(charset, errors="replace")
                    if content_type == "text/plain":
                        body = decoded
                        break
                    elif content_type == "text/html" and not body:
                        body = strip_html_tags(decoded)
            except Exception:
                continue
    else:
        try:
            charset = msg.get_content_charset() or "utf-8"
            payload = msg.get_payload(decode=True)
            if payload:
                decoded = payload.decode(charset, errors="replace")
                if msg.get_content_type() == "text/html":
                    body = strip_html_tags(decoded)
                else:
                    body = decoded
        except Exception:
            body = msg.get_payload()

    # Normalize and preview
    lines = body.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    preview_lines = [line.strip() for line in lines if line.strip()][:max_lines]
    preview = " ".join(preview_lines)
    return preview + "..." if len(lines) > max_lines else preview