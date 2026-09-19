# ⚡ LabSim Coach

A browser-based electronics lab where students build circuits on a virtual breadboard,
run a real DC simulation, and get **Socratic AI coaching** that guides them to the fix
instead of handing over the answer.

Built for the **AWS Zero to Shipped Hackathon** · Category: `#social-good` (Education) · Lane: `#community`

## Quick start

1. **Backend:** `cd backend && sam build && sam deploy --guided` → copy the `ApiBaseUrl`.
2. **Frontend:** paste that URL into `frontend/config.js`.
3. **Ship:** host `frontend/` via AWS Amplify or S3+CloudFront.

👉 Full step-by-step in **[DEPLOY.md](DEPLOY.md)**.

## Project layout

```
labsim-coach/
├── backend/
│   ├── template.yaml        # AWS SAM: API Gateway + 2 Lambdas + Bedrock IAM
│   ├── solve/app.py         # MNA DC circuit solver (numpy)
│   └── coach/app.py         # Socratic AI tutor (Amazon Bedrock)
├── frontend/
│   ├── index.html           # SVG breadboard + coach UI (no build step)
│   └── config.js            # set your API URL here
├── amplify.yml              # Amplify static-hosting config
├── DEPLOY.md                # deployment guide (start here)
├── DEVLOG.md                # submission story + dev log for Builder Center
└── README.md
```

## Tech

Vanilla JS + SVG · AWS Lambda (Python 3.12) · API Gateway HTTP API ·
Amazon Bedrock (Claude 3.5 Sonnet) · AWS SAM · Amplify / S3+CloudFront.

## What v1 supports

Battery · Resistor · LED · Switch · Wires. Detects reverse-biased LEDs, open switches,
and under-driven LEDs. The AI coach explains *why* — Socratically.
