"""
Phase 4 Complete Test Suite
Tests for email system, webhooks, and advanced analytics
"""

import unittest
import os
import tempfile
import shutil
from datetime import datetime

from webhooks import WebhookManager, Webhook as WebhookConfig, WebhookEvent
from advanced_analytics import AnalyticsManager, AnalyticsEvent, AnalyticsVisitor


class TestWebhooks(unittest.TestCase):
    """Test webhook system"""

    def setUp(self):
        """Set up test webhook manager"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_webhooks.db")
        self.manager = WebhookManager(db_path=self.db_path)

    def tearDown(self):
        """Clean up"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_create_webhook(self):
        """Test creating webhook"""
        result = self.manager.create_webhook(
            user_id="user_1",
            url="https://example.com/webhook",
            events=["site.created", "email.sent"]
        )

        self.assertIn("id", result)
        self.assertIn("secret", result)
        self.assertEqual(result["user_id"], "user_1")
        self.assertEqual(result["url"], "https://example.com/webhook")

    def test_get_webhook(self):
        """Test getting webhook"""
        created = self.manager.create_webhook(
            user_id="user_1",
            url="https://example.com/webhook",
            events=["site.created"]
        )

        retrieved = self.manager.get_webhook(created["id"])
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.url, "https://example.com/webhook")

    def test_get_user_webhooks(self):
        """Test getting user webhooks"""
        self.manager.create_webhook("user_1", "https://ex1.com", ["site.created"])
        self.manager.create_webhook("user_1", "https://ex2.com", ["email.sent"])
        self.manager.create_webhook("user_2", "https://ex3.com", ["site.updated"])

        user1_hooks = self.manager.get_user_webhooks("user_1")
        self.assertEqual(len(user1_hooks), 2)

        user2_hooks = self.manager.get_user_webhooks("user_2")
        self.assertEqual(len(user2_hooks), 1)

    def test_update_webhook(self):
        """Test updating webhook"""
        created = self.manager.create_webhook(
            user_id="user_1",
            url="https://old.com",
            events=["site.created"]
        )

        self.manager.update_webhook(
            created["id"],
            url="https://new.com",
            active=False
        )

        updated = self.manager.get_webhook(created["id"])
        self.assertEqual(updated.url, "https://new.com")
        self.assertFalse(updated.active)

    def test_delete_webhook(self):
        """Test deleting webhook"""
        created = self.manager.create_webhook(
            user_id="user_1",
            url="https://example.com",
            events=["site.created"]
        )

        deleted = self.manager.delete_webhook(created["id"])
        self.assertTrue(deleted)

        retrieved = self.manager.get_webhook(created["id"])
        self.assertIsNone(retrieved)

    def test_dispatch_event(self):
        """Test event dispatch"""
        webhook = self.manager.create_webhook(
            user_id="user_1",
            url="https://example.com/webhook",
            events=["site.created"]
        )

        result = self.manager.dispatch_event(
            "site.created",
            {"site_id": "site_1", "site_name": "My Site"}
        )

        self.assertIn("event_id", result)
        self.assertEqual(result["deliveries_queued"], 1)

    def test_webhook_event_creation(self):
        """Test webhook event"""
        event = WebhookEvent(
            "site.created",
            {"site_id": "site_1"}
        )

        self.assertIn("evt_", event.id)
        self.assertEqual(event.type, "site.created")
        self.assertIsNotNone(event.timestamp)

    def test_get_delivery_logs(self):
        """Test getting delivery logs"""
        webhook = self.manager.create_webhook(
            user_id="user_1",
            url="https://example.com",
            events=["site.created", "email.sent"]
        )

        self.manager.dispatch_event("site.created", {"site_id": "site_1"})
        self.manager.dispatch_event("site.created", {"site_id": "site_2"})

        logs = self.manager.get_delivery_logs(webhook["id"])
        self.assertEqual(len(logs), 2)


