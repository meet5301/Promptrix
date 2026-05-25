"""Email Sender Module - Phase 4"""

import smtplib
import asyncio
import time
import json
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmailProvider(Enum):
    """Email service providers"""
    SMTP = "smtp"
    GMAIL = "gmail"
    SENDGRID = "sendgrid"


class EmailStatus(Enum):
    """Email delivery status"""
    PENDING = "pending"
    SENDING = "sending"
    SENT = "sent"
    FAILED = "failed"
    BOUNCED = "bounced"


@dataclass
class EmailMessage:
    """Email message structure"""
    id: str
    to: str
    subject: str
    html_content: str
    plain_text: str
    from_email: str
    from_name: str
    reply_to: Optional[str] = None
    cc: Optional[List[str]] = None
    bcc: Optional[List[str]] = None
    headers: Optional[Dict[str, str]] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: str = None
    updated_at: str = None
    status: str = "pending"
    attempts: int = 0
    last_error: Optional[str] = None

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class EmailResult:
    """Email sending result"""
    success: bool
    message_id: Optional[str] = None
    status: str = "pending"
    error: Optional[str] = None
    timestamp: str = None


class EmailQueue:
    """In-memory email queue with SQLite persistence"""

    def __init__(self, db_path: str = "email_queue.db"):
        self.db_path = db_path
        self.in_memory = db_path == ":memory:"
        self._init_db()

    def _get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        if self.in_memory:
            conn.isolation_level = None  # Autocommit mode for in-memory
        return conn

    def _init_db(self):
        """Initialize SQLite database"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS email_queue (
                id TEXT PRIMARY KEY,
                to_email TEXT,
                subject TEXT,
                html_content TEXT,
                plain_text TEXT,
                from_email TEXT,
                from_name TEXT,
                reply_to TEXT,
                cc TEXT,
                bcc TEXT,
                headers TEXT,
                metadata TEXT,
                status TEXT,
                attempts INTEGER,
                last_error TEXT,
                created_at TEXT,
                updated_at TEXT,
                next_retry TEXT
            )
        """)
        conn.commit()
        conn.close()

    def add(self, email: EmailMessage) -> bool:
        """Add email to queue"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO email_queue (
                    id, to_email, subject, html_content, plain_text,
                    from_email, from_name, reply_to, cc, bcc, headers,
                    metadata, status, attempts, last_error, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                email.id, email.to, email.subject, email.html_content,
                email.plain_text, email.from_email, email.from_name,
                email.reply_to, json.dumps(email.cc or []),
                json.dumps(email.bcc or []), json.dumps(email.headers or {}),
                json.dumps(email.metadata or {}), email.status,
                email.attempts, email.last_error,
                email.created_at or datetime.utcnow().isoformat(),
                email.updated_at or datetime.utcnow().isoformat()
            ))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Failed to add email to queue: {e}")
            return False

    def get_pending(self, limit: int = 100) -> List[EmailMessage]:
        """Get pending emails"""
        try:
            conn = self._get_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM email_queue 
                WHERE status = 'pending' 
                AND (next_retry IS NULL OR next_retry <= ?)
                LIMIT ?
            """, (datetime.utcnow().isoformat(), limit))
            rows = cursor.fetchall()
            conn.close()

            emails = []
            for row in rows:
                email = EmailMessage(
                    id=row['id'],
                    to=row['to_email'],
                    subject=row['subject'],
                    html_content=row['html_content'],
                    plain_text=row['plain_text'],
                    from_email=row['from_email'],
                    from_name=row['from_name'],
                    reply_to=row['reply_to'],
                    cc=json.loads(row['cc']),
                    bcc=json.loads(row['bcc']),
                    headers=json.loads(row['headers']),
                    metadata=json.loads(row['metadata']),
                    status=row['status'],
                    attempts=row['attempts'],
                    last_error=row['last_error']
                )
                emails.append(email)
            return emails
        except Exception as e:
            logger.error(f"Failed to get pending emails: {e}")
            return []

    def update_status(self, email_id: str, status: str, error: Optional[str] = None):
        """Update email status"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE email_queue 
                SET status = ?, last_error = ?, updated_at = ?
                WHERE id = ?
            """, (status, error, datetime.utcnow().isoformat(), email_id))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to update email status: {e}")

    def increment_attempts(self, email_id: str):
        """Increment attempt counter"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE email_queue 
                SET attempts = attempts + 1, updated_at = ?
                WHERE id = ?
            """, (datetime.utcnow().isoformat(), email_id))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to increment attempts: {e}")

    def schedule_retry(self, email_id: str, retry_in_seconds: int):
        """Schedule retry with exponential backoff"""
        try:
            retry_time = datetime.utcnow() + timedelta(seconds=retry_in_seconds)
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE email_queue 
                SET next_retry = ?, updated_at = ?
                WHERE id = ?
            """, (retry_time.isoformat(), datetime.utcnow().isoformat(), email_id))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to schedule retry: {e}")

    def get_status(self, email_id: str) -> Optional[Dict[str, Any]]:
        """Get email status"""
        try:
            conn = self._get_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM email_queue WHERE id = ?", (email_id,))
            row = cursor.fetchone()
            conn.close()

            if row:
                return {
                    "id": row['id'],
                    "to": row['to_email'],
                    "status": row['status'],
                    "attempts": row['attempts'],
                    "error": row['last_error'],
                    "created_at": row['created_at'],
                    "updated_at": row['updated_at']
                }
            return None
        except Exception as e:
            logger.error(f"Failed to get email status: {e}")
            return None

    def get_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get email logs"""
        try:
            conn = self._get_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, to_email, subject, status, attempts, last_error, created_at, updated_at
                FROM email_queue
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            conn.close()

            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Failed to get logs: {e}")
            return []


