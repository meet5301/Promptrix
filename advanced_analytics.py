"""
Advanced Analytics Module - Phase 4
Real-time event tracking, visitor profiling, and funnel analysis
"""

import uuid
import json
import logging
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
from collections import defaultdict
import sqlite3

logger = logging.getLogger(__name__)


class AnalyticsEvent:
    """Analytics event"""

    def __init__(self, event_type: str, site_id: str, visitor_id: str,
                 session_id: str, properties: Optional[Dict[str, Any]] = None,
                 event_id: str = None, timestamp: str = None):
        self.id = event_id or f"evt_{uuid.uuid4().hex[:16]}"
        self.type = event_type
        self.site_id = site_id
        self.visitor_id = visitor_id
        self.session_id = session_id
        self.properties = properties or {}
        self.timestamp = timestamp or datetime.utcnow().isoformat()


class AnalyticsVisitor:
    """Visitor profile"""

    def __init__(self, visitor_id: str, site_id: str, first_seen: str = None,
                 last_seen: str = None, session_count: int = 0, event_count: int = 0):
        self.id = visitor_id
        self.site_id = site_id
        self.first_seen = first_seen or datetime.utcnow().isoformat()
        self.last_seen = last_seen or datetime.utcnow().isoformat()
        self.session_count = session_count
        self.event_count = event_count


class AnalyticsSession:
    """Visitor session"""

    def __init__(self, session_id: str, visitor_id: str, site_id: str,
                 started_at: str = None, ended_at: Optional[str] = None,
                 event_count: int = 0, properties: Optional[Dict[str, Any]] = None):
        self.id = session_id
        self.visitor_id = visitor_id
        self.site_id = site_id
        self.started_at = started_at or datetime.utcnow().isoformat()
        self.ended_at = ended_at
        self.event_count = event_count
        self.properties = properties or {}


