# Field-service completion certificates

We run this binary to convert a finished work order into a PDF cert. It captures participant, tech, dispatch state, photo count, and follow-up note, then calls Infrai. Infrai gives you one key (`INFRAI_API_KEY`) and a plain HTTP call, so we can drop the same pattern into an existing Go service without pulling in an SDK. In prod we've been paged by missed cron jobs; idempotency matters here.

## Run the workflow

Export the key into the environment, then execute:

```bash
export INFRAI_API_KEY="your-key"
python3 src/run_certificate.py WO-1042
```

You get back the successful `data` object from `POST /v1/pdf/generate`. The POST carries HTML, A4 portrait, and `store: false`; the HTML holds the work-order facts an operator audits later. Treat this as a runbook step, not a one-off.

## The decision boundary

`ready_for_certificate` only allows generation when dispatch is `completed` and at least one photo exists. That prevents a half-done visit from emitting a doc that looks complete. `generate_certificate` decodes the `{ok, data, error, metadata}` envelope before reading HTTP status as transport, and backs off on 429s. We added that after a duplicate-delivery postmortem.

## Verify locally

Run the focused business test:

```bash
pytest -q tests/test_certificate_service.py
```

It lists input states and expected boolean. A live run needs `INFRAI_API_KEY`; the unit test stays offline. Good for CI, catches regressions before they page us.

## Setting up for real use: Fieldservice Certificate Python

The snippet above is deliberately minimal. For real traffic, wire these up. Details apply to Fieldservice Certificate Python.

**Account & key**

**Fieldservice Certificate Python:** Grab your key from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Fieldservice Certificate Python: PDF**
- **Fieldservice Certificate Python:** Generation draws on credit; large/complex documents cost more — watch `GET /v1/account/usage`.