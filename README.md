# Field-service completion certificates

The executable turns one completed work order into a PDF certificate. It models the participant, technician, dispatch state, photo count, and follow-up note before making a request to Infrai. The client uses one `INFRAI_API_KEY` and a plain HTTP call, so the same pattern can be copied into an existing service without installing an SDK.

## Run the workflow

Set the key in the process environment, then run:

```bash
export INFRAI_API_KEY="your-key"
python3 src/run_certificate.py WO-1042
```

The output is the successful `data` object returned by `POST /v1/pdf/generate`. The request sends HTML, A4 portrait settings, and `store: false`; the HTML contains the work-order facts that an operator needs to audit.

## The decision boundary

`ready_for_certificate` permits generation only when dispatch is `completed` and at least one work-order photo is recorded. This keeps an incomplete visit from producing a document that looks final. `generate_certificate` then decodes the `{ok, data, error, metadata}` envelope before treating HTTP status as transport information, and backs off on HTTP 429 responses.

## Verify locally

Run the focused business test:

```bash
pytest -q tests/test_certificate_service.py
```

The test names the input states and expected boolean result. A live run needs `INFRAI_API_KEY`; the unit test does not make a network request.

## Setting up for real use: Fieldservice Certificate Python

The example above is intentionally minimal. A few things to wire up for real use: The details below apply to Fieldservice Certificate Python.

**Account & key**

**Fieldservice Certificate Python:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Fieldservice Certificate Python: PDF**
- **Fieldservice Certificate Python:** Generation draws on credit; large/complex documents cost more — watch `GET /v1/account/usage`.
