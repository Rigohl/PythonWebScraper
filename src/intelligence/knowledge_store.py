import sqlite3
import os
import time
from typing import List, Dict, Any, Optional, Tuple

SCHEMA = {
    'facts': '''CREATE TABLE IF NOT EXISTS facts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT,
        subject TEXT,
        predicate TEXT,
        obj TEXT,
        confidence REAL,
        source TEXT,
        created_at REAL
    )''',
    'relations': '''CREATE TABLE IF NOT EXISTS relations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        from_fact INTEGER,
        to_fact INTEGER,
        relation_type TEXT,
        weight REAL,
        created_at REAL,
        FOREIGN KEY(from_fact) REFERENCES facts(id),
        FOREIGN KEY(to_fact) REFERENCES facts(id)
    )''',
    'code_metrics': '''CREATE TABLE IF NOT EXISTS code_metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_path TEXT,
        lines INTEGER,
        functions INTEGER,
        classes INTEGER,
        avg_function_length REAL,
        complexity REAL,
        imports INTEGER,
        scanned_at REAL
    )''',
    'strategies': '''CREATE TABLE IF NOT EXISTS strategies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        goal TEXT,
        confidence REAL,
        steps TEXT,
        meta TEXT,
        created_at REAL
    )''',
    'improvements': '''CREATE TABLE IF NOT EXISTS improvements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_path TEXT,
        issue_type TEXT,
        description TEXT,
        severity TEXT,
        score REAL,
        suggestion TEXT,
        created_at REAL
    )''',
    'patch_proposals': '''CREATE TABLE IF NOT EXISTS patch_proposals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        improvement_id INTEGER,
        file_path TEXT,
        proposed_patch TEXT,
        risk_level TEXT,
        estimated_impact TEXT,
        created_at REAL,
        FOREIGN KEY(improvement_id) REFERENCES improvements(id)
    )''',
    'programming_knowledge': '''CREATE TABLE IF NOT EXISTS programming_knowledge (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT,
        topic TEXT,
        content TEXT,
        confidence REAL,
        source TEXT,
        created_at REAL
    )'''
}

