# FieldBrain — ACT III submission copy, OFFLINE-HONEST version

Prepared Fri Oct 16, 2026 by Ren. Use this version if the AMD Developer
Cloud credits activation has not landed by filing time (Sat Oct 17 night).
The claim was submitted Oct 16 and AMD said activation instructions arrive
by email within 3 business days — counted from Fri Oct 16, that can land
Tue Oct 20, AFTER the Sun Oct 18, 11:00 AM EDT close. So the expected case
is: file with the offline demo and describe it exactly as it is.

Supersedes the long description in
`~/workspace/hackathons/weekend-20261017-18-run-sheet.md`, whose draft copy
claims a live vLLM endpoint on AMD Developer Cloud and Evolus building
blocks. Do NOT file that wording unless both are actually true at filing
time (endpoint live + Evolus workspace created with blocks wired). The
Evolus event code still had not appeared anywhere as of Oct 16 — if it
still hasn't by Sat night, the Evolus partner-track claim comes out too
(already removed below).

## Fields

- **Title:** FieldBrain — Technician Manual Q&A with Honest Hand-Off
- **Selected challenge:** Track 1 — Intelligent Industry
- **Short description:** Field technicians ask plain-language questions and
  get answers grounded in their own equipment manuals and maintenance
  history — with named sources, the manual's own action checklist, and an
  honest escalation hand-off instead of a guess when the docs can't answer.
- **Long description:** Field technicians lose time digging through
  equipment manuals and old work orders, and junior techs miss the
  recommended next action. The documents exist — nobody can query them from
  a rooftop. FieldBrain indexes uploaded manuals and maintenance logs and
  answers a question like "compressor short-cycling, fault code E47 — what
  do I check first?" with (1) an answer grounded in the retrieved sections,
  citing document + section, (2) a recommended action checklist extracted
  from the manual's own procedure, in order, and (3) when retrieval
  confidence is low, a structured hand-off summary (question, what was
  searched, closest matches, suggested route) for a senior tech or
  dispatcher. The demo build runs in offline demo mode: retrieval and
  answer assembly are local (BM25 over the indexed corpus), so it works
  with no external model call. The production architecture targets an
  open model served by vLLM on AMD Developer Cloud (ROCm) behind the same
  API; the grounding, checklist, and hand-off behaviour are identical in
  both modes, because they live in the retrieval layer, not the model.
  Built by a practitioner with 10 years managing residential and
  commercial service accounts — the workflow is the one he lived.
- **Tech tags:** FastAPI, BM25, RAG, Docker, Python, vLLM (target),
  ROCm (target), AMD Developer Cloud (target)
- **Demo scenario:** the bundled two-question script in the repo
  (`scripts/run_demo.py`): Q1 E47 short-cycling → sourced answer +
  checklist (corroborated by the 2026-03-14 maintenance log); Q2
  refrigerant type/charge weight → docs deliberately don't state it →
  confidence gate fires → hand-off summary. Pacing per the standing video
  rules (~1.6 w/s raw opening, ≤~2.0 w/s body, one complete file).
- **Pitch outline (5 beats):** (1) time lost searching manuals in the
  field; (2) grounded answer with sources; (3) checklist = the manual's
  own procedure; (4) honest hand-off as the differentiator; (5) AMD
  target architecture (vLLM/ROCm) and what changes when credits activate.

## Saturday checklist (Oct 17)

- [ ] Re-check email for the AMD activation message; if it landed, the
      original run-sheet copy can be used instead — verify the endpoint
      is actually live first.
- [ ] Re-check for the Evolus event code (LabLab Discord / email); only
      re-add the partner-track claim if a workspace exists with ≥2 blocks
      wired.
- [ ] Public GitHub repo — still local-only as of Oct 16; needs Quincy's
      yes (already asked in earlier updates, still pending).
- [ ] Demo video recorded from `scripts/run_demo.py` (single scenario).
- [ ] File on lablab.ai Saturday night — never Sunday morning.
