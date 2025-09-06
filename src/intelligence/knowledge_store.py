import os
import sqlite3
import time
from typing import Any, Dict, List, Optional

SCHEMA = {
    "facts": """CREATE TABLE IF NOT EXISTS facts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT,
        subject TEXT,
        predicate TEXT,
        obj TEXT,
        confidence REAL,
        source TEXT,
        created_at REAL
    )""",
    "relations": """CREATE TABLE IF NOT EXISTS relations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        from_fact INTEGER,
        to_fact INTEGER,
        relation_type TEXT,
        weight REAL,
        created_at REAL,
        FOREIGN KEY(from_fact) REFERENCES facts(id),
        FOREIGN KEY(to_fact) REFERENCES facts(id)
    )""",
    "code_metrics": """CREATE TABLE IF NOT EXISTS code_metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_path TEXT,
        lines INTEGER,
        functions INTEGER,
        classes INTEGER,
        avg_function_length REAL,
        complexity REAL,
        imports INTEGER,
        scanned_at REAL
    )""",
    "strategies": """CREATE TABLE IF NOT EXISTS strategies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        goal TEXT,
        confidence REAL,
        steps TEXT,
        meta TEXT,
        created_at REAL
    )""",
    "improvements": """CREATE TABLE IF NOT EXISTS improvements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_path TEXT,
        issue_type TEXT,
        description TEXT,
        severity TEXT,
        score REAL,
        suggestion TEXT,
        created_at REAL
    )""",
    "patch_proposals": """CREATE TABLE IF NOT EXISTS patch_proposals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        improvement_id INTEGER,
        file_path TEXT,
        proposed_patch TEXT,
        risk_level TEXT,
        estimated_impact TEXT,
        created_at REAL,
        FOREIGN KEY(improvement_id) REFERENCES improvements(id)
    )""",
    "programming_knowledge": """CREATE TABLE IF NOT EXISTS programming_knowledge (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT,
        topic TEXT,
        content TEXT,
        confidence REAL,
        source TEXT,
        created_at REAL,
        domain TEXT,
        priority INTEGER,
        tags TEXT,
        related_concepts TEXT
    )""",
    "knowledge_relationships": """CREATE TABLE IF NOT EXISTS knowledge_relationships (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_knowledge_id INTEGER,
        target_knowledge_id INTEGER,
        relationship_type TEXT,
        strength REAL,
        created_at REAL,
        FOREIGN KEY(source_knowledge_id) REFERENCES programming_knowledge(id),
        FOREIGN KEY(target_knowledge_id) REFERENCES programming_knowledge(id)
    )""",
    "data_sources": """CREATE TABLE IF NOT EXISTS data_sources (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        url TEXT,
        source_type TEXT,
        access_method TEXT,
        credentials_needed BOOLEAN,
        last_accessed REAL,
        success_rate REAL,
        notes TEXT,
        created_at REAL
    )""",
    "scraping_targets": """CREATE TABLE IF NOT EXISTS scraping_targets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        domain TEXT,
        url_pattern TEXT,
        content_type TEXT,
        extraction_rules TEXT,
        anti_detection_level INTEGER,
        success_rate REAL,
        last_scraped REAL,
        metadata TEXT,
        created_at REAL
    )""",
    "learned_patterns": """CREATE TABLE IF NOT EXISTS learned_patterns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pattern_type TEXT,
        pattern_data TEXT,
        confidence REAL,
        usage_count INTEGER,
        success_rate REAL,
        domain TEXT,
        context TEXT,
        created_at REAL
    )""",
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
    def add_fact(
        self,
        category: str,
        subject: str,
        predicate: str,
        obj: str,
        confidence: float = 0.7,
        source: str = "system",
    ) -> int:
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO facts(category,subject,predicate,obj,confidence,source,created_at) VALUES (?,?,?,?,?,?,?)",
                (category, subject, predicate, obj, confidence, source, time.time()),
            )
            conn.commit()
            return cur.lastrowid

    def query_facts(
        self,
        subject: Optional[str] = None,
        predicate: Optional[str] = None,
        category: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
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
                "id": r[0],
                "category": r[1],
                "subject": r[2],
                "predicate": r[3],
                "object": r[4],
                "confidence": r[5],
                "source": r[6],
                "created_at": r[7],
            }
            for r in rows
        ]

    # ------------------------ Code Metrics ------------------------
    def add_code_metrics(
        self,
        file_path: str,
        lines: int,
        functions: int,
        classes: int,
        avg_func_len: float,
        complexity: float,
        imports: int,
    ):
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO code_metrics(file_path,lines,functions,classes,avg_function_length,complexity,imports,scanned_at) VALUES (?,?,?,?,?,?,?,?)",
                (
                    file_path,
                    lines,
                    functions,
                    classes,
                    avg_func_len,
                    complexity,
                    imports,
                    time.time(),
                ),
            )
            conn.commit()

    def recent_code_metrics(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            cur = conn.cursor()
            rows = cur.execute(
                "SELECT file_path,lines,functions,classes,avg_function_length,complexity,imports,scanned_at FROM code_metrics ORDER BY scanned_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [
            {
                "file_path": r[0],
                "lines": r[1],
                "functions": r[2],
                "classes": r[3],
                "avg_function_length": r[4],
                "complexity": r[5],
                "imports": r[6],
                "scanned_at": r[7],
            }
            for r in rows
        ]

    # ------------------------ Strategies ------------------------
    def add_strategy(
        self, goal: str, confidence: float, steps: List[str], meta: Dict[str, Any]
    ):
        import json

        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO strategies(goal,confidence,steps,meta,created_at) VALUES (?,?,?,?,?)",
                (goal, confidence, json.dumps(steps), json.dumps(meta), time.time()),
            )
            conn.commit()

    def recent_strategies(self, limit: int = 20) -> List[Dict[str, Any]]:
        import json

        with self._connect() as conn:
            cur = conn.cursor()
            rows = cur.execute(
                "SELECT goal,confidence,steps,meta,created_at FROM strategies ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [
            {
                "goal": r[0],
                "confidence": r[1],
                "steps": json.loads(r[2]),
                "meta": json.loads(r[3]),
                "created_at": r[4],
            }
            for r in rows
        ]

    # ------------------------ Improvements ------------------------
    def add_improvement_suggestion(
        self,
        file_path: str,
        issue_type: str,
        description: str,
        severity: str,
        score: float,
        suggestion: str,
    ):
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO improvements(file_path,issue_type,description,severity,score,suggestion,created_at) VALUES (?,?,?,?,?,?,?)",
                (
                    file_path,
                    issue_type,
                    description,
                    severity,
                    score,
                    suggestion,
                    time.time(),
                ),
            )
            conn.commit()

    def recent_improvements(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            cur = conn.cursor()
            rows = cur.execute(
                "SELECT file_path,issue_type,description,severity,score,suggestion,created_at FROM improvements ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [
            {
                "file_path": r[0],
                "issue_type": r[1],
                "description": r[2],
                "severity": r[3],
                "score": r[4],
                "suggestion": r[5],
                "created_at": r[6],
            }
            for r in rows
        ]

    # ------------------------ Patch Proposals ------------------------
    def add_patch_proposal(
        self,
        improvement_id: int,
        file_path: str,
        proposed_patch: str,
        risk_level: str,
        estimated_impact: str,
    ):
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO patch_proposals(improvement_id,file_path,proposed_patch,risk_level,estimated_impact,created_at) VALUES (?,?,?,?,?,?)",
                (
                    improvement_id,
                    file_path,
                    proposed_patch,
                    risk_level,
                    estimated_impact,
                    time.time(),
                ),
            )
            conn.commit()

    def recent_patch_proposals(self, limit: int = 20) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            cur = conn.cursor()
            rows = cur.execute(
                "SELECT improvement_id,file_path,proposed_patch,risk_level,estimated_impact,created_at FROM patch_proposals ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [
            {
                "improvement_id": r[0],
                "file_path": r[1],
                "proposed_patch": r[2],
                "risk_level": r[3],
                "estimated_impact": r[4],
                "created_at": r[5],
            }
            for r in rows
        ]

    # ------------------------ Programming Knowledge ------------------------
    def add_programming_knowledge(
        self,
        category: str,
        topic: str,
        content: str,
        confidence: float = 0.8,
        source: str = "system",
    ):
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO programming_knowledge(category,topic,content,confidence,source,created_at) VALUES (?,?,?,?,?,?)",
                (category, topic, content, confidence, source, time.time()),
            )
            conn.commit()

    def query_programming_knowledge(
        self, category: Optional[str] = None, topic: Optional[str] = None
    ) -> List[Dict[str, Any]]:
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
                "category": r[0],
                "topic": r[1],
                "content": r[2],
                "confidence": r[3],
                "source": r[4],
                "created_at": r[5],
            }
            for r in rows
        ]

    def seed_programming_knowledge(self):
        """Seed comprehensive programming knowledge base with specialized domains"""
        knowledge_items = [
            # ======================== WEB SCRAPING MASTERY ========================
            (
                "web_scraping",
                "rate_limiting",
                "Always implement rate limiting between requests to avoid being blocked. Use delays of 1-3 seconds between requests.",
                0.9,
                "best_practices",
            ),
            (
                "web_scraping",
                "user_agents",
                "Rotate user agents to appear more human-like. Use realistic browser user agent strings.",
                0.8,
                "best_practices",
            ),
            (
                "web_scraping",
                "session_management",
                "Use session objects to maintain cookies and connection pooling for better performance.",
                0.9,
                "best_practices",
            ),
            (
                "web_scraping",
                "error_handling",
                "Implement comprehensive error handling for network timeouts, HTTP errors, and parsing failures.",
                0.9,
                "best_practices",
            ),
            (
                "web_scraping",
                "data_validation",
                "Always validate scraped data before storing. Check for expected data types and formats.",
                0.8,
                "best_practices",
            ),
            (
                "web_scraping",
                "proxy_rotation",
                "Use rotating proxies to distribute requests and avoid IP-based blocking.",
                0.8,
                "advanced",
            ),
            (
                "web_scraping",
                "captcha_handling",
                "Implement CAPTCHA detection and handling strategies, including human solver integration.",
                0.7,
                "advanced",
            ),
            (
                "web_scraping",
                "javascript_rendering",
                "Use headless browsers like Selenium, Playwright, or Puppeteer for JS-heavy sites.",
                0.9,
                "advanced",
            ),
            (
                "web_scraping",
                "anti_detection",
                "Mimic human behavior with random delays, mouse movements, and realistic browsing patterns.",
                0.8,
                "stealth",
            ),
            # ======================== PYTHON MASTERY ========================
            (
                "python",
                "exception_handling",
                "Use specific exception types rather than bare except clauses. Handle exceptions at the appropriate level.",
                0.9,
                "patterns",
            ),
            (
                "python",
                "logging",
                "Use structured logging with appropriate levels (DEBUG, INFO, WARNING, ERROR, CRITICAL).",
                0.8,
                "patterns",
            ),
            (
                "python",
                "type_hints",
                "Use type hints for better code documentation and IDE support. Import from typing module.",
                0.7,
                "patterns",
            ),
            (
                "python",
                "context_managers",
                "Use context managers (with statements) for resource management like files and database connections.",
                0.9,
                "patterns",
            ),
            (
                "python",
                "list_comprehensions",
                "Use list comprehensions for simple transformations, but prefer regular loops for complex logic.",
                0.7,
                "patterns",
            ),
            (
                "python",
                "async_programming",
                "Use asyncio for I/O-bound operations. async/await syntax for coroutines, aiohttp for async HTTP.",
                0.8,
                "async",
            ),
            (
                "python",
                "decorators",
                "Use decorators for cross-cutting concerns like timing, caching, authentication, and retry logic.",
                0.8,
                "patterns",
            ),
            (
                "python",
                "generators",
                "Use generators for memory-efficient iteration over large datasets. yield for lazy evaluation.",
                0.8,
                "memory",
            ),
            (
                "python",
                "dataclasses",
                "Use dataclasses for simple data containers. @dataclass decorator reduces boilerplate code.",
                0.7,
                "modern",
            ),
            (
                "python",
                "pathlib",
                "Use pathlib.Path instead of os.path for more readable and cross-platform file operations.",
                0.8,
                "modern",
            ),
            # ======================== JAVASCRIPT MASTERY ========================
            (
                "javascript",
                "promises_async",
                "Use async/await for asynchronous operations. Promise.all() for concurrent operations.",
                0.9,
                "async",
            ),
            (
                "javascript",
                "event_loop",
                "Understand the event loop: call stack, callback queue, microtask queue. Avoid blocking operations.",
                0.9,
                "fundamentals",
            ),
            (
                "javascript",
                "closures",
                "Master closures for data privacy and function factories. Understand lexical scoping.",
                0.8,
                "fundamentals",
            ),
            (
                "javascript",
                "dom_manipulation",
                "Use modern DOM APIs: querySelector, addEventListener, classList for efficient manipulation.",
                0.8,
                "frontend",
            ),
            (
                "javascript",
                "fetch_api",
                "Use fetch() for HTTP requests. Handle promises properly with .then()/.catch() or async/await.",
                0.9,
                "api",
            ),
            (
                "javascript",
                "module_system",
                "Use ES6 modules: import/export for code organization. Understand default vs named exports.",
                0.8,
                "modules",
            ),
            (
                "javascript",
                "arrow_functions",
                "Use arrow functions for concise syntax, but understand 'this' binding differences.",
                0.7,
                "syntax",
            ),
            (
                "javascript",
                "destructuring",
                "Use destructuring assignment for objects and arrays to extract values elegantly.",
                0.7,
                "syntax",
            ),
            (
                "javascript",
                "template_literals",
                "Use template literals with ${} for string interpolation instead of concatenation.",
                0.8,
                "syntax",
            ),
            (
                "javascript",
                "error_handling",
                "Use try/catch for synchronous code, .catch() for promises, and proper error propagation.",
                0.9,
                "error_handling",
            ),
            # ======================== BOT DEVELOPMENT ========================
            (
                "bot_development",
                "bot_framework",
                "Choose appropriate framework: discord.py for Discord, python-telegram-bot for Telegram, selenium for web bots.",
                0.9,
                "frameworks",
            ),
            (
                "bot_development",
                "rate_limiting",
                "Implement proper rate limiting to respect API limits. Use exponential backoff for retries.",
                0.9,
                "api_management",
            ),
            (
                "bot_development",
                "state_management",
                "Use databases or memory stores to maintain bot state between interactions.",
                0.8,
                "state",
            ),
            (
                "bot_development",
                "command_parsing",
                "Implement robust command parsing with argument validation and help systems.",
                0.8,
                "parsing",
            ),
            (
                "bot_development",
                "webhook_vs_polling",
                "Use webhooks for production bots for better performance, polling for development.",
                0.8,
                "architecture",
            ),
            (
                "bot_development",
                "error_recovery",
                "Implement graceful error recovery with logging, user notifications, and automatic restart.",
                0.9,
                "reliability",
            ),
            (
                "bot_development",
                "authentication",
                "Secure bot tokens and API keys. Use environment variables, never hardcode secrets.",
                0.9,
                "security",
            ),
            (
                "bot_development",
                "natural_language",
                "Use NLP libraries like spaCy, NLTK, or cloud APIs for intent recognition.",
                0.7,
                "ai",
            ),
            (
                "bot_development",
                "conversation_flow",
                "Design conversation flows with state machines for complex multi-step interactions.",
                0.8,
                "design",
            ),
            (
                "bot_development",
                "testing",
                "Test bots with mock APIs and automated conversation flows. Unit test command handlers.",
                0.8,
                "testing",
            ),
            # ======================== UI/UX DESIGN PRINCIPLES ========================
            (
                "uiux",
                "design_principles",
                "Follow design principles: contrast, repetition, alignment, proximity (CRAP). Consistent visual hierarchy.",
                0.9,
                "principles",
            ),
            (
                "uiux",
                "user_research",
                "Conduct user research: interviews, surveys, usability testing to understand user needs.",
                0.9,
                "research",
            ),
            (
                "uiux",
                "wireframing",
                "Create wireframes before high-fidelity designs. Focus on information architecture and user flow.",
                0.8,
                "process",
            ),
            (
                "uiux",
                "prototyping",
                "Build interactive prototypes with tools like Figma, Adobe XD, or code for user testing.",
                0.8,
                "prototyping",
            ),
            (
                "uiux",
                "accessibility",
                "Design for accessibility: WCAG guidelines, keyboard navigation, screen reader compatibility.",
                0.9,
                "accessibility",
            ),
            (
                "uiux",
                "responsive_design",
                "Design mobile-first with flexible grids, fluid images, and media queries for all screen sizes.",
                0.9,
                "responsive",
            ),
            (
                "uiux",
                "color_theory",
                "Understand color psychology, contrast ratios, color blindness considerations in design.",
                0.8,
                "visual",
            ),
            (
                "uiux",
                "typography",
                "Choose readable fonts, establish type hierarchy, consider line height and letter spacing.",
                0.8,
                "visual",
            ),
            (
                "uiux",
                "user_testing",
                "Conduct regular user testing sessions. Observe behavior, gather feedback, iterate designs.",
                0.9,
                "validation",
            ),
            (
                "uiux",
                "information_architecture",
                "Organize content logically with clear navigation patterns and intuitive site structure.",
                0.8,
                "architecture",
            ),
            # ======================== DATABASE EXCELLENCE ========================
            (
                "database",
                "connection_pooling",
                "Use connection pooling to efficiently manage database connections in multi-threaded applications.",
                0.9,
                "patterns",
            ),
            (
                "database",
                "prepared_statements",
                "Use parameterized queries to prevent SQL injection attacks.",
                0.9,
                "security",
            ),
            (
                "database",
                "indexing_strategy",
                "Create indexes on frequently queried columns. Understand B-tree, hash, and full-text indexes.",
                0.9,
                "performance",
            ),
            (
                "database",
                "normalization",
                "Normalize databases to reduce redundancy, but denormalize for read-heavy workloads.",
                0.8,
                "design",
            ),
            (
                "database",
                "transaction_management",
                "Use transactions for data consistency. Understand ACID properties and isolation levels.",
                0.9,
                "consistency",
            ),
            (
                "database",
                "query_optimization",
                "Analyze query execution plans. Use EXPLAIN to identify bottlenecks and optimize queries.",
                0.8,
                "performance",
            ),
            (
                "database",
                "backup_strategies",
                "Implement automated backups with point-in-time recovery. Test restore procedures regularly.",
                0.9,
                "reliability",
            ),
            (
                "database",
                "migration_patterns",
                "Use database migrations for schema changes. Version control database schema changes.",
                0.8,
                "versioning",
            ),
            # ======================== API DEVELOPMENT ========================
            (
                "api_development",
                "rest_principles",
                "Follow REST principles: stateless, cacheable, uniform interface, layered system.",
                0.9,
                "architecture",
            ),
            (
                "api_development",
                "http_status_codes",
                "Use appropriate HTTP status codes: 200 success, 400 client error, 500 server error.",
                0.9,
                "standards",
            ),
            (
                "api_development",
                "authentication",
                "Implement secure authentication: JWT tokens, OAuth2, API keys with proper expiration.",
                0.9,
                "security",
            ),
            (
                "api_development",
                "rate_limiting",
                "Implement API rate limiting to prevent abuse. Use sliding window or token bucket algorithms.",
                0.8,
                "protection",
            ),
            (
                "api_development",
                "versioning",
                "Version APIs with URL versioning (/v1/), header versioning, or parameter versioning.",
                0.8,
                "versioning",
            ),
            (
                "api_development",
                "documentation",
                "Document APIs with OpenAPI/Swagger. Include examples, error codes, and authentication details.",
                0.9,
                "documentation",
            ),
            (
                "api_development",
                "error_handling",
                "Return consistent error responses with error codes, messages, and debugging information.",
                0.9,
                "error_handling",
            ),
            (
                "api_development",
                "caching",
                "Implement caching strategies: ETags, Cache-Control headers, Redis for distributed caching.",
                0.8,
                "performance",
            ),
            # ======================== SECURITY BEST PRACTICES ========================
            (
                "security",
                "input_validation",
                "Validate and sanitize all user inputs. Use whitelist validation over blacklist.",
                0.9,
                "input",
            ),
            (
                "security",
                "authentication",
                "Use strong password policies, multi-factor authentication, and secure session management.",
                0.9,
                "auth",
            ),
            (
                "security",
                "encryption",
                "Use HTTPS everywhere. Encrypt sensitive data at rest with AES-256, bcrypt for passwords.",
                0.9,
                "encryption",
            ),
            (
                "security",
                "sql_injection",
                "Prevent SQL injection with parameterized queries, stored procedures, and input validation.",
                0.9,
                "injection",
            ),
            (
                "security",
                "xss_prevention",
                "Prevent XSS attacks with output encoding, CSP headers, and input sanitization.",
                0.9,
                "xss",
            ),
            (
                "security",
                "csrf_protection",
                "Implement CSRF tokens for state-changing operations. Use SameSite cookie attributes.",
                0.8,
                "csrf",
            ),
            (
                "security",
                "secrets_management",
                "Store secrets securely using environment variables, key vaults, or secret management services.",
                0.9,
                "secrets",
            ),
            (
                "security",
                "security_headers",
                "Use security headers: HSTS, X-Frame-Options, X-Content-Type-Options, CSP.",
                0.8,
                "headers",
            ),
            # ======================== PERFORMANCE OPTIMIZATION ========================
            (
                "performance",
                "profiling",
                "Profile applications to identify bottlenecks. Use cProfile, line_profiler, memory_profiler.",
                0.9,
                "profiling",
            ),
            (
                "performance",
                "caching_strategies",
                "Implement multi-level caching: browser cache, CDN, application cache, database cache.",
                0.9,
                "caching",
            ),
            (
                "performance",
                "lazy_loading",
                "Use lazy loading for images, modules, and data to improve initial load times.",
                0.8,
                "loading",
            ),
            (
                "performance",
                "database_optimization",
                "Optimize database queries, use proper indexing, and implement connection pooling.",
                0.9,
                "database",
            ),
            (
                "performance",
                "compression",
                "Use compression: gzip for HTTP responses, image optimization, minification for assets.",
                0.8,
                "compression",
            ),
            (
                "performance",
                "cdn_usage",
                "Use Content Delivery Networks for static assets to reduce latency and server load.",
                0.8,
                "infrastructure",
            ),
            (
                "performance",
                "async_processing",
                "Use asynchronous processing for I/O-bound operations to improve throughput.",
                0.8,
                "async",
            ),
            # ======================== CODE QUALITY ========================
            (
                "code_quality",
                "clean_code",
                "Write self-documenting code with meaningful names, small functions, and clear intent.",
                0.9,
                "principles",
            ),
            (
                "code_quality",
                "testing",
                "Write comprehensive tests: unit tests, integration tests, end-to-end tests.",
                0.9,
                "testing",
            ),
            (
                "code_quality",
                "code_review",
                "Conduct thorough code reviews focusing on logic, security, performance, and maintainability.",
                0.9,
                "review",
            ),
            (
                "code_quality",
                "refactoring",
                "Regularly refactor code to improve structure while maintaining functionality.",
                0.8,
                "maintenance",
            ),
            (
                "code_quality",
                "documentation",
                "Document code with clear comments, docstrings, and architectural decision records.",
                0.8,
                "documentation",
            ),
            (
                "code_quality",
                "version_control",
                "Use Git effectively: meaningful commits, branching strategies, pull requests.",
                0.9,
                "git",
            ),
            (
                "database",
                "indexing",
                "Create indexes on frequently queried columns to improve performance.",
                0.8,
                "performance",
            ),
            (
                "database",
                "transactions",
                "Use database transactions for operations that must be atomic.",
                0.9,
                "patterns",
            ),
            # Performance Optimization
            (
                "performance",
                "caching",
                "Implement caching strategies for frequently accessed data to reduce database load.",
                0.8,
                "optimization",
            ),
            (
                "performance",
                "async_programming",
                "Use async/await for I/O bound operations to improve concurrency.",
                0.7,
                "optimization",
            ),
            (
                "performance",
                "memory_management",
                "Be mindful of memory usage when processing large datasets. Use generators for large data streams.",
                0.8,
                "optimization",
            ),
            # Security Best Practices
            (
                "security",
                "input_validation",
                "Always validate and sanitize user input to prevent injection attacks.",
                0.9,
                "security",
            ),
            (
                "security",
                "authentication",
                "Implement proper authentication and authorization mechanisms.",
                0.9,
                "security",
            ),
            (
                "security",
                "secrets_management",
                "Never hard-code secrets in source code. Use environment variables or secure vaults.",
                0.9,
                "security",
            ),
            # Code Quality
            (
                "code_quality",
                "single_responsibility",
                "Each function should have a single, well-defined responsibility.",
                0.8,
                "principles",
            ),
            (
                "code_quality",
                "documentation",
                "Write clear docstrings and comments explaining the why, not just the what.",
                0.7,
                "principles",
            ),
            (
                "code_quality",
                "testing",
                "Write unit tests for critical functions. Aim for good test coverage.",
                0.8,
                "principles",
            ),
            (
                "code_quality",
                "refactoring",
                "Regularly refactor code to improve readability and maintainability.",
                0.7,
                "principles",
            ),
        ]

        existing_count = 0
        with self._connect() as conn:
            cur = conn.cursor()
            existing_count = cur.execute(
                "SELECT COUNT(*) FROM programming_knowledge"
            ).fetchone()[0]

        if existing_count == 0:
            for category, topic, content, confidence, source in knowledge_items:
                self.add_programming_knowledge(
                    category, topic, content, confidence, source
                )
            return len(knowledge_items)
        return 0

    # ------------------------ Utility ------------------------
    def stats(self) -> Dict[str, Any]:
        with self._connect() as conn:
            cur = conn.cursor()
            counts = {}
            for table in SCHEMA.keys():
                try:
                    counts[table] = cur.execute(
                        f"SELECT COUNT(*) FROM {table}"
                    ).fetchone()[0]
                except Exception:
                    counts[table] = 0
        return counts

    # ------------------------ Advanced SQL Operations ------------------------
    def add_data_source(
        self,
        name: str,
        url: str,
        source_type: str,
        access_method: str = "HTTP",
        credentials_needed: bool = False,
        notes: str = "",
    ) -> int:
        """Add a new data source for scraping."""
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT OR REPLACE INTO data_sources
                (name, url, source_type, access_method, credentials_needed, notes, success_rate, created_at)
                VALUES (?, ?, ?, ?, ?, ?, 0.0, ?)
            """,
                (
                    name,
                    url,
                    source_type,
                    access_method,
                    credentials_needed,
                    notes,
                    time.time(),
                ),
            )
            return cur.lastrowid

    def add_scraping_target(
        self,
        domain: str,
        url_pattern: str,
        content_type: str,
        extraction_rules: str,
        anti_detection_level: int = 1,
    ) -> int:
        """Add a scraping target with extraction rules."""
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO scraping_targets
                (domain, url_pattern, content_type, extraction_rules, anti_detection_level,
                 success_rate, created_at)
                VALUES (?, ?, ?, ?, ?, 0.0, ?)
            """,
                (
                    domain,
                    url_pattern,
                    content_type,
                    extraction_rules,
                    anti_detection_level,
                    time.time(),
                ),
            )
            return cur.lastrowid

    def add_learned_pattern(
        self,
        pattern_type: str,
        pattern_data: str,
        confidence: float,
        domain: str = "",
        context: str = "",
    ) -> int:
        """Add a learned pattern from successful operations."""
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO learned_patterns
                (pattern_type, pattern_data, confidence, usage_count, success_rate,
                 domain, context, created_at)
                VALUES (?, ?, ?, 0, 1.0, ?, ?, ?)
            """,
                (pattern_type, pattern_data, confidence, domain, context, time.time()),
            )
            return cur.lastrowid

    def create_knowledge_relationship(
        self,
        source_id: int,
        target_id: int,
        relationship_type: str,
        strength: float = 0.5,
    ):
        """Create a relationship between two knowledge items."""
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO knowledge_relationships
                (source_knowledge_id, target_knowledge_id, relationship_type, strength, created_at)
                VALUES (?, ?, ?, ?, ?)
            """,
                (source_id, target_id, relationship_type, strength, time.time()),
            )

    def get_related_knowledge(self, knowledge_id: int, limit: int = 10) -> List[Dict]:
        """Get knowledge items related to the given item."""
        with self._connect() as conn:
            cur = conn.cursor()
            results = cur.execute(
                """
                SELECT pk.*, kr.relationship_type, kr.strength
                FROM programming_knowledge pk
                JOIN knowledge_relationships kr ON pk.id = kr.target_knowledge_id
                WHERE kr.source_knowledge_id = ?
                ORDER BY kr.strength DESC
                LIMIT ?
            """,
                (knowledge_id, limit),
            ).fetchall()

            return [dict(row) for row in results]

    def get_data_sources_by_type(self, source_type: str) -> List[Dict]:
        """Get all data sources of a specific type."""
        with self._connect() as conn:
            cur = conn.cursor()
            results = cur.execute(
                """
                SELECT * FROM data_sources
                WHERE source_type = ?
                ORDER BY success_rate DESC, name
            """,
                (source_type,),
            ).fetchall()

            return [dict(row) for row in results]

    def get_successful_patterns(
        self, pattern_type: str = None, min_success_rate: float = 0.7
    ) -> List[Dict]:
        """Get learned patterns with high success rates."""
        with self._connect() as conn:
            cur = conn.cursor()

            if pattern_type:
                results = cur.execute(
                    """
                    SELECT * FROM learned_patterns
                    WHERE pattern_type = ? AND success_rate >= ?
                    ORDER BY success_rate DESC, usage_count DESC
                """,
                    (pattern_type, min_success_rate),
                ).fetchall()
            else:
                results = cur.execute(
                    """
                    SELECT * FROM learned_patterns
                    WHERE success_rate >= ?
                    ORDER BY success_rate DESC, usage_count DESC
                """,
                    (min_success_rate,),
                ).fetchall()

            return [dict(row) for row in results]

    def update_pattern_success(self, pattern_id: int, success: bool):
        """Update the success rate of a learned pattern."""
        with self._connect() as conn:
            cur = conn.cursor()

            # Get current stats
            current = cur.execute(
                """
                SELECT usage_count, success_rate FROM learned_patterns WHERE id = ?
            """,
                (pattern_id,),
            ).fetchone()

            if current:
                usage_count, success_rate = current
                new_usage_count = usage_count + 1

                # Update success rate using incremental average
                if success:
                    new_success_rate = (
                        success_rate * usage_count + 1.0
                    ) / new_usage_count
                else:
                    new_success_rate = (success_rate * usage_count) / new_usage_count

                cur.execute(
                    """
                    UPDATE learned_patterns
                    SET usage_count = ?, success_rate = ?
                    WHERE id = ?
                """,
                    (new_usage_count, new_success_rate, pattern_id),
                )

    def advanced_knowledge_search(
        self, query: str, domains: List[str] = None, min_confidence: float = 0.5
    ) -> List[Dict]:
        """Advanced search across knowledge base with domain filtering."""
        with self._connect() as conn:
            cur = conn.cursor()

            base_query = """
                SELECT *,
                       CASE
                           WHEN content LIKE ? THEN confidence + 0.2
                           WHEN topic LIKE ? THEN confidence + 0.1
                           ELSE confidence
                       END as relevance_score
                FROM programming_knowledge
                WHERE (content LIKE ? OR topic LIKE ? OR category LIKE ?)
                AND confidence >= ?
            """

            params = [
                f"%{query}%",
                f"%{query}%",
                f"%{query}%",
                f"%{query}%",
                f"%{query}%",
                min_confidence,
            ]

            if domains:
                domain_placeholders = ",".join("?" * len(domains))
                base_query += f" AND category IN ({domain_placeholders})"
                params.extend(domains)

            base_query += " ORDER BY relevance_score DESC, confidence DESC"

            results = cur.execute(base_query, params).fetchall()
            return [dict(row) for row in results]

    def get_knowledge_graph_data(self) -> Dict[str, Any]:
        """Get data for visualizing the knowledge graph."""
        with self._connect() as conn:
            cur = conn.cursor()

            # Get nodes (knowledge items)
            nodes = cur.execute(
                """
                SELECT id, category, topic, confidence, source
                FROM programming_knowledge
            """
            ).fetchall()

            # Get edges (relationships)
            edges = cur.execute(
                """
                SELECT source_knowledge_id, target_knowledge_id, relationship_type, strength
                FROM knowledge_relationships
            """
            ).fetchall()

            return {
                "nodes": [dict(row) for row in nodes],
                "edges": [dict(row) for row in edges],
            }

    def get_domain_expertise_score(self, domain: str) -> float:
        """Calculate expertise score for a specific domain."""
        with self._connect() as conn:
            cur = conn.cursor()

            result = cur.execute(
                """
                SELECT
                    COUNT(*) as knowledge_count,
                    AVG(confidence) as avg_confidence,
                    COUNT(DISTINCT source) as source_diversity
                FROM programming_knowledge
                WHERE category = ?
            """,
                (domain,),
            ).fetchone()

            if result and result[0] > 0:
                knowledge_count, avg_confidence, source_diversity = result

                # Calculate expertise score based on quantity, quality, and diversity
                quantity_score = min(
                    knowledge_count / 20.0, 1.0
                )  # Normalize to max 20 items
                quality_score = avg_confidence
                diversity_score = min(
                    source_diversity / 5.0, 1.0
                )  # Normalize to max 5 sources

                expertise_score = (
                    quantity_score * 0.4 + quality_score * 0.4 + diversity_score * 0.2
                )
                return expertise_score

            return 0.0

    def backup_knowledge_to_json(self, output_path: str):
        """Backup entire knowledge base to JSON for portability."""
        import json

        with self._connect() as conn:
            cur = conn.cursor()

            backup_data = {}

            for table_name in SCHEMA.keys():
                try:
                    results = cur.execute(f"SELECT * FROM {table_name}").fetchall()
                    backup_data[table_name] = [dict(row) for row in results]
                except Exception:
                    backup_data[table_name] = []

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)

    def get_comprehensive_summary(self) -> Dict[str, Any]:
        """Get comprehensive summary of the knowledge base."""
        with self._connect() as conn:
            cur = conn.cursor()

            # Knowledge distribution by category
            categories = cur.execute(
                """
                SELECT category, COUNT(*) as count, AVG(confidence) as avg_confidence
                FROM programming_knowledge
                GROUP BY category
                ORDER BY count DESC
            """
            ).fetchall()

            # Top sources
            sources = cur.execute(
                """
                SELECT source, COUNT(*) as contributions
                FROM programming_knowledge
                GROUP BY source
                ORDER BY contributions DESC
                LIMIT 10
            """
            ).fetchall()

            # Recent additions
            recent = cur.execute(
                """
                SELECT category, topic, created_at
                FROM programming_knowledge
                ORDER BY created_at DESC
                LIMIT 10
            """
            ).fetchall()

            # Overall stats
            total_knowledge = cur.execute(
                "SELECT COUNT(*) FROM programming_knowledge"
            ).fetchone()[0]
            total_relationships = cur.execute(
                "SELECT COUNT(*) FROM knowledge_relationships"
            ).fetchone()[0]
            total_sources = cur.execute("SELECT COUNT(*) FROM data_sources").fetchone()[
                0
            ]
            total_patterns = cur.execute(
                "SELECT COUNT(*) FROM learned_patterns"
            ).fetchone()[0]

            return {
                "total_knowledge_items": total_knowledge,
                "total_relationships": total_relationships,
                "total_data_sources": total_sources,
                "total_learned_patterns": total_patterns,
                "categories": [dict(row) for row in categories],
                "top_sources": [dict(row) for row in sources],
                "recent_additions": [dict(row) for row in recent],
                "domain_expertise": {
                    category[0]: self.get_domain_expertise_score(category[0])
                    for category in categories
                },
            }

    def get_knowledge_summary(self) -> Dict[str, Any]:
        """Get comprehensive knowledge summary for the brain"""
        stats = self.stats()

        # Get programming knowledge categories
        prog_categories = {}
        try:
            with self._connect() as conn:
                cur = conn.cursor()
                rows = cur.execute(
                    "SELECT category, COUNT(*) FROM programming_knowledge GROUP BY category"
                ).fetchall()
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
                rows = cur.execute(
                    """
                    SELECT subject, obj, COUNT(*)
                    FROM facts
                    WHERE category='scrape_event' AND predicate='event_result'
                    GROUP BY subject, obj
                """
                ).fetchall()
                for domain, result, count in rows:
                    if domain not in domain_performance:
                        domain_performance[domain] = {"success": 0, "failure": 0}
                    domain_performance[domain][result] = count
        except Exception:
            pass

        return {
            "total_facts": stats.get("facts", 0),
            "programming_knowledge": {
                "total": stats.get("programming_knowledge", 0),
                "categories": prog_categories,
            },
            "strategies": {
                "total": stats.get("strategies", 0),
                "recent": [s["goal"] for s in recent_strategies],
            },
            "improvements": stats.get("improvements", 0),
            "patch_proposals": stats.get("patch_proposals", 0),
            "domain_performance": domain_performance,
        }