class SMTPEmailSender:
    """SMTP Email Sender"""

    def __init__(self, smtp_server: str, smtp_port: int, username: str, password: str, use_tls: bool = True):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.use_tls = use_tls

    def send(self, email: EmailMessage) -> EmailResult:
        """Send email via SMTP"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = Header(email.subject, 'utf-8')
            msg['From'] = f"{email.from_name} <{email.from_email}>"
            msg['To'] = email.to

            if email.reply_to:
                msg['Reply-To'] = email.reply_to

            if email.cc:
                msg['Cc'] = ', '.join(email.cc)

            # Add custom headers
            if email.headers:
                for key, value in email.headers.items():
                    msg[key] = value

            # Add body
            msg.attach(MIMEText(email.plain_text, 'plain', _charset='utf-8'))
            msg.attach(MIMEText(email.html_content, 'html', _charset='utf-8'))

            # Connect and send
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.username, self.password)

                # Send to all recipients
                recipients = [email.to] + (email.cc or []) + (email.bcc or [])
                server.sendmail(email.from_email, recipients, msg.as_string())

            logger.info(f"Email sent successfully: {email.id}")
            return EmailResult(
                success=True,
                message_id=email.id,
                status="sent",
                timestamp=datetime.utcnow().isoformat()
            )

        except Exception as e:
            error_msg = f"SMTP error: {str(e)}"
            logger.error(error_msg)
            return EmailResult(
                success=False,
                status="failed",
                error=error_msg,
                timestamp=datetime.utcnow().isoformat()
            )


class GmailSender:
    """Gmail SMTP Sender (using app-specific password)"""

    GMAIL_SMTP = "smtp.gmail.com"
    GMAIL_PORT = 587

    def __init__(self, gmail_address: str, app_password: str):
        self.gmail_address = gmail_address
        self.app_password = app_password
        self.sender = SMTPEmailSender(
            self.GMAIL_SMTP,
            self.GMAIL_PORT,
            gmail_address,
            app_password,
            use_tls=True
        )

    def send(self, email: EmailMessage) -> EmailResult:
        """Send via Gmail"""
        email.from_email = self.gmail_address
        return self.sender.send(email)


class SendgridSender:
    """Sendgrid Email Sender"""

    SENDGRID_API = "https://api.sendgrid.com/v3/mail/send"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def send(self, email: EmailMessage) -> EmailResult:
        """Send via Sendgrid"""
        try:
            import requests

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            # Build Sendgrid payload
            payload = {
                "personalizations": [{
                    "to": [{"email": email.to}],
                    "cc": [{"email": cc} for cc in (email.cc or [])],
                    "bcc": [{"email": bcc} for bcc in (email.bcc or [])],
                    "subject": email.subject
                }],
                "from": {
                    "email": email.from_email,
                    "name": email.from_name
                },
                "reply_to": {"email": email.reply_to} if email.reply_to else None,
                "content": [
                    {
                        "type": "text/plain",
                        "value": email.plain_text
                    },
                    {
                        "type": "text/html",
                        "value": email.html_content
                    }
                ],
                "custom_args": email.metadata or {}
            }

            # Remove None values
            if payload["reply_to"] is None:
                del payload["reply_to"]

            response = requests.post(self.SENDGRID_API, json=payload, headers=headers)

            if response.status_code == 202:
                logger.info(f"Email sent via Sendgrid: {email.id}")
                return EmailResult(
                    success=True,
                    message_id=email.id,
                    status="sent",
                    timestamp=datetime.utcnow().isoformat()
                )
            else:
                error_msg = f"Sendgrid error: {response.text}"
                logger.error(error_msg)
                return EmailResult(
                    success=False,
                    status="failed",
                    error=error_msg,
                    timestamp=datetime.utcnow().isoformat()
                )

        except Exception as e:
            error_msg = f"Sendgrid error: {str(e)}"
            logger.error(error_msg)
            return EmailResult(
                success=False,
                status="failed",
                error=error_msg,
                timestamp=datetime.utcnow().isoformat()
            )


class EmailSender:
    """Main Email Sender with provider abstraction"""

    def __init__(self, provider: EmailProvider, **config):
        self.provider = provider
        self.config = config
        self.queue = EmailQueue()
        self._init_sender()

    def _init_sender(self):
        """Initialize appropriate email sender"""
        if self.provider == EmailProvider.SMTP:
            self.sender = SMTPEmailSender(**self.config)
        elif self.provider == EmailProvider.GMAIL:
            self.sender = GmailSender(**self.config)
        elif self.provider == EmailProvider.SENDGRID:
            self.sender = SendgridSender(**self.config)
        else:
            raise ValueError(f"Unknown email provider: {self.provider}")

    def send(self, email: EmailMessage) -> EmailResult:
        """Send email with retry logic"""
        try:
            # Add to queue
            self.queue.add(email)
            self.queue.update_status(email.id, "sending")

            # Send
            result = self.sender.send(email)

            # Update status
            if result.success:
                self.queue.update_status(email.id, "sent")
            else:
                self.queue.increment_attempts(email.id)
                # Exponential backoff: 5s, 30s, 5m, 30m, 2h
                backoff_seconds = 5 * (2 ** min(email.attempts, 4))
                self.queue.schedule_retry(email.id, backoff_seconds)
                self.queue.update_status(email.id, "failed", result.error)

            return result

        except Exception as e:
            error_msg = f"Send error: {str(e)}"
            logger.error(error_msg)
            self.queue.update_status(email.id, "failed", error_msg)
            return EmailResult(
                success=False,
                status="failed",
                error=error_msg,
                timestamp=datetime.utcnow().isoformat()
            )

    def process_queue(self, batch_size: int = 10) -> Dict[str, int]:
        """Process pending emails from queue"""
        stats = {"sent": 0, "failed": 0, "retried": 0}

        pending_emails = self.queue.get_pending(batch_size)

        for email_msg in pending_emails:
            result = self.send(email_msg)
            if result.success:
                stats["sent"] += 1
            else:
                stats["failed"] += 1

        return stats

    def get_status(self, email_id: str) -> Dict[str, Any]:
        """Get email status from queue"""
        return self.queue.get_status(email_id)

    def get_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get email logs"""
        try:
            conn = self.queue._get_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, to_email, subject, status, attempts, last_error, created_at, updated_at
                FROM email_queue
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            conn.close()

            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Failed to get logs: {e}")
            return []
