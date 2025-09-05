"""
Brain Persistence Layer - Dual Storage System
==============================================

Provides robust persistence using SQLite for structured data and JSON for configuration.
Handles atomic operations, concurrency, and migrations.

Features:
- SQLite for events, domain stats, and metrics
- JSON for configuration and metadata
- Atomic transactions
- Thread-safe operations
- Automatic migrations
- Backup and recovery
"""

import json
import logging
import sqlite3
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

class BrainPersistence:
    """Dual persistence layer for Brain system using SQLite + JSON."""

    def __init__(self, db_path: str = "data/brain.db", config_path: str = "data/brain_config.json"):
        self.db_path = Path(db_path)
        self.config_path = Path(config_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self.config_path.parent.mkdir(exist_ok=True)

        # Thread safety
        self._lock = threading.RLock()
        self._connection: Optional[sqlite3.Connection] = None

        # Schema version for migrations
        self.schema_version = 1

        # Initialize storage
        self._init_database()
        self._load_config()

    def _init_database(self) -> None:
        """Initialize SQLite database with schema."""
        with self._lock:
            self._connection = sqlite3.connect(str(self.db_path), check_same_thread=False)
            self._connection.row_factory = sqlite3.Row

            # Create tables
            self._create_tables()

            # Run migrations if needed
            self._run_migrations()

    def _create_tables(self) -> None:
        """Create database tables."""
        with self._connection:
            # Events table
            self._connection.execute('''
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL,
                    status TEXT NOT NULL,
                    response_time REAL,
                    content_length INTEGER,
                    new_links INTEGER,
                    timestamp TEXT NOT NULL,
                    domain TEXT,
                    extracted_fields INTEGER,
                    error_type TEXT,
                    created_at REAL DEFAULT (strftime('%s', 'now'))
                )
            ''')

            # Domain stats table
            self._connection.execute('''
                CREATE TABLE IF NOT EXISTS domain_stats (
                    domain TEXT PRIMARY KEY,
                    visits INTEGER DEFAULT 0,
                    success INTEGER DEFAULT 0,
                    errors INTEGER DEFAULT 0,
                    duplicates INTEGER DEFAULT 0,
                    total_new_links INTEGER DEFAULT 0,
                    total_content_length INTEGER DEFAULT 0,
                    extractions INTEGER DEFAULT 0,
                    response_time_sum REAL DEFAULT 0.0,
                    updated_at REAL DEFAULT (strftime('%s', 'now'))
                )
            ''')

            # Error frequency table
            self._connection.execute('''
                CREATE TABLE IF NOT EXISTS error_freq (
                    error_type TEXT PRIMARY KEY,
                    count INTEGER DEFAULT 0,
                    updated_at REAL DEFAULT (strftime('%s', 'now'))
                )
            ''')

            # Schema version table
            self._connection.execute('''
                CREATE TABLE IF NOT EXISTS schema_version (
                    version INTEGER PRIMARY KEY,
                    migrated_at REAL DEFAULT (strftime('%s', 'now'))
                )
            ''')

            # Insert initial schema version if not exists
            self._connection.execute('''
                INSERT OR IGNORE INTO schema_version (version) VALUES (1)
            ''')

    def _run_migrations(self) -> None:
        """Run database migrations."""
        current_version = self._get_schema_version()

        # Migration logic can be added here as needed
        if current_version < self.schema_version:
            logger.info(f"Running migrations from v{current_version} to v{self.schema_version}")
            # Add migration logic here
            self._update_schema_version(self.schema_version)

    def _get_schema_version(self) -> int:
        """Get current schema version."""
        cursor = self._connection.execute('SELECT MAX(version) FROM schema_version')
        result = cursor.fetchone()
        return result[0] if result and result[0] else 0

    def _update_schema_version(self, version: int) -> None:
        """Update schema version."""
        self._connection.execute('INSERT INTO schema_version (version) VALUES (?)', (version,))

    def _load_config(self) -> None:
        """Load JSON configuration."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
            except Exception as e:
                logger.warning(f"Could not load config: {e}")
                self._config = {}
        else:
            self._config = {}

    def _save_config(self) -> None:
        """Save JSON configuration."""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Could not save config: {e}")

    # Public API Methods

    def save_event(self, event_data: Dict[str, Any]) -> None:
        """Save a single event to database."""
        with self._lock:
            with self._connection:
                self._connection.execute('''
                    INSERT INTO events
                    (url, status, response_time, content_length, new_links,
                     timestamp, domain, extracted_fields, error_type)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    event_data.get('url'),
                    event_data.get('status'),
                    event_data.get('response_time'),
                    event_data.get('content_length'),
                    event_data.get('new_links'),
                    event_data.get('timestamp'),
                    event_data.get('domain'),
                    event_data.get('extracted_fields'),
                    event_data.get('error_type')
                ))

    def save_events_batch(self, events: List[Dict[str, Any]]) -> None:
        """Save multiple events in a single transaction."""
        with self._lock:
            with self._connection:
                self._connection.executemany('''
                    INSERT INTO events
                    (url, status, response_time, content_length, new_links,
                     timestamp, domain, extracted_fields, error_type)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', [(
                    e.get('url'), e.get('status'), e.get('response_time'),
                    e.get('content_length'), e.get('new_links'), e.get('timestamp'),
                    e.get('domain'), e.get('extracted_fields'), e.get('error_type')
                ) for e in events])

    def update_domain_stats(self, domain: str, stats: Dict[str, Any]) -> None:
        """Update domain statistics."""
        with self._lock:
            with self._connection:
                self._connection.execute('''
                    INSERT OR REPLACE INTO domain_stats
                    (domain, visits, success, errors, duplicates, total_new_links,
                     total_content_length, extractions, response_time_sum, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, strftime('%s', 'now'))
                ''', (
                    domain,
                    stats.get('visits', 0),
                    stats.get('success', 0),
                    stats.get('errors', 0),
                    stats.get('duplicates', 0),
                    stats.get('total_new_links', 0),
                    stats.get('total_content_length', 0),
                    stats.get('extractions', 0),
                    stats.get('response_time_sum', 0.0)
                ))

    def update_error_freq(self, error_type: str, count: int) -> None:
        """Update error frequency."""
        with self._lock:
            with self._connection:
                self._connection.execute('''
                    INSERT OR REPLACE INTO error_freq
                    (error_type, count, updated_at)
                    VALUES (?, ?, strftime('%s', 'now'))
                ''', (error_type, count))

    def load_recent_events(self, limit: int = 500) -> List[Dict[str, Any]]:
        """Load recent events from database."""
        with self._lock:
            cursor = self._connection.execute('''
                SELECT * FROM events
                ORDER BY created_at DESC
                LIMIT ?
            ''', (limit,))

            return [dict(row) for row in cursor.fetchall()]

    def load_domain_stats(self) -> Dict[str, Dict[str, Any]]:
        """Load all domain statistics."""
        with self._lock:
            cursor = self._connection.execute('SELECT * FROM domain_stats')
            stats = {}
            for row in cursor.fetchall():
                domain = row['domain']
                stats[domain] = dict(row)
            return stats

    def load_error_freq(self) -> Dict[str, int]:
        """Load error frequencies."""
        with self._lock:
            cursor = self._connection.execute('SELECT error_type, count FROM error_freq')
            return {row['error_type']: row['count'] for row in cursor.fetchall()}

    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self._config.get(key, default)

    def set_config(self, key: str, value: Any) -> None:
        """Set configuration value."""
        self._config[key] = value
        self._save_config()

    def cleanup_old_events(self, days: int = 30) -> int:
        """Clean up old events to prevent database bloat."""
        with self._lock:
            with self._connection:
                cursor = self._connection.execute('''
                    DELETE FROM events
                    WHERE created_at < strftime('%s', 'now', '-{} days')
                '''.format(days))
                return cursor.rowcount

    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        with self._lock:
            stats = {}

            # Event count
            cursor = self._connection.execute('SELECT COUNT(*) FROM events')
            stats['total_events'] = cursor.fetchone()[0]

            # Domain count
            cursor = self._connection.execute('SELECT COUNT(*) FROM domain_stats')
            stats['total_domains'] = cursor.fetchone()[0]

            # Database size
            if self.db_path.exists():
                stats['db_size_bytes'] = self.db_path.stat().st_size

            # Recent activity
            cursor = self._connection.execute('''
                SELECT COUNT(*) FROM events
                WHERE created_at > strftime('%s', 'now', '-1 day')
            ''')
            stats['events_last_24h'] = cursor.fetchone()[0]

            return stats

    def backup(self, backup_path: Optional[str] = None) -> str:
        """Create database backup."""
        if backup_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"data/brain_backup_{timestamp}.db"

        with self._lock:
            # Close current connection for backup
            if self._connection:
                self._connection.close()
                self._connection = None

            # Copy file
            import shutil
            shutil.copy2(str(self.db_path), backup_path)

            # Reopen connection
            self._init_database()

        return backup_path

    def close(self) -> None:
        """Close database connection."""
        with self._lock:
            if self._connection:
                self._connection.close()
                self._connection = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
