"""Webhook System Module - Phase 4"""

import uuid
import json
import hashlib
import hmac
import logging
from typing import Optional, Dict, List, Any, Callable
from datetime import datetime, timedelta
from enum import Enum
import sqlite3
import requests

logger = logging.getLogger(__name__)


class WebhookEvent(Enum):
    """Webhook event types"""
    SITE_CREATED = "site.created"
    SITE_UPDATED = "site.updated"
    SITE_DELETED = "site.deleted"
    SITE_PUBLISHED = "site.published"
    CONTENT_CREATED = "content.created"
    CONTENT_UPDATED = "content.updated"
    CONTENT_DELETED = "content.deleted"
    EMAIL_SENT = "email.sent"
    EMAIL_FAILED = "email.failed"
    CAMPAIGN_STARTED = "campaign.started"
    CAMPAIGN_COMPLETED = "campaign.completed"
    ANALYTICS_MILESTONE = "analytics.milestone"


class WebhookStatus(Enum):
    """Webhook delivery status"""
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    RETRYING = "retrying"
    ABANDONED = "abandoned"


class Webhook:
    """Webhook configuration"""

    def __init__(self, webhook_id: str, user_id: str, url: str, 
                 events: List[str], secret: str, active: bool = True,
                 created_at: str = None):
        self.id = webhook_id
        self.user_id = user_id
        self.url = url
        self.events = events
        self.secret = secret
        self.active = active
        self.created_at = created_at or datetime.utcnow().isoformat()
        self.updated_at = datetime.utcnow().isoformat()

    def verify_signature(self, payload: str, signature: str) -> bool:
        """Verify HMAC signature"""
        expected = hmac.new(
            self.secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected, signature.replace("sha256=", ""))

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "url": self.url,
            "events": self.events,
            "active": self.active,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


class WebhookEvent:
    """Webhook event payload"""

    def __init__(self, event_type: str, data: Dict[str, Any], 
                 event_id: str = None, timestamp: str = None):
        self.id = event_id or f"evt_{uuid.uuid4().hex[:16]}"
        self.type = event_type
        self.data = data
        self.timestamp = timestamp or datetime.utcnow().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "type": self.type,
            "timestamp": self.timestamp,
            "data": self.data
        }

    def to_json(self) -> str:
        """Convert to JSON"""
        return json.dumps(self.to_dict())


class WebhookDelivery:
    """Webhook delivery record"""

    def __init__(self, delivery_id: str, webhook_id: str, event_id: str,
                 payload: str, status: str = "pending", attempts: int = 0,
                 next_retry: Optional[str] = None, error: Optional[str] = None):
        self.id = delivery_id
        self.webhook_id = webhook_id
        self.event_id = event_id
        self.payload = payload
        self.status = status
        self.attempts = attempts
        self.next_retry = next_retry
        self.error = error
        self.created_at = datetime.utcnow().isoformat()
        self.updated_at = datetime.utcnow().isoformat()


