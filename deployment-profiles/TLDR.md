# TLDR Deployment Profile — Applied AI Engineer (Claude Skills + Agents)

This is a job-specific overlay for the **Always-On Automation Runtime** demo repo. The core repo demonstrates reliability/composability patterns (idempotency, persistent state, guardrails, operator controls). This page maps that foundation to TLDR’s needs: **a production Skills library + autonomous agents that non-technical teammates can compose.**

## 10-second fit
- Build a **Skills Library**: modular, permissioned connectors ("Claude Skills") for HubSpot, Google Drive, Slack, Sponsy (and internal data sources)
- Ship **autonomous agents** (often n8n-run) that use those skills daily for sales/marketing/ops tasks
- Own the **AI dev environment**: templates, patterns, evals, and docs so anyone can start building within an hour
- Design for **composability + safety**: structured outputs, policy checks, approvals for high-impact actions, audit logs

## How the runtime maps to TLDR
**Runtime layer (this repo):**
- Webhook/event ingestion (n8n triggers, Slack events, scheduled jobs)
- Validation/auth + idempotency (retry-safe tool calls)
- Persistent state (deterministic behavior + progress tracking)
- Guardrails (allowlists, rate limits, approval gates, kill switch)
- Connector interface (clean I/O boundaries for skills)
- Operator controls (health/status, safe modes, runbooks)

**Skills library (what you add):**
- `hubspot.search_contacts`, `hubspot.update_property`, `hubspot.create_task`
- `drive.search_files`, `drive.read_doc`, `drive.write_doc`
- `slack.post_message`, `slack.create_channel`, `slack.lookup_user`
- `sponsy.fetch_campaigns`, `sponsy.generate_proposal_draft`, `sponsy.update_status`

**Agent runners (what you add):**
- n8n workflows that call the runtime’s skills with structured inputs/outputs
- escalation paths to humans when confidence is low or impact is high

## Example Claude Skills (primitives)
Each skill is small, typed, and permissioned. Outputs are structured so downstream steps can reliably compose.

### 1) HubSpot: Lead enrichment + hygiene
**Input**
```json
{"email":"jane@company.com","company":"Company","fields":["title","size","industry"],"mode":"enrich_then_update"}
```
**Output**
```json
{"contact_id":"123","updates_applied":["industry","size"],"missing":["title"],"needs_review":true}
```

### 2) Competitive research snapshot
**Input**
```json
{"company":"Acme","sources":["web","internal_notes"],"focus":["positioning","pricing","case_studies"]}
```
**Output**
```json
{"summary":"...","citations":[{"source":"web","url":"..."},{"source":"internal","doc_id":"..."}],"confidence":0.76}
```

### 3) Proposal draft generator (Drive + Sponsy)
**Input**
```json
{"campaign_id":"cmp_456","audience":"CIOs","tone":"concise","include_pricing":false}
```
**Output**
```json
{"drive_doc_id":"1AbC...","sections":["overview","audience","deliverables"],"open_questions":["pricing tier?"]}
```

## Autonomous agents to ship first (high ROI)
1) **Lead Enrichment Agent (daily)**
   - Pull new leads -> enrich -> update HubSpot -> flag low-confidence records -> Slack summary

2) **Proposal Draft Agent (on demand)**
   - Given a Sponsy campaign -> draft proposal in Drive -> post link to Slack -> route for approval

3) **CRM Insight Agent (weekly)**
   - Analyze pipeline changes -> detect anomalies/data hygiene issues -> create HubSpot tasks -> Slack report

4) **Content Research Agent (daily)**
   - Collect topic briefs + sources -> produce structured research packets for writers

## Development environment (make it reproducible)
- `templates/skill/` scaffolding: schema, tests, mock fixtures, permissions
- local runner + mock connectors for fast iteration (no real side effects)
- eval harness: golden inputs/outputs for prompts + retrieval regressions
- docs: “How to build a new skill in 30 minutes”

## Safety / escalation rules (non-negotiable)
- **Structured outputs** + validation on every tool call
- **Approvals** for irreversible actions (CRM mass updates, campaign status changes)
- **Rate limits** + allowlists per connector
- **Audit trail** for every action
- **Kill switch** and safe degraded mode when dependencies fail

## 30/60/90 plan (what I’d ship)
**30 days:** skill scaffolding + 5–8 core skills (HubSpot/Slack/Drive), n8n patterns, basic evals, docs  
**60 days:** 2–3 daily agents in prod, role-based permissions, audit logs, better monitoring/alerts  
**90 days:** skills catalog is self-serve for non-technical teams; agents cover core revenue workflows; regression tests prevent breakage