class KnowledgeStore:
    """SQLite-based structured knowledge repository for the brain."""

    def __init__(self, db_path: str = "data/brain_knowledge.db"):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self._init_db()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._connect() as conn:
            cur = conn.cursor()
            for ddl in SCHEMA.values():
                cur.execute(ddl)
            conn.commit()

    # ------------------------ Fact Storage ------------------------
    def add_fact(self, category: str, subject: str, predicate: str, obj: str, confidence: float = 0.7, source: str = "system") -> int:
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO facts(category,subject,predicate,obj,confidence,source,created_at) VALUES (?,?,?,?,?,?,?)",
                        (category, subject, predicate, obj, confidence, source, time.time()))
            conn.commit()
            return cur.lastrowid

    def query_facts(self, subject: Optional[str] = None, predicate: Optional[str] = None, category: Optional[str] = None) -> List[Dict[str, Any]]:
        clauses = []
        params: List[Any] = []
        if subject:
            clauses.append("subject=?")
            params.append(subject)
        if predicate:
            clauses.append("predicate=?")
            params.append(predicate)
        if category:
            clauses.append("category=?")
            params.append(category)
        where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
        sql = f"SELECT id,category,subject,predicate,obj,confidence,source,created_at FROM facts {where} ORDER BY created_at DESC LIMIT 100"
        with self._connect() as conn:
            cur = conn.cursor()
            rows = cur.execute(sql, params).fetchall()
        return [
            {
                'id': r[0], 'category': r[1], 'subject': r[2], 'predicate': r[3], 'object': r[4],
                'confidence': r[5], 'source': r[6], 'created_at': r[7]
            } for r in rows
        ]

    # ------------------------ Code Metrics ------------------------
    def add_code_metrics(self, file_path: str, lines: int, functions: int, classes: int, avg_func_len: float, complexity: float, imports: int):
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO code_metrics(file_path,lines,functions,classes,avg_function_length,complexity,imports,scanned_at) VALUES (?,?,?,?,?,?,?,?)",
                        (file_path, lines, functions, classes, avg_func_len, complexity, imports, time.time()))
            conn.commit()

    def recent_code_metrics(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            cur = conn.cursor()
            rows = cur.execute("SELECT file_path,lines,functions,classes,avg_function_length,complexity,imports,scanned_at FROM code_metrics ORDER BY scanned_at DESC LIMIT ?", (limit,)).fetchall()
        return [
            {
                'file_path': r[0], 'lines': r[1], 'functions': r[2], 'classes': r[3], 'avg_function_length': r[4],
                'complexity': r[5], 'imports': r[6], 'scanned_at': r[7]
            } for r in rows
        ]

    # ------------------------ Strategies ------------------------
    def add_strategy(self, goal: str, confidence: float, steps: List[str], meta: Dict[str, Any]):
        import json
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO strategies(goal,confidence,steps,meta,created_at) VALUES (?,?,?,?,?)",
                        (goal, confidence, json.dumps(steps), json.dumps(meta), time.time()))
            conn.commit()

    def recent_strategies(self, limit: int = 20) -> List[Dict[str, Any]]:
        import json
        with self._connect() as conn:
            cur = conn.cursor()
            rows = cur.execute("SELECT goal,confidence,steps,meta,created_at FROM strategies ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
        return [
            {
                'goal': r[0], 'confidence': r[1], 'steps': json.loads(r[2]), 'meta': json.loads(r[3]), 'created_at': r[4]
            } for r in rows
        ]

    # ------------------------ Improvements ------------------------
    def add_improvement_suggestion(self, file_path: str, issue_type: str, description: str, severity: str, score: float, suggestion: str):
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO improvements(file_path,issue_type,description,severity,score,suggestion,created_at) VALUES (?,?,?,?,?,?,?)",
                        (file_path, issue_type, description, severity, score, suggestion, time.time()))
            conn.commit()

    def recent_improvements(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            cur = conn.cursor()
            rows = cur.execute("SELECT file_path,issue_type,description,severity,score,suggestion,created_at FROM improvements ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
        return [
            {
                'file_path': r[0], 'issue_type': r[1], 'description': r[2], 'severity': r[3], 'score': r[4], 'suggestion': r[5], 'created_at': r[6]
            } for r in rows
        ]

    # ------------------------ Patch Proposals ------------------------
    def add_patch_proposal(self, improvement_id: int, file_path: str, proposed_patch: str, risk_level: str, estimated_impact: str):
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO patch_proposals(improvement_id,file_path,proposed_patch,risk_level,estimated_impact,created_at) VALUES (?,?,?,?,?,?)",
                        (improvement_id, file_path, proposed_patch, risk_level, estimated_impact, time.time()))
            conn.commit()

    def recent_patch_proposals(self, limit: int = 20) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            cur = conn.cursor()
            rows = cur.execute("SELECT improvement_id,file_path,proposed_patch,risk_level,estimated_impact,created_at FROM patch_proposals ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
        return [
            {
                'improvement_id': r[0], 'file_path': r[1], 'proposed_patch': r[2], 'risk_level': r[3], 'estimated_impact': r[4], 'created_at': r[5]
            } for r in rows
        ]

    # ------------------------ Programming Knowledge ------------------------
    def add_programming_knowledge(self, category: str, topic: str, content: str, confidence: float = 0.8, source: str = "system"):
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO programming_knowledge(category,topic,content,confidence,source,created_at) VALUES (?,?,?,?,?,?)",
                        (category, topic, content, confidence, source, time.time()))
            conn.commit()

    def query_programming_knowledge(self, category: Optional[str] = None, topic: Optional[str] = None) -> List[Dict[str, Any]]:
        clauses = []
        params: List[Any] = []
        if category:
            clauses.append("category=?")
            params.append(category)
        if topic:
            clauses.append("topic LIKE ?")
            params.append(f"%{topic}%")
        where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
        sql = f"SELECT category,topic,content,confidence,source,created_at FROM programming_knowledge {where} ORDER BY confidence DESC, created_at DESC LIMIT 100"
        with self._connect() as conn:
            cur = conn.cursor()
            rows = cur.execute(sql, params).fetchall()
        return [
            {
                'category': r[0], 'topic': r[1], 'content': r[2], 'confidence': r[3], 'source': r[4], 'created_at': r[5]
            } for r in rows
        ]

    def seed_programming_knowledge(self):
        """Seed comprehensive programming knowledge base with specialized domains"""
        knowledge_items = [
            # ======================== WEB SCRAPING MASTERY ========================
            ("web_scraping", "rate_limiting", "Always implement rate limiting between requests to avoid being blocked. Use delays of 1-3 seconds between requests.", 0.9, "best_practices"),
            ("web_scraping", "user_agents", "Rotate user agents to appear more human-like. Use realistic browser user agent strings.", 0.8, "best_practices"),
            ("web_scraping", "session_management", "Use session objects to maintain cookies and connection pooling for better performance.", 0.9, "best_practices"),
            ("web_scraping", "error_handling", "Implement comprehensive error handling for network timeouts, HTTP errors, and parsing failures.", 0.9, "best_practices"),
            ("web_scraping", "data_validation", "Always validate scraped data before storing. Check for expected data types and formats.", 0.8, "best_practices"),
            ("web_scraping", "proxy_rotation", "Use rotating proxies to distribute requests and avoid IP-based blocking.", 0.8, "advanced"),
            ("web_scraping", "captcha_handling", "Implement CAPTCHA detection and handling strategies, including human solver integration.", 0.7, "advanced"),
            ("web_scraping", "javascript_rendering", "Use headless browsers like Selenium, Playwright, or Puppeteer for JS-heavy sites.", 0.9, "advanced"),
            ("web_scraping", "anti_detection", "Mimic human behavior with random delays, mouse movements, and realistic browsing patterns.", 0.8, "stealth"),

            # ======================== PYTHON MASTERY ========================
            ("python", "exception_handling", "Use specific exception types rather than bare except clauses. Handle exceptions at the appropriate level.", 0.9, "patterns"),
            ("python", "logging", "Use structured logging with appropriate levels (DEBUG, INFO, WARNING, ERROR, CRITICAL).", 0.8, "patterns"),
            ("python", "type_hints", "Use type hints for better code documentation and IDE support. Import from typing module.", 0.7, "patterns"),
            ("python", "context_managers", "Use context managers (with statements) for resource management like files and database connections.", 0.9, "patterns"),
            ("python", "list_comprehensions", "Use list comprehensions for simple transformations, but prefer regular loops for complex logic.", 0.7, "patterns"),
            ("python", "async_programming", "Use asyncio for I/O-bound operations. async/await syntax for coroutines, aiohttp for async HTTP.", 0.8, "async"),
            ("python", "decorators", "Use decorators for cross-cutting concerns like timing, caching, authentication, and retry logic.", 0.8, "patterns"),
            ("python", "generators", "Use generators for memory-efficient iteration over large datasets. yield for lazy evaluation.", 0.8, "memory"),
            ("python", "dataclasses", "Use dataclasses for simple data containers. @dataclass decorator reduces boilerplate code.", 0.7, "modern"),
            ("python", "pathlib", "Use pathlib.Path instead of os.path for more readable and cross-platform file operations.", 0.8, "modern"),

            # ======================== JAVASCRIPT MASTERY ========================
            ("javascript", "promises_async", "Use async/await for asynchronous operations. Promise.all() for concurrent operations.", 0.9, "async"),
            ("javascript", "event_loop", "Understand the event loop: call stack, callback queue, microtask queue. Avoid blocking operations.", 0.9, "fundamentals"),
            ("javascript", "closures", "Master closures for data privacy and function factories. Understand lexical scoping.", 0.8, "fundamentals"),
            ("javascript", "dom_manipulation", "Use modern DOM APIs: querySelector, addEventListener, classList for efficient manipulation.", 0.8, "frontend"),
            ("javascript", "fetch_api", "Use fetch() for HTTP requests. Handle promises properly with .then()/.catch() or async/await.", 0.9, "api"),
            ("javascript", "module_system", "Use ES6 modules: import/export for code organization. Understand default vs named exports.", 0.8, "modules"),
            ("javascript", "arrow_functions", "Use arrow functions for concise syntax, but understand 'this' binding differences.", 0.7, "syntax"),
            ("javascript", "destructuring", "Use destructuring assignment for objects and arrays to extract values elegantly.", 0.7, "syntax"),
            ("javascript", "template_literals", "Use template literals with ${} for string interpolation instead of concatenation.", 0.8, "syntax"),
            ("javascript", "error_handling", "Use try/catch for synchronous code, .catch() for promises, and proper error propagation.", 0.9, "error_handling"),

            # ======================== BOT DEVELOPMENT ========================
            ("bot_development", "bot_framework", "Choose appropriate framework: discord.py for Discord, python-telegram-bot for Telegram, selenium for web bots.", 0.9, "frameworks"),
            ("bot_development", "rate_limiting", "Implement proper rate limiting to respect API limits. Use exponential backoff for retries.", 0.9, "api_management"),
            ("bot_development", "state_management", "Use databases or memory stores to maintain bot state between interactions.", 0.8, "state"),
            ("bot_development", "command_parsing", "Implement robust command parsing with argument validation and help systems.", 0.8, "parsing"),
            ("bot_development", "webhook_vs_polling", "Use webhooks for production bots for better performance, polling for development.", 0.8, "architecture"),
            ("bot_development", "error_recovery", "Implement graceful error recovery with logging, user notifications, and automatic restart.", 0.9, "reliability"),
            ("bot_development", "authentication", "Secure bot tokens and API keys. Use environment variables, never hardcode secrets.", 0.9, "security"),
            ("bot_development", "natural_language", "Use NLP libraries like spaCy, NLTK, or cloud APIs for intent recognition.", 0.7, "ai"),
            ("bot_development", "conversation_flow", "Design conversation flows with state machines for complex multi-step interactions.", 0.8, "design"),
            ("bot_development", "testing", "Test bots with mock APIs and automated conversation flows. Unit test command handlers.", 0.8, "testing"),

            # ======================== UI/UX DESIGN PRINCIPLES ========================
            ("uiux", "design_principles", "Follow design principles: contrast, repetition, alignment, proximity (CRAP). Consistent visual hierarchy.", 0.9, "principles"),
            ("uiux", "user_research", "Conduct user research: interviews, surveys, usability testing to understand user needs.", 0.9, "research"),
            ("uiux", "wireframing", "Create wireframes before high-fidelity designs. Focus on information architecture and user flow.", 0.8, "process"),
            ("uiux", "prototyping", "Build interactive prototypes with tools like Figma, Adobe XD, or code for user testing.", 0.8, "prototyping"),
            ("uiux", "accessibility", "Design for accessibility: WCAG guidelines, keyboard navigation, screen reader compatibility.", 0.9, "accessibility"),
            ("uiux", "responsive_design", "Design mobile-first with flexible grids, fluid images, and media queries for all screen sizes.", 0.9, "responsive"),
            ("uiux", "color_theory", "Understand color psychology, contrast ratios, color blindness considerations in design.", 0.8, "visual"),
            ("uiux", "typography", "Choose readable fonts, establish type hierarchy, consider line height and letter spacing.", 0.8, "visual"),
            ("uiux", "user_testing", "Conduct regular user testing sessions. Observe behavior, gather feedback, iterate designs.", 0.9, "validation"),
            ("uiux", "information_architecture", "Organize content logically with clear navigation patterns and intuitive site structure.", 0.8, "architecture"),

            # ======================== DATABASE EXCELLENCE ========================
            ("database", "connection_pooling", "Use connection pooling to efficiently manage database connections in multi-threaded applications.", 0.9, "patterns"),
            ("database", "prepared_statements", "Use parameterized queries to prevent SQL injection attacks.", 0.9, "security"),
            ("database", "indexing_strategy", "Create indexes on frequently queried columns. Understand B-tree, hash, and full-text indexes.", 0.9, "performance"),
            ("database", "normalization", "Normalize databases to reduce redundancy, but denormalize for read-heavy workloads.", 0.8, "design"),
            ("database", "transaction_management", "Use transactions for data consistency. Understand ACID properties and isolation levels.", 0.9, "consistency"),
            ("database", "query_optimization", "Analyze query execution plans. Use EXPLAIN to identify bottlenecks and optimize queries.", 0.8, "performance"),
            ("database", "backup_strategies", "Implement automated backups with point-in-time recovery. Test restore procedures regularly.", 0.9, "reliability"),
            ("database", "migration_patterns", "Use database migrations for schema changes. Version control database schema changes.", 0.8, "versioning"),

            # ======================== API DEVELOPMENT ========================
            ("api_development", "rest_principles", "Follow REST principles: stateless, cacheable, uniform interface, layered system.", 0.9, "architecture"),
            ("api_development", "http_status_codes", "Use appropriate HTTP status codes: 200 success, 400 client error, 500 server error.", 0.9, "standards"),
            ("api_development", "authentication", "Implement secure authentication: JWT tokens, OAuth2, API keys with proper expiration.", 0.9, "security"),
            ("api_development", "rate_limiting", "Implement API rate limiting to prevent abuse. Use sliding window or token bucket algorithms.", 0.8, "protection"),
            ("api_development", "versioning", "Version APIs with URL versioning (/v1/), header versioning, or parameter versioning.", 0.8, "versioning"),
            ("api_development", "documentation", "Document APIs with OpenAPI/Swagger. Include examples, error codes, and authentication details.", 0.9, "documentation"),
            ("api_development", "error_handling", "Return consistent error responses with error codes, messages, and debugging information.", 0.9, "error_handling"),
            ("api_development", "caching", "Implement caching strategies: ETags, Cache-Control headers, Redis for distributed caching.", 0.8, "performance"),

            # ======================== SECURITY BEST PRACTICES ========================
            ("security", "input_validation", "Validate and sanitize all user inputs. Use whitelist validation over blacklist.", 0.9, "input"),
            ("security", "authentication", "Use strong password policies, multi-factor authentication, and secure session management.", 0.9, "auth"),
            ("security", "encryption", "Use HTTPS everywhere. Encrypt sensitive data at rest with AES-256, bcrypt for passwords.", 0.9, "encryption"),
            ("security", "sql_injection", "Prevent SQL injection with parameterized queries, stored procedures, and input validation.", 0.9, "injection"),
            ("security", "xss_prevention", "Prevent XSS attacks with output encoding, CSP headers, and input sanitization.", 0.9, "xss"),
            ("security", "csrf_protection", "Implement CSRF tokens for state-changing operations. Use SameSite cookie attributes.", 0.8, "csrf"),
            ("security", "secrets_management", "Store secrets securely using environment variables, key vaults, or secret management services.", 0.9, "secrets"),
            ("security", "security_headers", "Use security headers: HSTS, X-Frame-Options, X-Content-Type-Options, CSP.", 0.8, "headers"),

            # ======================== PERFORMANCE OPTIMIZATION ========================
            ("performance", "profiling", "Profile applications to identify bottlenecks. Use cProfile, line_profiler, memory_profiler.", 0.9, "profiling"),
            ("performance", "caching_strategies", "Implement multi-level caching: browser cache, CDN, application cache, database cache.", 0.9, "caching"),
            ("performance", "lazy_loading", "Use lazy loading for images, modules, and data to improve initial load times.", 0.8, "loading"),
            ("performance", "database_optimization", "Optimize database queries, use proper indexing, and implement connection pooling.", 0.9, "database"),
            ("performance", "compression", "Use compression: gzip for HTTP responses, image optimization, minification for assets.", 0.8, "compression"),
            ("performance", "cdn_usage", "Use Content Delivery Networks for static assets to reduce latency and server load.", 0.8, "infrastructure"),
            ("performance", "async_processing", "Use asynchronous processing for I/O-bound operations to improve throughput.", 0.8, "async"),

            # ======================== CODE QUALITY ========================
            ("code_quality", "clean_code", "Write self-documenting code with meaningful names, small functions, and clear intent.", 0.9, "principles"),
            ("code_quality", "testing", "Write comprehensive tests: unit tests, integration tests, end-to-end tests.", 0.9, "testing"),
            ("code_quality", "code_review", "Conduct thorough code reviews focusing on logic, security, performance, and maintainability.", 0.9, "review"),
            ("code_quality", "refactoring", "Regularly refactor code to improve structure while maintaining functionality.", 0.8, "maintenance"),
            ("code_quality", "documentation", "Document code with clear comments, docstrings, and architectural decision records.", 0.8, "documentation"),
            ("code_quality", "version_control", "Use Git effectively: meaningful commits, branching strategies, pull requests.", 0.9, "git"),
            ("database", "indexing", "Create indexes on frequently queried columns to improve performance.", 0.8, "performance"),
            ("database", "transactions", "Use database transactions for operations that must be atomic.", 0.9, "patterns"),

            # Performance Optimization
            ("performance", "caching", "Implement caching strategies for frequently accessed data to reduce database load.", 0.8, "optimization"),
            ("performance", "async_programming", "Use async/await for I/O bound operations to improve concurrency.", 0.7, "optimization"),
            ("performance", "memory_management", "Be mindful of memory usage when processing large datasets. Use generators for large data streams.", 0.8, "optimization"),

            # Security Best Practices
            ("security", "input_validation", "Always validate and sanitize user input to prevent injection attacks.", 0.9, "security"),
            ("security", "authentication", "Implement proper authentication and authorization mechanisms.", 0.9, "security"),
            ("security", "secrets_management", "Never hard-code secrets in source code. Use environment variables or secure vaults.", 0.9, "security"),

            # Code Quality
            ("code_quality", "single_responsibility", "Each function should have a single, well-defined responsibility.", 0.8, "principles"),
            ("code_quality", "documentation", "Write clear docstrings and comments explaining the why, not just the what.", 0.7, "principles"),
            ("code_quality", "testing", "Write unit tests for critical functions. Aim for good test coverage.", 0.8, "principles"),
            ("code_quality", "refactoring", "Regularly refactor code to improve readability and maintainability.", 0.7, "principles"),
        ]

        existing_count = 0
        with self._connect() as conn:
            cur = conn.cursor()
            existing_count = cur.execute("SELECT COUNT(*) FROM programming_knowledge").fetchone()[0]

        if existing_count == 0:
            for category, topic, content, confidence, source in knowledge_items:
                self.add_programming_knowledge(category, topic, content, confidence, source)
            return len(knowledge_items)
        return 0

    # ------------------------ Utility ------------------------
    def stats(self) -> Dict[str, Any]:
        with self._connect() as conn:
            cur = conn.cursor()
            counts = {}
            for table in SCHEMA.keys():
                try:
                    counts[table] = cur.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                except Exception:
                    counts[table] = 0
        return counts

    def get_knowledge_summary(self) -> Dict[str, Any]:
        """Get comprehensive knowledge summary for the brain"""
        stats = self.stats()

        # Get programming knowledge categories
        prog_categories = {}
        try:
            with self._connect() as conn:
                cur = conn.cursor()
                rows = cur.execute("SELECT category, COUNT(*) FROM programming_knowledge GROUP BY category").fetchall()
                prog_categories = {r[0]: r[1] for r in rows}
        except Exception:
            pass

        # Get recent strategies
        recent_strategies = self.recent_strategies(5)

        # Get domain success rates from facts
        domain_performance = {}
        try:
            with self._connect() as conn:
                cur = conn.cursor()
                rows = cur.execute("""
                    SELECT subject, obj, COUNT(*)
                    FROM facts
                    WHERE category='scrape_event' AND predicate='event_result'
                    GROUP BY subject, obj
                """).fetchall()
                for domain, result, count in rows:
                    if domain not in domain_performance:
                        domain_performance[domain] = {'success': 0, 'failure': 0}
                    domain_performance[domain][result] = count
        except Exception:
            pass

        return {
            'total_facts': stats.get('facts', 0),
            'programming_knowledge': {
                'total': stats.get('programming_knowledge', 0),
                'categories': prog_categories
            },
            'strategies': {
                'total': stats.get('strategies', 0),
                'recent': [s['goal'] for s in recent_strategies]
            },
            'improvements': stats.get('improvements', 0),
            'patch_proposals': stats.get('patch_proposals', 0),
            'domain_performance': domain_performance
        }