class WebhookManager:
    """Manage webhooks and deliveries"""

    MAX_RETRIES = 5
    RETRY_BACKOFF = [5, 30, 300, 1800, 7200]  # 5s, 30s, 5m, 30m, 2h

    def __init__(self, db_path: str = "webhooks.db"):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        return conn

    def _init_db(self):
        """Initialize database"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Webhooks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS webhooks (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                url TEXT,
                events TEXT,
                secret TEXT,
                active BOOLEAN,
                created_at TEXT,
                updated_at TEXT
            )
        """)

        # Events table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS webhook_events (
                id TEXT PRIMARY KEY,
                type TEXT,
                data TEXT,
                timestamp TEXT,
                created_at TEXT
            )
        """)

        # Deliveries table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS webhook_deliveries (
                id TEXT PRIMARY KEY,
                webhook_id TEXT,
                event_id TEXT,
                payload TEXT,
                status TEXT,
                attempts INTEGER,
                next_retry TEXT,
                error TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        """)

        conn.commit()
        conn.close()

    def create_webhook(self, user_id: str, url: str, events: List[str]) -> Dict[str, Any]:
        """Create webhook"""
        try:
            webhook_id = f"wh_{uuid.uuid4().hex[:16]}"
            secret = uuid.uuid4().hex
            webhook = Webhook(webhook_id, user_id, url, events, secret)

            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO webhooks (id, user_id, url, events, secret, active, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (webhook.id, webhook.user_id, webhook.url, json.dumps(webhook.events),
                  webhook.secret, webhook.active, webhook.created_at, webhook.updated_at))
            conn.commit()
            conn.close()

            result = webhook.to_dict()
            result["secret"] = secret  # Return secret only on creation
            return result

        except Exception as e:
            logger.error(f"Failed to create webhook: {e}")
            return {"error": str(e)}

    def get_webhook(self, webhook_id: str) -> Optional[Webhook]:
        """Get webhook by ID"""
        try:
            conn = self._get_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM webhooks WHERE id = ?", (webhook_id,))
            row = cursor.fetchone()
            conn.close()

            if row:
                return Webhook(
                    row['id'], row['user_id'], row['url'],
                    json.loads(row['events']), row['secret'], row['active'],
                    row['created_at']
                )
            return None
        except Exception as e:
            logger.error(f"Failed to get webhook: {e}")
            return None

    def get_user_webhooks(self, user_id: str) -> List[Webhook]:
        """Get user's webhooks"""
        try:
            conn = self._get_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM webhooks WHERE user_id = ? ORDER BY created_at DESC",
                          (user_id,))
            rows = cursor.fetchall()
            conn.close()

            webhooks = []
            for row in rows:
                webhooks.append(Webhook(
                    row['id'], row['user_id'], row['url'],
                    json.loads(row['events']), row['secret'], row['active'],
                    row['created_at']
                ))
            return webhooks
        except Exception as e:
            logger.error(f"Failed to get user webhooks: {e}")
            return []

    def update_webhook(self, webhook_id: str, **updates) -> bool:
        """Update webhook"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            set_clauses = []
            values = []

            for key, value in updates.items():
                if key == "events":
                    set_clauses.append(f"{key} = ?")
                    values.append(json.dumps(value))
                else:
                    set_clauses.append(f"{key} = ?")
                    values.append(value)

            if set_clauses:
                values.append(webhook_id)
                query = f"UPDATE webhooks SET {', '.join(set_clauses)}, updated_at = ? WHERE id = ?"
                values.insert(-1, datetime.utcnow().isoformat())
                cursor.execute(query, values)
                conn.commit()

            conn.close()
            return True
        except Exception as e:
            logger.error(f"Failed to update webhook: {e}")
            return False

    def delete_webhook(self, webhook_id: str) -> bool:
        """Delete webhook"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM webhooks WHERE id = ?", (webhook_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Failed to delete webhook: {e}")
            return False

    def dispatch_event(self, event_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatch event to webhooks"""
        try:
            event = WebhookEvent(event_type, data)

            # Save event
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO webhook_events (id, type, data, timestamp, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (event.id, event.type, json.dumps(event.data), 
                  event.timestamp, datetime.utcnow().isoformat()))
            conn.commit()
            conn.close()

            # Find webhooks for this event type
            conn = self._get_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM webhooks WHERE active = 1", ())
            webhooks = cursor.fetchall()
            conn.close()

            delivery_count = 0
            for webhook_row in webhooks:
                events = json.loads(webhook_row['events'])
                if event_type in events:
                    # Queue delivery
                    self._queue_delivery(webhook_row['id'], event)
                    delivery_count += 1

            return {
                "event_id": event.id,
                "event_type": event_type,
                "deliveries_queued": delivery_count
            }

        except Exception as e:
            logger.error(f"Failed to dispatch event: {e}")
            return {"error": str(e)}

    def _queue_delivery(self, webhook_id: str, event: WebhookEvent) -> bool:
        """Queue delivery"""
        try:
            delivery_id = f"del_{uuid.uuid4().hex[:16]}"
            payload = event.to_json()

            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO webhook_deliveries 
                (id, webhook_id, event_id, payload, status, attempts, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (delivery_id, webhook_id, event.id, payload, "pending", 0,
                  datetime.utcnow().isoformat(), datetime.utcnow().isoformat()))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Failed to queue delivery: {e}")
            return False

    def get_delivery_logs(self, webhook_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get delivery logs for webhook"""
        try:
            conn = self._get_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM webhook_deliveries 
                WHERE webhook_id = ? 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (webhook_id, limit))
            rows = cursor.fetchall()
            conn.close()

            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Failed to get logs: {e}")
            return []

    def process_deliveries(self, batch_size: int = 10) -> Dict[str, int]:
        """Process pending deliveries"""
        stats = {"sent": 0, "failed": 0, "retried": 0}

        try:
            # Get pending deliveries
            conn = self._get_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM webhook_deliveries
                WHERE status IN ('pending', 'retrying')
                AND (next_retry IS NULL OR next_retry <= ?)
                ORDER BY created_at ASC
                LIMIT ?
            """, (datetime.utcnow().isoformat(), batch_size))
            deliveries = cursor.fetchall()
            conn.close()

            for delivery in deliveries:
                webhook = self.get_webhook(delivery['webhook_id'])
                if not webhook:
                    continue

                # Send to webhook URL
                success = self._send_delivery(webhook, delivery)

                if success:
                    self._update_delivery_status(delivery['id'], "sent")
                    stats["sent"] += 1
                else:
                    # Schedule retry
                    attempts = delivery['attempts'] + 1
                    if attempts < self.MAX_RETRIES:
                        backoff = self.RETRY_BACKOFF[min(attempts - 1, len(self.RETRY_BACKOFF) - 1)]
                        retry_time = datetime.utcnow() + timedelta(seconds=backoff)
                        self._update_delivery_status(
                            delivery['id'], "retrying", 
                            next_retry=retry_time.isoformat(),
                            attempts=attempts
                        )
                        stats["retried"] += 1
                    else:
                        self._update_delivery_status(delivery['id'], "abandoned")
                        stats["failed"] += 1

            return stats
        except Exception as e:
            logger.error(f"Failed to process deliveries: {e}")
            return stats

    def _send_delivery(self, webhook: Webhook, delivery: Dict) -> bool:
        """Send delivery to webhook URL"""
        try:
            payload = delivery['payload']
            signature = f"sha256={hmac.new(webhook.secret.encode(), payload.encode(), hashlib.sha256).hexdigest()}"

            headers = {
                "Content-Type": "application/json",
                "X-Webhook-Signature": signature,
                "X-Webhook-ID": webhook.id,
                "User-Agent": "Promptrix-Webhook/1.0"
            }

            response = requests.post(
                webhook.url,
                data=payload,
                headers=headers,
                timeout=10
            )

            return response.status_code in [200, 201, 202, 204]

        except Exception as e:
            logger.error(f"Failed to send webhook to {webhook.url}: {e}")
            return False

    def _update_delivery_status(self, delivery_id: str, status: str,
                               next_retry: Optional[str] = None, 
                               attempts: Optional[int] = None,
                               error: Optional[str] = None) -> bool:
        """Update delivery status"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            updates = ["status = ?", "updated_at = ?"]
            values = [status, datetime.utcnow().isoformat()]

            if next_retry:
                updates.append("next_retry = ?")
                values.append(next_retry)

            if attempts is not None:
                updates.append("attempts = ?")
                values.append(attempts)

            if error:
                updates.append("error = ?")
                values.append(error)

            values.append(delivery_id)
            query = f"UPDATE webhook_deliveries SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, values)
            conn.commit()
            conn.close()
            return True

        except Exception as e:
            logger.error(f"Failed to update delivery status: {e}")
            return False


# Singleton instance
_webhook_manager: Optional[WebhookManager] = None


def get_webhook_manager() -> WebhookManager:
    """Get or create webhook manager singleton"""
    global _webhook_manager
    if _webhook_manager is None:
        _webhook_manager = WebhookManager()
    return _webhook_manager


def set_webhook_manager(manager: WebhookManager):
    """Set webhook manager singleton"""
    global _webhook_manager
    _webhook_manager = manager
