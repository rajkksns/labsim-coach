# ⚡ LabSim Coach — The Virtual Electronics Lab That Teaches, Not Tells

**Category:** `#social-good` (Education)  ·  **Lane:** `#community`
**Live app:** https://main.d1ydraybtlnyxz.amplifyapp.com
**Built with:** Amazon Q Developer CLI + AWS SAM + Lambda + API Gateway + Amazon Bedrock + AWS Amplify

---

## The problem I watch every single week

I teach Electronics & Communication Engineering. Every lab session follows the same painful
pattern: a student wires up a circuit, the LED doesn't light, and instead of *reasoning* about
why, they start swapping parts at random — "maybe this resistor, maybe flip that." The single
most valuable moment in an engineering education — the "*ohhh, that's why current isn't
flowing*" — gets lost in guesswork. And with 60+ students and one of me, I can't be at every
bench at the right second.

**LabSim Coach is the tutor I wish I could clone.**

## What it does

Students build a circuit on a virtual breadboard — battery, resistor, LED, switch, wires —
right in the browser. They hit **Run**, and a real circuit simulator computes what's actually
happening: node voltages, branch currents, whether each LED lights. Then an AI coach explains
*why* — Socratically. It never hands over the answer. It asks the question that makes the
student think.

Try it yourself: open the [live app](https://main.d1ydraybtlnyxz.amplifyapp.com), click
**Load Example → Run Simulation**, then ask the coach *"why won't my LED light?"*

> **Correct circuit →** the LED glows and the coach celebrates, then poses a "what if?" extension.
>
> **Broken circuit (reversed LED / open switch) →** the LED stays dark, the app pinpoints the
> fault, and the coach nudges: *"Is your LED perhaps in backwards? What does current direction
> tell you?"*

That difference — **detecting the mistake AND coaching the fix** — is the whole point.

## Why this is more than a chatbot (Technical Innovation)

The simulator isn't a canned animation. It's a genuine **Modified Nodal Analysis (MNA)** DC
solver:
- Builds the conductance matrix from the student's actual circuit graph
- Models the LED as a real diode (forward-voltage drop + on-resistance) and iterates the
  on/off state until self-consistent
- Uses union-find to merge wired nodes, and a gmin leak-to-ground so even open/floating
  circuits solve cleanly instead of crashing
- Detects the classic beginner faults: reverse-biased LED, open switch, under-driven LED

The AI coach then reasons over that **structured solver output** (voltages, currents, detected
faults) — so its hints are specific and correct, not generic filler. It's grounded in the
math, not hallucinating.

## Architecture (Implementation Quality)

```
Browser (SVG breadboard, vanilla JS)
        │
        ├─ POST /solve ──►  API Gateway ─►  Lambda  (pure-Python MNA solver, no deps)
        │
        └─ POST /coach ──►  API Gateway ─►  Lambda  ─►  Amazon Bedrock
                                                        (Claude Haiku 4.5, Converse API)
Hosted on AWS Amplify (CI/CD from GitHub) — public HTTPS URL.
```

- **100% serverless** — fits the Free Tier for classroom-scale traffic; Bedrock is a few cents.
- **Infrastructure as Code** via AWS SAM (`template.yaml`) — one-command reproducible deploy.
- **Least-privilege IAM** — the coach Lambda only holds `bedrock:InvokeModel`.
- **Model-agnostic coach** — built on Bedrock's Converse API, so swapping models is a one-line
  parameter change.

## How the coding agent helped me ship (and a real war story)

I connected **Amazon Q Developer CLI** to my AWS account and drove the build and deployment
through it. Concretely, the agent:

- Ran `aws sts get-caller-identity` and inspected my **`labsim-coach`** CloudFormation stack —
  autonomously adapting when its first tool call failed, locating my AWS CLI, and re-running via
  the correct path (see proof screenshot).
- Helped scaffold the SAM template (HTTP API + two Lambdas), reason about IAM, and debug deploys.

**The most instructive moment:** the coach initially failed with `ResourceNotFoundException:
This model version has reached the end of its life.` The fix — discovered by querying Bedrock
directly — was that bare model IDs (`amazon.nova-lite-v1:0`) are dead for on-demand calls; you
must use a **cross-region inference profile ID** with a `us.` prefix. Listing them with
`aws bedrock list-inference-profiles` revealed `us.anthropic.claude-haiku-4-5-20251001-v1:0`,
and pairing that with the **Converse API** (which normalizes request/response across model
families) made the coach robust to future model swaps. That's the kind of real-world
cloud-debugging I now bring straight back to my classroom.

## Community impact (this is the Community lane)

LabSim Coach is built for a group I belong to: my own ECE students. It's anonymous (no login),
works on a phone at the lab bench, and scales me from one professor to sixty simultaneous
"benchmates." My plan is to run it live in the next lab cohort and measure time-to-understanding
on the LED-doesn't-light exercise.

⟨After your classroom test, add real numbers + a student quote here.⟩

## AWS services used

Amazon Q Developer CLI · AWS Lambda · Amazon API Gateway (HTTP API) · Amazon Bedrock
(Claude Haiku 4.5) · AWS SAM · AWS Amplify Hosting · IAM

## Links

- **Live app:** https://main.d1ydraybtlnyxz.amplifyapp.com
- **Source:** https://github.com/rajkksns/labsim-coach
- **Proof of agent → AWS connection:** see attached screenshots

---

*Tags: `#social-good` `#community`*