class AnalyticsManager:
    """Manage analytics events and reports"""

    def __init__(self, db_path: str = "analytics.db"):
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

        # Events table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analytics_events (
                id TEXT PRIMARY KEY,
                type TEXT,
                site_id TEXT,
                visitor_id TEXT,
                session_id TEXT,
                properties TEXT,
                timestamp TEXT,
                created_at TEXT
            )
        """)

        # Visitors table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analytics_visitors (
                id TEXT PRIMARY KEY,
                site_id TEXT,
                first_seen TEXT,
                last_seen TEXT,
                session_count INTEGER,
                event_count INTEGER,
                properties TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        """)

        # Sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analytics_sessions (
                id TEXT PRIMARY KEY,
                visitor_id TEXT,
                site_id TEXT,
                started_at TEXT,
                ended_at TEXT,
                event_count INTEGER,
                properties TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        """)

        # Conversions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analytics_conversions (
                id TEXT PRIMARY KEY,
                site_id TEXT,
                visitor_id TEXT,
                conversion_type TEXT,
                value REAL,
                timestamp TEXT,
                properties TEXT,
                created_at TEXT
            )
        """)

        conn.commit()
        conn.close()

    def track_event(self, event: AnalyticsEvent) -> bool:
        """Track analytics event"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # Insert event
            cursor.execute("""
                INSERT INTO analytics_events
                (id, type, site_id, visitor_id, session_id, properties, timestamp, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (event.id, event.type, event.site_id, event.visitor_id,
                  event.session_id, json.dumps(event.properties),
                  event.timestamp, datetime.utcnow().isoformat()))

            # Update visitor
            cursor.execute("""
                INSERT INTO analytics_visitors
                (id, site_id, first_seen, last_seen, session_count, event_count, properties, created_at, updated_at)
                VALUES (?, ?, ?, ?, 1, 1, '{}', ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    last_seen = ?, event_count = event_count + 1, updated_at = ?
            """, (event.visitor_id, event.site_id, event.timestamp, event.timestamp,
                  datetime.utcnow().isoformat(), datetime.utcnow().isoformat(),
                  event.timestamp, datetime.utcnow().isoformat()))

            # Update session
            cursor.execute("""
                INSERT INTO analytics_sessions
                (id, visitor_id, site_id, started_at, event_count, properties, created_at, updated_at)
                VALUES (?, ?, ?, ?, 1, '{}', ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    event_count = event_count + 1, updated_at = ?
            """, (event.session_id, event.visitor_id, event.site_id, event.timestamp,
                  datetime.utcnow().isoformat(), datetime.utcnow().isoformat(),
                  datetime.utcnow().isoformat()))

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            logger.error(f"Failed to track event: {e}")
            return False

    def track_conversion(self, site_id: str, visitor_id: str, conversion_type: str,
                        value: float = 1.0, properties: Optional[Dict[str, Any]] = None) -> bool:
        """Track conversion"""
        try:
            conversion_id = f"conv_{uuid.uuid4().hex[:16]}"
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO analytics_conversions
                (id, site_id, visitor_id, conversion_type, value, timestamp, properties, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (conversion_id, site_id, visitor_id, conversion_type, value,
                  datetime.utcnow().isoformat(), json.dumps(properties or {}),
                  datetime.utcnow().isoformat()))

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            logger.error(f"Failed to track conversion: {e}")
            return False

    def get_summary(self, site_id: str, days: int = 30) -> Dict[str, Any]:
        """Get analytics summary"""
        try:
            since = (datetime.utcnow() - timedelta(days=days)).isoformat()

            conn = self._get_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Page views (count of page_view events)
            cursor.execute("""
                SELECT COUNT(*) as count FROM analytics_events
                WHERE site_id = ? AND type = 'page_view' AND timestamp >= ?
            """, (site_id, since))
            page_views = cursor.fetchone()['count']

            # Unique visitors
            cursor.execute("""
                SELECT COUNT(DISTINCT visitor_id) as count FROM analytics_events
                WHERE site_id = ? AND timestamp >= ?
            """, (site_id, since))
            unique_visitors = cursor.fetchone()['count']

            # Sessions
            cursor.execute("""
                SELECT COUNT(*) as count FROM analytics_sessions
                WHERE site_id = ? AND started_at >= ?
            """, (site_id, since))
            sessions = cursor.fetchone()['count']

            # Conversions
            cursor.execute("""
                SELECT COUNT(*) as count, SUM(value) as total 
                FROM analytics_conversions
                WHERE site_id = ? AND timestamp >= ?
            """, (site_id, since))
            conv_row = cursor.fetchone()
            conversions = conv_row['count']
            conversion_value = conv_row['total'] or 0.0

            # Bounce rate (sessions with 1 event)
            cursor.execute("""
                SELECT COUNT(*) as count FROM analytics_sessions
                WHERE site_id = ? AND event_count = 1 AND started_at >= ?
            """, (site_id, since))
            bounces = cursor.fetchone()['count']
            bounce_rate = (bounces / sessions * 100) if sessions > 0 else 0

            # Conversion rate
            conversion_rate = (conversions / unique_visitors * 100) if unique_visitors > 0 else 0

            conn.close()

            return {
                "site_id": site_id,
                "period_days": days,
                "period_end": datetime.utcnow().isoformat(),
                "metrics": {
                    "page_views": page_views,
                    "unique_visitors": unique_visitors,
                    "sessions": sessions,
                    "bounce_rate": round(bounce_rate, 2),
                    "conversions": conversions,
                    "conversion_rate": round(conversion_rate, 2),
                    "conversion_value": round(conversion_value, 2)
                }
            }

        except Exception as e:
            logger.error(f"Failed to get summary: {e}")
            return {"error": str(e)}

    def get_funnel(self, site_id: str, event_sequence: List[str], days: int = 30) -> Dict[str, Any]:
        """Get conversion funnel"""
        try:
            since = (datetime.utcnow() - timedelta(days=days)).isoformat()
            funnel = []

            conn = self._get_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            for i, event_type in enumerate(event_sequence):
                if i == 0:
                    # First event - all occurrences
                    cursor.execute("""
                        SELECT COUNT(DISTINCT visitor_id) as count
                        FROM analytics_events
                        WHERE site_id = ? AND type = ? AND timestamp >= ?
                    """, (site_id, event_type, since))
                else:
                    # Subsequent events - only visitors who completed previous
                    previous_event = event_sequence[i - 1]
                    cursor.execute(f"""
                        SELECT COUNT(DISTINCT e1.visitor_id) as count
                        FROM analytics_events e1
                        WHERE e1.site_id = ? AND e1.type = ? AND e1.timestamp >= ?
                        AND EXISTS (
                            SELECT 1 FROM analytics_events e2
                            WHERE e2.visitor_id = e1.visitor_id
                            AND e2.site_id = ?
                            AND e2.type = ?
                            AND e2.timestamp < e1.timestamp
                        )
                    """, (site_id, event_type, since, site_id, previous_event))

                row = cursor.fetchone()
                count = row['count']
                funnel.append({
                    "step": i + 1,
                    "event": event_type,
                    "count": count,
                    "drop_off": funnel[i - 1]["count"] - count if i > 0 else 0
                })

            conn.close()

            # Calculate conversion rate
            first = funnel[0]["count"]
            last = funnel[-1]["count"]
            conversion_rate = (last / first * 100) if first > 0 else 0

            return {
                "site_id": site_id,
                "event_sequence": event_sequence,
                "period_days": days,
                "conversion_rate": round(conversion_rate, 2),
                "funnel": funnel
            }

        except Exception as e:
            logger.error(f"Failed to get funnel: {e}")
            return {"error": str(e)}

    def get_cohort_analysis(self, site_id: str, cohort_size_days: int = 7) -> Dict[str, Any]:
        """Get cohort analysis"""
        try:
            conn = self._get_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Get visitors grouped by signup date
            cursor.execute("""
                SELECT 
                    DATE(first_seen) as cohort_date,
                    COUNT(*) as cohort_size
                FROM analytics_visitors
                WHERE site_id = ?
                GROUP BY DATE(first_seen)
                ORDER BY cohort_date DESC
            """, (site_id,))

            rows = cursor.fetchall()
            cohorts = []

            for row in rows:
                cohort_date = row['cohort_date']
                cohort_size = row['cohort_size']

                # Get activity in subsequent weeks
                retention = []
                for week in range(5):
                    week_start = datetime.fromisoformat(cohort_date)
                    week_start = week_start.replace(hour=0, minute=0, second=0)
                    week_start += timedelta(days=week * 7)
                    week_end = week_start + timedelta(days=7)

                    cursor.execute("""
                        SELECT COUNT(DISTINCT visitor_id) as active
                        FROM analytics_events
                        WHERE site_id = ?
                        AND visitor_id IN (
                            SELECT id FROM analytics_visitors
                            WHERE site_id = ? AND DATE(first_seen) = ?
                        )
                        AND timestamp >= ? AND timestamp < ?
                    """, (site_id, site_id, cohort_date, week_start.isoformat(), week_end.isoformat()))

                    active = cursor.fetchone()['active']
                    retention_rate = (active / cohort_size * 100) if cohort_size > 0 else 0
                    retention.append(round(retention_rate, 2))

                cohorts.append({
                    "cohort_date": cohort_date,
                    "cohort_size": cohort_size,
                    "retention": retention
                })

            conn.close()

            return {
                "site_id": site_id,
                "cohorts": cohorts
            }

        except Exception as e:
            logger.error(f"Failed to get cohort analysis: {e}")
            return {"error": str(e)}

    def get_events_report(self, site_id: str, days: int = 30, limit: int = 100) -> Dict[str, Any]:
        """Get events report"""
        try:
            since = (datetime.utcnow() - timedelta(days=days)).isoformat()

            conn = self._get_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Event counts by type
            cursor.execute("""
                SELECT type, COUNT(*) as count
                FROM analytics_events
                WHERE site_id = ? AND timestamp >= ?
                GROUP BY type
                ORDER BY count DESC
            """, (site_id, since))

            event_types = [{"type": row['type'], "count": row['count']} for row in cursor.fetchall()]

            # Recent events
            cursor.execute("""
                SELECT id, type, visitor_id, timestamp
                FROM analytics_events
                WHERE site_id = ? AND timestamp >= ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (site_id, since, limit))

            recent = [dict(row) for row in cursor.fetchall()]

            conn.close()

            return {
                "site_id": site_id,
                "period_days": days,
                "event_types": event_types,
                "recent_events": recent
            }

        except Exception as e:
            logger.error(f"Failed to get events report: {e}")
            return {"error": str(e)}


# Singleton instance
_analytics_manager: Optional[AnalyticsManager] = None


def get_analytics_manager() -> AnalyticsManager:
    """Get or create analytics manager singleton"""
    global _analytics_manager
    if _analytics_manager is None:
        _analytics_manager = AnalyticsManager()
    return _analytics_manager


def set_analytics_manager(manager: AnalyticsManager):
    """Set analytics manager singleton"""
    global _analytics_manager
    _analytics_manager = manager