class TestAdvancedAnalytics(unittest.TestCase):
    """Test advanced analytics"""

    def setUp(self):
        """Set up test analytics manager"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_analytics.db")
        self.manager = AnalyticsManager(db_path=self.db_path)

    def tearDown(self):
        """Clean up"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_track_event(self):
        """Test tracking event"""
        event = AnalyticsEvent(
            event_type="page_view",
            site_id="site_1",
            visitor_id="visitor_1",
            session_id="session_1",
            properties={"page": "/about"}
        )

        result = self.manager.track_event(event)
        self.assertTrue(result)

    def test_track_multiple_events(self):
        """Test tracking multiple events"""
        for i in range(5):
            event = AnalyticsEvent(
                event_type="page_view",
                site_id="site_1",
                visitor_id="visitor_1",
                session_id="session_1",
                properties={"page": f"/page{i}"}
            )
            self.manager.track_event(event)

        # Get summary to verify
        summary = self.manager.get_summary("site_1", days=1)
        self.assertEqual(summary["metrics"]["page_views"], 5)

    def test_track_conversion(self):
        """Test tracking conversion"""
        result = self.manager.track_conversion(
            site_id="site_1",
            visitor_id="visitor_1",
            conversion_type="purchase",
            value=99.99
        )
        self.assertTrue(result)

    def test_get_summary(self):
        """Test getting analytics summary"""
        # Track some events
        for i in range(3):
            event = AnalyticsEvent(
                event_type="page_view",
                site_id="site_1",
                visitor_id=f"visitor_{i}",
                session_id=f"session_{i}"
            )
            self.manager.track_event(event)

        summary = self.manager.get_summary("site_1", days=1)

        self.assertEqual(summary["metrics"]["page_views"], 3)
        self.assertEqual(summary["metrics"]["unique_visitors"], 3)
        self.assertIn("bounce_rate", summary["metrics"])
        self.assertIn("conversion_rate", summary["metrics"])

    def test_get_funnel(self):
        """Test conversion funnel"""
        # Track funnel events
        events = ["page_view", "add_to_cart", "checkout", "purchase"]
        for i, event_type in enumerate(events):
            for v in range(5 - i):
                event = AnalyticsEvent(
                    event_type=event_type,
                    site_id="site_1",
                    visitor_id=f"visitor_{v}",
                    session_id=f"session_{v}"
                )
                self.manager.track_event(event)

        funnel = self.manager.get_funnel(
            "site_1",
            event_sequence=events,
            days=1
        )

        self.assertEqual(len(funnel["funnel"]), 4)
        self.assertIn("conversion_rate", funnel)

    def test_get_cohort_analysis(self):
        """Test cohort analysis"""
        # Create events for cohort analysis
        for i in range(3):
            event = AnalyticsEvent(
                event_type="page_view",
                site_id="site_1",
                visitor_id=f"visitor_{i}",
                session_id=f"session_{i}"
            )
            self.manager.track_event(event)

        cohorts = self.manager.get_cohort_analysis("site_1")

        self.assertIn("cohorts", cohorts)
        self.assertIsInstance(cohorts["cohorts"], list)

    def test_get_events_report(self):
        """Test events report"""
        # Track various events
        event_types = ["page_view", "click", "form_submit"]
        for event_type in event_types:
            for i in range(3):
                event = AnalyticsEvent(
                    event_type=event_type,
                    site_id="site_1",
                    visitor_id=f"visitor_{i}",
                    session_id=f"session_{i}"
                )
                self.manager.track_event(event)

        report = self.manager.get_events_report("site_1", days=1)

        self.assertIn("event_types", report)
        self.assertIn("recent_events", report)
        self.assertEqual(len(report["event_types"]), 3)

    def test_analytics_event_creation(self):
        """Test AnalyticsEvent"""
        event = AnalyticsEvent(
            event_type="page_view",
            site_id="site_1",
            visitor_id="visitor_1",
            session_id="session_1",
            properties={"page": "/home"}
        )

        self.assertIn("evt_", event.id)
        self.assertEqual(event.type, "page_view")
        self.assertEqual(event.properties["page"], "/home")


class TestPhase4Integration(unittest.TestCase):
    """Integration tests for Phase 4 components"""

    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.webhook_db = os.path.join(self.temp_dir, "webhooks.db")
        self.analytics_db = os.path.join(self.temp_dir, "analytics.db")
        self.webhook_manager = WebhookManager(db_path=self.webhook_db)
        self.analytics_manager = AnalyticsManager(db_path=self.analytics_db)

    def tearDown(self):
        """Clean up"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_webhook_and_analytics_workflow(self):
        """Test combined webhook and analytics workflow"""
        # Create webhook for analytics events
        webhook = self.webhook_manager.create_webhook(
            user_id="user_1",
            url="https://example.com/webhook",
            events=["analytics.milestone"]
        )

        # Track analytics events
        for i in range(5):
            event = AnalyticsEvent(
                event_type="page_view",
                site_id="site_1",
                visitor_id=f"visitor_{i}",
                session_id=f"session_{i}"
            )
            self.analytics_manager.track_event(event)

        # Dispatch webhook event
        result = self.webhook_manager.dispatch_event(
            "analytics.milestone",
            {"visitors": 5, "page_views": 5}
        )

        self.assertEqual(result["deliveries_queued"], 1)

        # Verify analytics
        summary = self.analytics_manager.get_summary("site_1", days=1)
        self.assertEqual(summary["metrics"]["unique_visitors"], 5)


def run_tests():
    """Run all Phase 4 tests"""
    print("\n" + "="*70)
    print("🧪 Phase 4 Complete Test Suite")
    print("="*70)

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestWebhooks))
    suite.addTests(loader.loadTestsFromTestCase(TestAdvancedAnalytics))
    suite.addTests(loader.loadTestsFromTestCase(TestPhase4Integration))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "="*70)
    if result.wasSuccessful():
        print(f"✅ All {result.testsRun} tests passed!")
    else:
        print(f"❌ {len(result.failures)} failures, {len(result.errors)} errors")
    print("="*70 + "\n")

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