# ===== MULTI-DATABASE CONNECTOR SYSTEM =====


class DatabaseConnector:
    """Base class for database connectors."""

    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.connection = None

    def connect(self):
        """Establish connection to database."""
        raise NotImplementedError

    def disconnect(self):
        """Close database connection."""
        raise NotImplementedError

    def execute_query(self, query: str, params: Optional[List] = None) -> List[Dict]:
        """Execute query and return results."""
        raise NotImplementedError

    def get_schema_info(self) -> Dict[str, Any]:
        """Get database schema information."""
        raise NotImplementedError

    def test_connection(self) -> bool:
        """Test database connectivity."""
        raise NotImplementedError


class MongoDBConnector(DatabaseConnector):
    """MongoDB database connector."""

    def __init__(self, connection_string: str):
        super().__init__(connection_string)
        try:
            from pymongo import MongoClient

            self.client_class = MongoClient
        except ImportError:
            self.client_class = None

    def connect(self):
        """Connect to MongoDB."""
        if not self.client_class:
            raise ImportError(
                "pymongo not installed. Install with: pip install pymongo"
            )

        self.connection = self.client_class(self.connection_string)
        return self.connection

    def disconnect(self):
        """Close MongoDB connection."""
        if self.connection:
            self.connection.close()

    def execute_query(self, query: str, params: Optional[List] = None) -> List[Dict]:
        """Execute MongoDB query."""
        # MongoDB uses different query format - this is a simplified example
        db_name, collection_name = query.split(".")[:2]
        db = self.connection[db_name]
        collection = db[collection_name]

        if params and "find" in query:
            return list(collection.find(params[0] if params else {}))
        elif "count" in query:
            return [{"count": collection.count_documents(params[0] if params else {})}]

        return []

    def get_schema_info(self) -> Dict[str, Any]:
        """Get MongoDB collection information."""
        db_names = self.connection.list_database_names()
        schema = {}

        for db_name in db_names[:5]:  # Limit to first 5 databases
            db = self.connection[db_name]
            collections = db.list_collection_names()
            schema[db_name] = {
                "collections": collections[:10],  # Limit collections
                "type": "document_store",
            }

        return schema

    def test_connection(self) -> bool:
        """Test MongoDB connectivity."""
        try:
            self.connection.admin.command("ping")
            return True
        except Exception:
            return False


