# 🚀 LabSim Coach — Deployment Guide (Zero to Shipped)

This guide takes you from an empty AWS account to a **live public URL** the judges can reach.
Follow it top to bottom. Estimated time: **45–75 min** the first time.

> **Hackathon requirement mapping**
> - ✅ Coding agent connected to AWS console → **Step 1** (capture proof screenshot)
> - ✅ Live app on AWS, public URL → **Steps 4–6**
> - ✅ Category `#social-good` · Lane `#community` → set in Builder Center (Step 8)
> - ✅ Builder Center writeup + dev log → **Step 8** (+ see `DEVLOG.md`)

---

## Prerequisites (install once)

| Tool | Check it works | Install |
|---|---|---|
| AWS account | — | https://aws.amazon.com/free |
| AWS CLI v2 | `aws --version` | https://aws.amazon.com/cli |
| AWS SAM CLI | `sam --version` | https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html |
| Python 3.12 | `python --version` | https://python.org |
| A coding agent | — | **Amazon Q Developer CLI** (recommended) or Kiro |

---

## STEP 1 — Connect your coding agent to the AWS console (REQUIRED PROOF)

This is a graded submission requirement. Do it first and screenshot it.

**Option A — Amazon Q Developer CLI (recommended, free tier):**
```bash
# Install Q Developer CLI, then:
q login
# choose "Use with AWS Builder ID" or your IAM Identity Center
q doctor          # verifies the connection
```
Then run any command that touches your account so the agent is demonstrably wired in:
```bash
q chat "list my S3 buckets using the AWS CLI and explain the output"
```

**Option B — Kiro / Claude Code with AWS MCP:** connect the AWS MCP server and run a
read-only call (e.g. `aws sts get-caller-identity`).

📸 **PROOF TO CAPTURE NOW:**
1. Screenshot of `aws sts get-caller-identity` returning your account ID.
2. Screenshot of your coding agent running an AWS command successfully.
Save both to `submission/proof/`. You'll upload them to Builder Center in Step 8.

---

## STEP 2 — Configure AWS credentials

```bash
aws configure
# Access key, secret, default region: us-east-1, output: json
aws sts get-caller-identity     # should print your account ID
```

> Use **us-east-1** — it has the widest Bedrock model availability.

---

## STEP 3 — Enable the Bedrock model (one-time, ~2 min)

1. Open the AWS Console → **Amazon Bedrock** → **Model access**.
2. Click **Enable specific models** → enable **Anthropic Claude 3.5 Sonnet**.
3. Wait until status shows **Access granted** (usually instant).

> If Claude isn't available in your region/account, use `amazon.nova-lite-v1:0`
> and pass it as a parameter in Step 4. (The coach prompt works with Nova too.)

---

## STEP 4 — Deploy the backend (API + Lambdas)

From the `backend/` folder:
```bash
cd backend
sam build
sam deploy --guided
```
Answer the prompts:
- Stack name: `labsim-coach`
- Region: `us-east-1`
- Confirm changes: `Y`
- Allow SAM to create IAM roles: `Y`
- Disable rollback: `N`
- `SolveFunction` / `CoachFunction` may not have auth — say **Y** (public API is intended).
- Save arguments to config: `Y`

**To use a non-default Bedrock model:**
```bash
sam deploy --guided --parameter-overrides BedrockModelId=amazon.nova-lite-v1:0
```

When it finishes, copy the **`ApiBaseUrl`** from the Outputs, e.g.:
```
https://abc123xyz.execute-api.us-east-1.amazonaws.com
```

**Smoke-test the API:**
```bash
curl -s -X POST "$API/solve" -H "Content-Type: application/json" -d '{
 "nodes":["n1","n2","n3","n0"],
 "components":[
  {"id":"B1","type":"battery","a":"n1","b":"n0","value":9},
  {"id":"R1","type":"resistor","a":"n1","b":"n2","value":330},
  {"id":"D1","type":"led","a":"n2","b":"n3","vf":2},
  {"id":"W1","type":"wire","a":"n3","b":"n0"}]}'
# expect: {"ok":true,..., "leds":{"D1":"on"}, ...}
```

---

## STEP 5 — Point the frontend at your API

Edit `frontend/config.js`:
```js
window.LABSIM_CONFIG = { apiBaseUrl: "https://abc123xyz.execute-api.us-east-1.amazonaws.com" };
```

---

## STEP 6 — Ship the frontend live (pick ONE)

### 6A — AWS Amplify Hosting (easiest, gives HTTPS URL + CI/CD)
1. Push this project to a GitHub repo.
2. AWS Console → **Amplify** → **Create new app** → **Host web app** → connect GitHub.
3. Pick the repo/branch. Set **build settings → no build** (static). App root: `frontend`.
4. Deploy. Amplify gives you `https://main.xxxx.amplifyapp.com` — **this is your live public URL.** ✅

**amplify.yml** (already included at repo root) tells Amplify to just publish `frontend/`.

### 6B — S3 + CloudFront (pure static, no GitHub needed)
```bash
# create a bucket (globally unique name)
aws s3 mb s3://labsim-coach-<yourname> --region us-east-1
aws s3 website s3://labsim-coach-<yourname> --index-document index.html
aws s3 sync frontend/ s3://labsim-coach-<yourname> --acl public-read
# public URL:
echo "http://labsim-coach-<yourname>.s3-website-us-east-1.amazonaws.com"
```
For HTTPS (judges prefer it), put a **CloudFront** distribution in front of the bucket
(Console → CloudFront → Create distribution → origin = your S3 website endpoint).

---

## STEP 7 — Verify the SHIP GATE ✅

Open your live URL in an incognito window and confirm:
- [ ] Page loads with no console errors
- [ ] "Load Example" → "Run Simulation" lights the LED (green pill `D1: ON`)
- [ ] Reverse the LED or open the switch → LED shows OFF + a reason appears
- [ ] Ask the coach "why won't my LED light?" → you get a Socratic hint (not the full answer)
- [ ] URL is reachable from a phone / another network

If all boxes are checked, **you have passed the ship gate.**

---

## STEP 8 — Publish on AWS Builder Center

1. Go to your Builder Center profile → create the Zero to Shipped project.
2. Add:
   - **Title & description** (use the "Story" section of `DEVLOG.md`)
   - **Live app URL** (Step 6)
   - **Proof of agent connection** (screenshots from Step 1)
   - **Development process** — paste your `DEVLOG.md` narrative
   - **AWS services used** — Lambda, API Gateway, Bedrock, Amplify/S3+CloudFront
3. Add the two required tags: **`#social-good`** and **`#community`**.
4. Submit **before Oct 2, 11:59 PM PT.** Leave buffer!

---

## Cost & cleanup

- Everything here sits in the **AWS Free Tier** for a low-traffic demo (Lambda, API Gateway,
  S3, CloudFront). Bedrock charges per token — a classroom demo is a few cents.
- To tear down after judging:
```bash
sam delete --stack-name labsim-coach
aws s3 rb s3://labsim-coach-<yourname> --force   # if you used 6B
```

## Troubleshooting

| Symptom | Fix |
|---|---|
| `curl /solve` returns 500 | Check `sam logs -n SolveFunction --stack-name labsim-coach --tail` |
| Coach returns `AccessDenied` | Bedrock model not enabled (Step 3) or wrong region |
| Frontend can't reach API (CORS) | Confirm `config.js` URL has **no trailing slash**; CORS is already enabled in the template |
| Build error in Lambda | Solver is pure Python (no numpy) — a plain `sam build` works with no Docker |
| Coach says "coach_error" | Model ID mismatch — redeploy with the correct `BedrockModelId` |
