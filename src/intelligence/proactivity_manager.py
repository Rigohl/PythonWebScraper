"""
Proactivity Manager for Curiosity System

This module manages proactive notifications and suggestions from the curiosity system.
It implements rate limiting, user preference checking, and advisory-only notifications
to ensure the system remains helpful without being intrusive.
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from .. import settings
from .novelty_detector import NoveltyAnalysis

logger = logging.getLogger(__name__)


class NotificationPriority(Enum):
    """Priority levels for notifications"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class NotificationType(Enum):
    """Types of notifications the system can send"""

    NOVEL_CONTENT = "novel_content"
    INTERESTING_FINDING = "interesting_finding"
    LEARNING_OPPORTUNITY = "learning_opportunity"
    SYSTEM_SUGGESTION = "system_suggestion"


@dataclass
class ProactiveNotification:
    """A proactive notification to be sent to the user"""

    id: str
    type: NotificationType
    priority: NotificationPriority
    title: str
    message: str
    context: Dict[str, Any]
    timestamp: float
    novelty_analysis: Optional[NoveltyAnalysis] = None
    actionable: bool = False


@dataclass
class NotificationResult:
    """Result of sending a notification"""

    notification_id: str
    sent: bool
    reason: str
    timestamp: float


class RateLimiter:
    """Rate limiter for notifications to prevent spam"""

    def __init__(self, max_notifications: int, window_minutes: int):
        self.max_notifications = max_notifications
        self.window_seconds = window_minutes * 60
        self.notifications: List[float] = []  # Timestamps of recent notifications

    def can_send(self) -> bool:
        """Check if a notification can be sent within rate limits."""
        current_time = time.time()

        # Remove old notifications outside the window
        self.notifications = [
            ts for ts in self.notifications if current_time - ts < self.window_seconds
        ]

        return len(self.notifications) < self.max_notifications

    def record_notification(self):
        """Record that a notification was sent."""
        self.notifications.append(time.time())

    def get_remaining_capacity(self) -> int:
        """Get remaining notification capacity in current window."""
        current_time = time.time()
        self.notifications = [
            ts for ts in self.notifications if current_time - ts < self.window_seconds
        ]
        return max(0, self.max_notifications - len(self.notifications))


