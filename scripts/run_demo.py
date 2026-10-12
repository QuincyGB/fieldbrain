#!/usr/bin/env python3
"""Run the FieldBrain demo scenario against a running server.

Usage:
    uvicorn app.main:app --port 8000        # in one terminal
    python scripts/run_demo.py              # in another

Scenario (single, complete):
  1. Ask about fault E47 compressor short-cycling -> sourced answer + checklist.
  2. Ask a question the documents cannot answer -> escalation hand-off summary.
"""
import json
import sys

import httpx

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"

QUESTIONS = [
    "The rooftop unit keeps short-cycling and shows fault code E47. What should I check first?",
    "What refrigerant type does the RTU-9000 use, and what is its factory charge weight in kilograms?",
]

# trust_env=False: ignore any proxy env vars; the demo server is local.
client = httpx.Client(trust_env=False, timeout=30.0)

for q in QUESTIONS:
    print("=" * 78)
    print("TECH:", q)
    resp = client.post(f"{BASE}/api/ask", json={"question": q})
    data = resp.json()
    print(f"[{data['type']} | mode={data.get('mode')} | confidence={data.get('confidence')}]")
    if data["type"] == "handoff":
        esc = data["escalation"]
        print("HAND-OFF SUMMARY:", esc["summary"])
        print("ROUTE:", esc["suggested_route"])
    else:
        print(data["answer"][:600])
        print("CHECKLIST:")
        for step in data.get("checklist", []):
            print("  -", step)
        print("SOURCES:", ", ".join(f"{s['document']} / {s['section']}"
                                    for s in data.get("sources", [])))
    print()