class PostgreSQLConnector(DatabaseConnector):
    """PostgreSQL database connector."""

    def __init__(self, connection_string: str):
        super().__init__(connection_string)
        try:
            import psycopg2

            self.driver = psycopg2
        except ImportError:
            self.driver = None

    def connect(self):
        """Connect to PostgreSQL."""
        if not self.driver:
            raise ImportError(
                "psycopg2 not installed. Install with: pip install psycopg2-binary"
            )

        self.connection = self.driver.connect(self.connection_string)
        return self.connection

    def disconnect(self):
        """Close PostgreSQL connection."""
        if self.connection:
            self.connection.close()

    def execute_query(self, query: str, params: Optional[List] = None) -> List[Dict]:
        """Execute PostgreSQL query."""
        cursor = self.connection.cursor()
        cursor.execute(query, params or [])

        if cursor.description:
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]

        return []

    def get_schema_info(self) -> Dict[str, Any]:
        """Get PostgreSQL schema information."""
        query = """
            SELECT table_schema, table_name, column_name, data_type
            FROM information_schema.columns
            WHERE table_schema NOT IN ('information_schema', 'pg_catalog')
            ORDER BY table_schema, table_name, ordinal_position
        """

        results = self.execute_query(query)
        schema = {}

        for row in results:
            schema_name = row["table_schema"]
            table_name = row["table_name"]

            if schema_name not in schema:
                schema[schema_name] = {"tables": {}, "type": "relational"}

            if table_name not in schema[schema_name]["tables"]:
                schema[schema_name]["tables"][table_name] = []

            schema[schema_name]["tables"][table_name].append(
                {"column": row["column_name"], "type": row["data_type"]}
            )

        return schema

    def test_connection(self) -> bool:
        """Test PostgreSQL connectivity."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT 1")
            return True
        except Exception:
            return False


class RedisConnector(DatabaseConnector):
    """Redis database connector."""

    def __init__(self, connection_string: str):
        super().__init__(connection_string)
        try:
            import redis

            self.redis_module = redis
        except ImportError:
            self.redis_module = None

    def connect(self):
        """Connect to Redis."""
        if not self.redis_module:
            raise ImportError("redis not installed. Install with: pip install redis")

        self.connection = self.redis_module.from_url(self.connection_string)
        return self.connection

    def disconnect(self):
        """Close Redis connection."""
        if self.connection:
            self.connection.close()

    def execute_query(self, query: str, params: Optional[List] = None) -> List[Dict]:
        """Execute Redis commands."""
        # Redis commands are different - this is a simplified example
        parts = query.split()
        command = parts[0].upper()

        if command == "GET":
            key = parts[1] if len(parts) > 1 else params[0] if params else ""
            value = self.connection.get(key)
            return [{"key": key, "value": value.decode() if value else None}]
        elif command == "KEYS":
            pattern = parts[1] if len(parts) > 1 else "*"
            keys = self.connection.keys(pattern)
            return [{"keys": [k.decode() for k in keys]}]
        elif command == "INFO":
            info = self.connection.info()
            return [info]

        return []

    def get_schema_info(self) -> Dict[str, Any]:
        """Get Redis database information."""
        info = self.connection.info()
        return {
            "redis_version": info.get("redis_version"),
            "db_count": info.get("databases", 16),
            "memory_usage": info.get("used_memory_human"),
            "type": "key_value",
        }

    def test_connection(self) -> bool:
        """Test Redis connectivity."""
        try:
            return self.connection.ping()
        except Exception:
            return False


class ElasticsearchConnector(DatabaseConnector):
    """Elasticsearch connector."""

    def __init__(self, connection_string: str):
        super().__init__(connection_string)
        try:
            from elasticsearch import Elasticsearch

            self.es_class = Elasticsearch
        except ImportError:
            self.es_class = None

    def connect(self):
        """Connect to Elasticsearch."""
        if not self.es_class:
            raise ImportError(
                "elasticsearch not installed. Install with: pip install elasticsearch"
            )

        self.connection = self.es_class([self.connection_string])
        return self.connection

    def disconnect(self):
        """Close Elasticsearch connection."""
        # Elasticsearch client doesn't need explicit close

    def execute_query(self, query: str, params: Optional[List] = None) -> List[Dict]:
        """Execute Elasticsearch query."""
        try:
            # Simple search example
            if "search" in query.lower():
                body = params[0] if params else {"query": {"match_all": {}}}
                result = self.connection.search(body=body)
                return result.get("hits", {}).get("hits", [])
            elif "indices" in query.lower():
                indices = self.connection.indices.get_alias("*")
                return [{"indices": list(indices.keys())}]
        except Exception:
            pass

        return []

    def get_schema_info(self) -> Dict[str, Any]:
        """Get Elasticsearch cluster information."""
        try:
            health = self.connection.cluster.health()
            indices = self.connection.indices.get_alias("*")

            return {
                "cluster_name": health.get("cluster_name"),
                "status": health.get("status"),
                "number_of_nodes": health.get("number_of_nodes"),
                "indices": list(indices.keys())[:10],  # Limit to first 10
                "type": "search_engine",
            }
        except Exception:
            return {"type": "search_engine", "error": "Failed to get info"}

    def test_connection(self) -> bool:
        """Test Elasticsearch connectivity."""
        try:
            return self.connection.ping()
        except Exception:
            return False


class MultiDatabaseManager:
    """Manager for multiple database connections."""

    def __init__(self):
        self.connectors = {}
        self.connector_classes = {
            "mongodb": MongoDBConnector,
            "postgresql": PostgreSQLConnector,
            "mysql": PostgreSQLConnector,  # Can use same connector with different driver
            "redis": RedisConnector,
            "elasticsearch": ElasticsearchConnector,
        }

    def add_database(self, name: str, db_type: str, connection_string: str) -> bool:
        """Add a new database connection."""
        try:
            if db_type.lower() not in self.connector_classes:
                raise ValueError(f"Unsupported database type: {db_type}")

            connector_class = self.connector_classes[db_type.lower()]
            connector = connector_class(connection_string)
            connector.connect()

            if connector.test_connection():
                self.connectors[name] = connector
                return True
            else:
                connector.disconnect()
                return False

        except Exception as e:
            print(f"Failed to add database {name}: {e}")
            return False

    def remove_database(self, name: str) -> bool:
        """Remove a database connection."""
        if name in self.connectors:
            self.connectors[name].disconnect()
            del self.connectors[name]
            return True
        return False

    def execute_query(
        self, db_name: str, query: str, params: Optional[List] = None
    ) -> List[Dict]:
        """Execute query on specific database."""
        if db_name in self.connectors:
            try:
                return self.connectors[db_name].execute_query(query, params)
            except Exception as e:
                print(f"Query failed on {db_name}: {e}")
                return []
        return []

    def get_all_schemas(self) -> Dict[str, Any]:
        """Get schema information from all connected databases."""
        schemas = {}
        for name, connector in self.connectors.items():
            try:
                schemas[name] = connector.get_schema_info()
            except Exception as e:
                schemas[name] = {"error": str(e)}
        return schemas

    def test_all_connections(self) -> Dict[str, bool]:
        """Test all database connections."""
        results = {}
        for name, connector in self.connectors.items():
            results[name] = connector.test_connection()
        return results

    def get_database_types(self) -> List[str]:
        """Get list of supported database types."""
        return list(self.connector_classes.keys())

    def close_all_connections(self):
        """Close all database connections."""
        for connector in self.connectors.values():
            connector.disconnect()
        self.connectors.clear()
