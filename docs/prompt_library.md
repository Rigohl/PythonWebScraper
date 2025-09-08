# Prompt Library — Gemini / Vertex / MCP

This file collects copy/paste-ready prompts grouped by use-case: code generation, repair, tests, DB, UI, infra, MCP interactions, function-calling, and evaluation templates.

## Usage notes

- Replace placeholders like `CODE`, `HTML`, `SCHEMA` before use.
- Prefer `system` + `user` messages structure when calling chat-style APIs.
- Always request `outputSchema` when expecting structured JSON.

---

## 1) Code generation — Python function

System: "You are a senior Python engineer. Produce clean, typed, testable functions following PEP8 and include docstrings and examples."

User:

```text
Task: Implement a function `parse_price(text: str) -> float` that accepts prices like "USD 12.34", "12,34€", "$12" and returns the price in euros as float. Assume 1 USD = 0.92 EUR. Handle thousands separators and missing currency as EUR.
Format: Return only the function source code in a single `python` fenced block.
Examples:
- "USD 12.34" -> 11.3528
- "12,34€" -> 12.34

Constraints: include type annotations, raise ValueError for unparsable inputs.
```

---

## 2) Repair code with tests

System: "You are a code reviewer. Given failing pytest output and code, produce a unified diff patch that fixes the bug and add a new pytest that covers the failing case."

User:

```text
Task: Repair the failing function. Input: `PASTE CODE` and `PASTE TEST OUTPUT`
Format: Return a diff (unified) and the new/modified test file content.
```

---

## 3) Generate DB models + Alembic migration

System: "You are a backend engineer. Generate SQLAlchemy models and an Alembic `upgrade` and `downgrade` migration snippet for the schema change."

User:

```text
Task: Create a `Product` model with fields: id (int pk), sku (str unique), name, price (decimal), metadata (json). Provide SQLAlchemy model and Alembic migration `upgrade`/`downgrade` functions.
Format: respond with two fenced blocks: first `python` for model, second `python` for alembic revision code.
```

---

## 4) Frontend components (React)

System: "You are a frontend engineer producing small React components with clear props and tests (React Testing Library)."

User:

```text
Task: Implement a React component `UrlForm` that posts to `/api/extract` and shows the JSON result. Include a unit test that mocks fetch and verifies render flow.
Format: Return `jsx` for component and `javascript` for test.
```

---

## 5) TUI with Textual

System: "You are a terminal UI developer. Create a small Textual app that lists items and shows details on selection."

User:

```python
Task: Provide `python` code with a small Textual app: list view + details pane.
```

---

## 6) MCP tool invocation prompt

System: "You are an LLM that can discover and call tools via MCP. Use `tools/list` to find available tools, then call them with `tools/call` providing `outputSchema` where applicable."

User:

```json
Task: Discover available tools and extract diffs from git using the `git` tool. Provide the JSON of results and, if non-empty, summarize the top 3 diffs.
Format: Provide a JSON output matching schema: {"diffs": [{"file": str, "diff": str}], "summary": str}
```

---

## 7) Function calling / structured output

System: "You are an assistant that returns only JSON matching the provided schema. You must not produce any extra text."

User:

```json
Schema: `PASTE JSON SCHEMA`
Task: Produce an output that validates against the schema given the input `PASTE INPUT`
Format: strict JSON.
```

---

## 8) Evaluation prompt (generate unit tests)

System: "You are a test generator. Produce pytest tests that cover edge cases, happy path, and property-based checks when appropriate."

User:

```python
Task: Given function code `CODE`, produce `tests/test_<module>.py` with >= 5 tests covering typical and edge cases.
Format: single python fenced block.
```

---

## 9) Infra as Code — Terraform snippet

System: "You are an infra engineer. Produce minimal Terraform snippets with variables and outputs."

User:

```hcl
Task: Create a Terraform resource for an Azure Container App or for an AWS ECS service (choose one), include variables and a minimal output block. Assume registry credentials are provided.
```

---

## 10) Prompt optimization / A/B testing

System: "You are an experiment designer. Produce two prompt variations (A and B), instrumentation plan, and metrics to compare."

User:

```text
Task: For the `parse_price` generator, provide two prompt variants, measurement plan (latency, exact-match on outputs, failure rate), and expected sample size.
```

---

## Notes on sourcing forum /.onion prompts

- I cannot access `.onion` (Tor) sites from this environment. Provide the content or allow me to crawl clearnet copies or community mirrors.
- For community-vetted prompts, prefer curated repos (Awesome lists), Reddit threads, and StackOverflow Q&A; I've included several links in the docs and can expand with more crawl results on request.

## End of prompt library

---

## Appendix: A/B Variants, structured outputs, and MCP templates

### A/B prompt variants (parse_price)

- Variant A (concise):

```text
System: You are a precise extractor. Return only the parsed numeric value in EUR as a JSON number.
User: Parse the price from the input string and convert to EUR. Use 0.92 conversion for USD. Examples: "USD 12.34" -> 11.3528.
Output: JSON number only.
```

- Variant B (with reasoning/examples):

```text
System: You are a senior data engineer. Explain briefly the parsing rules then provide the final numeric value in EUR.
User: Given the input string, describe how you parse currency and separators, then output JSON: {"value_eur": float, "source_currency": "EUR|USD|...", "notes": "..."}.
Examples: "USD 12.34" -> {"value_eur": 11.3528, "source_currency": "USD"}
```

### Structured `outputSchema` example (JSON Schema)

Requesting structured output reduces parsing errors. Example `outputSchema` for the `parse_price` task:

```json
{
  "type": "object",
  "properties": {
    "value_eur": {"type": "number"},
    "source_currency": {"type": "string"},
    "confidence": {"type": "number", "minimum": 0, "maximum": 1}
  },
  "required": ["value_eur", "source_currency"]
}
```

When calling Vertex/Gemini, include this schema as `outputSchema` and expect strict JSON back.

### MCP discovery + call prompt (template)

```text
System: You are an assistant that must discover available MCP tools via `tools/list`, select the `git` tool if present, and call it to extract diffs. Always validate tool responses against their declared output schema.
User: Discover tools, run `tools/list`, then find a tool with id containing `git` and call it with params {"args": ["diff", "--name-only"]}. Return JSON matching: {"tool_used": str, "result": {...}}.
```

### Function-calling template (when function calling is enabled)

```json
{
  "name": "extract_price",
  "description": "Extracts price and returns structured JSON",
  "parameters": {
    "type": "object",
    "properties": {
      "text": {"type": "string"}
    },
    "required": ["text"]
  }
}
```

Agent instruction: Only return the function call payload when invoking the function. Do not produce other text.

### Evaluation / Instrumentation plan (brief)

- Metrics: exact-match rate on `value_eur` (within tolerance), parsing failure rate (non-JSON or missing fields), runtime latency percentiles (p50, p95), and average confidence.
- A/B test design: run N=200 inputs per variant (A and B). Compute exact-match within 1e-3 tolerance and compare via two-proportion z-test (alpha=0.05). Measure latency and failure-rate tradeoffs.
- Logging: store model input, model raw output, parsed JSON, validation pass/fail, and any normalized results. Label human-reviewed edge-cases for retraining.