class ProactivityManager:
    """
    Manages proactive notifications and suggestions from the curiosity system.
    Implements safety measures, rate limiting, and user preference checking.
    """

    def __init__(self):
        # Rate limiters for different priorities
        self.rate_limiters = {
            NotificationPriority.LOW: RateLimiter(
                settings.CURIOSITY_RATE_LIMIT_LOW, settings.CURIOSITY_RATE_LIMIT_MINUTES
            ),
            NotificationPriority.MEDIUM: RateLimiter(
                settings.CURIOSITY_RATE_LIMIT_MEDIUM,
                settings.CURIOSITY_RATE_LIMIT_MINUTES,
            ),
            NotificationPriority.HIGH: RateLimiter(
                settings.CURIOSITY_RATE_LIMIT_HIGH,
                settings.CURIOSITY_RATE_LIMIT_MINUTES,
            ),
            NotificationPriority.CRITICAL: RateLimiter(
                settings.CURIOSITY_RATE_LIMIT_CRITICAL,
                settings.CURIOSITY_RATE_LIMIT_MINUTES,
            ),
        }

        # Notification handlers
        self.notification_handlers: List[Callable[[ProactiveNotification], None]] = []

        # User preference tracking
        self.user_preferences = self._load_user_preferences()

        # Notification history
        self.notification_history: List[NotificationResult] = []

        # Background task for periodic cleanup
        self.cleanup_task = None

        logger.info("ProactivityManager initialized")

    def _load_user_preferences(self) -> Dict[str, Any]:
        """Load user preferences for notifications."""
        # In a real implementation, this would load from persistent storage
        return {
            "enabled_types": {
                NotificationType.NOVEL_CONTENT: True,
                NotificationType.INTERESTING_FINDING: True,
                NotificationType.LEARNING_OPPORTUNITY: True,
                NotificationType.SYSTEM_SUGGESTION: False,  # Disabled by default
            },
            "quiet_hours_start": 22,  # 10 PM
            "quiet_hours_end": 8,  # 8 AM
            "max_daily_notifications": 10,
        }

    def add_notification_handler(
        self, handler: Callable[[ProactiveNotification], None]
    ):
        """Add a handler for processing notifications."""
        self.notification_handlers.append(handler)

    def remove_notification_handler(
        self, handler: Callable[[ProactiveNotification], None]
    ):
        """Remove a notification handler."""
        if handler in self.notification_handlers:
            self.notification_handlers.remove(handler)

    async def notify_novel_content(
        self, analysis: NoveltyAnalysis, context: Optional[Dict[str, Any]] = None
    ) -> NotificationResult:
        """
        Send a notification about novel content discovery.

        Args:
            analysis: Novelty analysis result
            context: Additional context information

        Returns:
            Notification result
        """
        notification_id = f"novel_{int(time.time())}_{hash(analysis.content) % 10000}"

        # Check if this type of notification is enabled
        if not self.user_preferences["enabled_types"].get(
            NotificationType.NOVEL_CONTENT, True
        ):
            return NotificationResult(
                notification_id=notification_id,
                sent=False,
                reason="Notification type disabled by user preferences",
                timestamp=time.time(),
            )

        # Determine priority based on novelty score
        if analysis.score.overall_score >= 0.8:
            priority = NotificationPriority.HIGH
        elif analysis.score.overall_score >= 0.6:
            priority = NotificationPriority.MEDIUM
        else:
            priority = NotificationPriority.LOW

        # Create notification
        notification = ProactiveNotification(
            id=notification_id,
            type=NotificationType.NOVEL_CONTENT,
            priority=priority,
            title="Novel Content Discovered",
            message=self._format_novelty_message(analysis),
            context=context or {},
            timestamp=time.time(),
            novelty_analysis=analysis,
            actionable=False,  # Advisory only
        )

        return await self._send_notification(notification)

    async def notify_interesting_finding(
        self, finding: str, confidence: float, context: Optional[Dict[str, Any]] = None
    ) -> NotificationResult:
        """
        Send a notification about an interesting finding.

        Args:
            finding: Description of the finding
            confidence: Confidence score (0-1)
            context: Additional context

        Returns:
            Notification result
        """
        notification_id = f"finding_{int(time.time())}_{hash(finding) % 10000}"

        # Check preferences
        if not self.user_preferences["enabled_types"].get(
            NotificationType.INTERESTING_FINDING, True
        ):
            return NotificationResult(
                notification_id=notification_id,
                sent=False,
                reason="Notification type disabled by user preferences",
                timestamp=time.time(),
            )

        # Determine priority
        if confidence >= 0.8:
            priority = NotificationPriority.HIGH
        elif confidence >= 0.6:
            priority = NotificationPriority.MEDIUM
        else:
            priority = NotificationPriority.LOW

        notification = ProactiveNotification(
            id=notification_id,
            type=NotificationType.INTERESTING_FINDING,
            priority=priority,
            title="Interesting Finding",
            message=finding,
            context=context or {},
            timestamp=time.time(),
            actionable=False,
        )

        return await self._send_notification(notification)

    async def notify_learning_opportunity(
        self, opportunity: str, context: Optional[Dict[str, Any]] = None
    ) -> NotificationResult:
        """
        Send a notification about a learning opportunity.

        Args:
            opportunity: Description of the learning opportunity
            context: Additional context

        Returns:
            Notification result
        """
        notification_id = f"learning_{int(time.time())}_{hash(opportunity) % 10000}"

        # Check preferences
        if not self.user_preferences["enabled_types"].get(
            NotificationType.LEARNING_OPPORTUNITY, True
        ):
            return NotificationResult(
                notification_id=notification_id,
                sent=False,
                reason="Notification type disabled by user preferences",
                timestamp=time.time(),
            )

        notification = ProactiveNotification(
            id=notification_id,
            type=NotificationType.LEARNING_OPPORTUNITY,
            priority=NotificationPriority.MEDIUM,
            title="Learning Opportunity",
            message=opportunity,
            context=context or {},
            timestamp=time.time(),
            actionable=True,  # Learning opportunities might be actionable
        )

        return await self._send_notification(notification)

    async def _send_notification(
        self, notification: ProactiveNotification
    ) -> NotificationResult:
        """
        Send a notification through all registered handlers.

        Args:
            notification: Notification to send

        Returns:
            Notification result
        """
        # Check rate limits
        if not self.rate_limiters[notification.priority].can_send():
            return NotificationResult(
                notification_id=notification.id,
                sent=False,
                reason=f"Rate limit exceeded for {notification.priority.value} priority",
                timestamp=time.time(),
            )

        # Check quiet hours
        if self._is_quiet_hours():
            return NotificationResult(
                notification_id=notification.id,
                sent=False,
                reason="Currently in user-defined quiet hours",
                timestamp=time.time(),
            )

        # Check daily limit
        if not self._check_daily_limit():
            return NotificationResult(
                notification_id=notification.id,
                sent=False,
                reason="Daily notification limit reached",
                timestamp=time.time(),
            )

        # Send through all handlers
        sent_count = 0
        for handler in self.notification_handlers:
            try:
                await asyncio.get_event_loop().run_in_executor(
                    None, handler, notification
                )
                sent_count += 1
            except Exception as e:
                logger.error(f"Notification handler failed: {e}")

        # Record the notification
        if sent_count > 0:
            self.rate_limiters[notification.priority].record_notification()
            result = NotificationResult(
                notification_id=notification.id,
                sent=True,
                reason=f"Sent to {sent_count} handler(s)",
                timestamp=time.time(),
            )
        else:
            result = NotificationResult(
                notification_id=notification.id,
                sent=False,
                reason="No handlers available or all handlers failed",
                timestamp=time.time(),
            )

        # Store in history
        self.notification_history.append(result)

        return result

    def _is_quiet_hours(self) -> bool:
        """Check if current time is within quiet hours."""
        current_hour = datetime.now().hour
        start = self.user_preferences.get("quiet_hours_start", 22)
        end = self.user_preferences.get("quiet_hours_end", 8)

        if start > end:  # Quiet hours span midnight
            return current_hour >= start or current_hour < end
        else:  # Quiet hours within same day
            return start <= current_hour < end

    def _check_daily_limit(self) -> bool:
        """Check if daily notification limit has been reached."""
        max_daily = self.user_preferences.get("max_daily_notifications", 10)
        today = datetime.now().date()

        # Count notifications from today
        today_count = sum(
            1
            for result in self.notification_history
            if datetime.fromtimestamp(result.timestamp).date() == today and result.sent
        )

        return today_count < max_daily

    def _format_novelty_message(self, analysis: NoveltyAnalysis) -> str:
        """Format a novelty analysis into a user-friendly message."""
        score = analysis.score

        # Create a concise message
        message_parts = []

        if score.overall_score >= 0.8:
            message_parts.append("Highly novel content detected!")
        elif score.overall_score >= 0.6:
            message_parts.append("Moderately novel content found.")
        else:
            message_parts.append("Slightly novel content discovered.")

        # Add key reasons
        if score.reasons:
            top_reasons = score.reasons[:2]  # Limit to top 2 reasons
            message_parts.extend(top_reasons)

        # Add confidence
        confidence_pct = int(score.confidence * 100)
        message_parts.append(f"Confidence: {confidence_pct}%")

        return " ".join(message_parts)

    def get_notification_stats(self) -> Dict[str, Any]:
        """Get statistics about notifications."""
        total_sent = sum(1 for result in self.notification_history if result.sent)
        total_attempted = len(self.notification_history)

        # Rate limiter stats
        rate_stats = {}
        for priority, limiter in self.rate_limiters.items():
            rate_stats[priority.value] = {
                "remaining_capacity": limiter.get_remaining_capacity(),
                "recent_count": len(limiter.notifications),
            }

        return {
            "total_sent": total_sent,
            "total_attempted": total_attempted,
            "success_rate": total_sent / total_attempted if total_attempted > 0 else 0,
            "rate_limits": rate_stats,
            "quiet_hours_active": self._is_quiet_hours(),
            "daily_limit_ok": self._check_daily_limit(),
        }

    def update_user_preferences(self, preferences: Dict[str, Any]):
        """Update user preferences for notifications."""
        self.user_preferences.update(preferences)
        logger.info("User preferences updated")

    def start_background_tasks(self):
        """Start background tasks for maintenance."""
        if self.cleanup_task is None:
            self.cleanup_task = asyncio.create_task(self._periodic_cleanup())

    def stop_background_tasks(self):
        """Stop background tasks."""
        if self.cleanup_task:
            self.cleanup_task.cancel()
            self.cleanup_task = None

    async def _periodic_cleanup(self):
        """Periodic cleanup of old notification history."""
        while True:
            try:
                # Clean up old notifications (older than 30 days)
                cutoff_time = time.time() - (30 * 24 * 60 * 60)
                self.notification_history = [
                    result
                    for result in self.notification_history
                    if result.timestamp > cutoff_time
                ]

                # Clean up rate limiter history
                for limiter in self.rate_limiters.values():
                    current_time = time.time()
                    limiter.notifications = [
                        ts
                        for ts in limiter.notifications
                        if current_time - ts < limiter.window_seconds
                    ]

                await asyncio.sleep(3600)  # Clean up every hour

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in periodic cleanup: {e}")
                await asyncio.sleep(60)  # Retry after 1 minute


# Global instance
proactivity_manager = ProactivityManager()


# Factory function
def create_proactivity_manager() -> ProactivityManager:
    """Create a new ProactivityManager instance."""
    return ProactivityManager()
