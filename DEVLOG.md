# 🛠️ LabSim Coach — Development Log & Submission Story

> Copy the relevant parts of this file into your AWS Builder Center project.
> Fill in the ⟨bracketed⟩ bits as you build.

## The Story (Creativity & Storytelling — 25%)

I teach Electronics & Communication Engineering. Every lab, I watch students wire up a
circuit, get no LED, and start *guessing* — swapping parts at random instead of reasoning.
The best learning moment (understanding *why* current isn't flowing) gets lost.

**LabSim Coach** is the tutor I wish I could clone. Students build a circuit on a virtual
breadboard, run a real DC simulation, and a Socratic AI coach nudges them toward the fix —
it never hands over the answer, it asks the question that makes them think. It's built for
my own classroom (Community lane) and squarely serves the **Education** focus of Social Good.

## What it does (Community/Market Impact — 25%)

- Drag-and-drop virtual lab: battery, resistor, LED, switch, wires.
- Real Modified Nodal Analysis (MNA) solver computes node voltages, branch currents, LED state.
- Detects the classic beginner mistakes: reverse-biased LED, open switch, resistor too large.
- AI coach (Amazon Bedrock / Claude) gives Socratic hints grounded in the student's *actual* circuit.
- Anonymous, no login — works on any phone in the lab.

⟨After your classroom test, add real numbers here: "Deployed to N students across M lab
sessions; X circuits built; teacher-reported time-to-understanding dropped from … to …"⟩
⟨Add one student testimonial quote.⟩

## Technical Innovation & Originality (25%)

- The simulator isn't a canned animation — it's a genuine linear-circuit solver (MNA with a
  companion-model diode for the LED and iterative on/off resolution).
- The AI tutor reasons over structured solver output (voltages/currents/detected faults),
  so hints are specific and correct, not generic chatbot filler.
- Numerically hardened (gmin leak-to-ground) so floating/open circuits still solve cleanly.

## Implementation Quality (25%) — Architecture

```
Browser (SVG breadboard, vanilla JS)  →  CloudFront/Amplify (static hosting)
        │  POST /solve  ─────────────►  API Gateway → Lambda (numpy MNA solver)
        │  POST /coach  ─────────────►  API Gateway → Lambda → Amazon Bedrock (Claude)
```
- 100% serverless, fits Free Tier for demo traffic.
- Infrastructure as Code via AWS SAM (`backend/template.yaml`) — reproducible one-command deploy.
- CORS handled, IAM least-privilege (coach Lambda only gets `bedrock:InvokeModel`).

## How the coding agent helped me ship (REQUIRED)

I connected ⟨Amazon Q Developer CLI / Kiro⟩ to my AWS account and drove the build through it:

| Milestone | What I asked the agent | What it produced |
|---|---|---|
| Scaffold | "Create a SAM app with two Python Lambdas behind an HTTP API" | `template.yaml`, folder layout |
| Solver | "Write an MNA DC solver in numpy supporting battery/resistor/LED/wire/switch" | `solve/app.py` |
| Tutor | "Add a Lambda that calls Bedrock Claude with a Socratic system prompt" | `coach/app.py` |
| Deploy | "Run sam build && sam deploy --guided and fix any IAM errors" | Live API URL |
| Hosting | "Set up Amplify to host the static frontend from /frontend" | Live public URL |

⟨Paste 3–5 real prompts you used + a screenshot of the agent running an AWS command.⟩

## Proof of agent → AWS console connection

- `submission/proof/agent-connection.png` — coding agent running `aws sts get-caller-identity`
- `submission/proof/agent-deploy.png` — agent executing `sam deploy`

## AWS services used

Amazon Bedrock · AWS Lambda · Amazon API Gateway (HTTP API) · AWS SAM ·
AWS Amplify Hosting (or S3 + CloudFront) · IAM

## Tags

`#social-good`  `#community`

## Live app

⟨https://your-live-url⟩
