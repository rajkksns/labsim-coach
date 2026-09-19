"""LabSim Coach — /coach Lambda
Socratic AI tutor. Takes the student's circuit + solver result + their question,
and returns a hint that guides them toward the fix WITHOUT giving the full answer.

Uses Amazon Bedrock. Works with BOTH Amazon Nova (Converse API) and Anthropic
Claude — it uses the Bedrock `converse` API, which normalizes the request/response
format across model families, so you can switch BedrockModelId freely.
"""
import json
import os
import boto3

REGION = os.environ.get("BEDROCK_REGION", "us-east-1")
MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "amazon.nova-lite-v1:0")

bedrock = boto3.client("bedrock-runtime", region_name=REGION)

SYSTEM_PROMPT = """You are LabSim Coach, a warm, encouraging electronics lab tutor for
undergraduate students. You use the SOCRATIC method.

HARD RULES — never break these:
- NEVER give the complete solution or the exact component values to use.
- NEVER say "do exactly this." Instead, ask a guiding question or give ONE small hint.
- Keep replies SHORT: 2-4 sentences max. Encouraging, never condescending.
- Base every hint on the ACTUAL circuit state and solver results given to you.
- If the circuit already works, celebrate it and pose a "what if?" extension question.
- Use plain language a first-year student understands. Explain WHY, not just WHAT.
- If the student is close, nudge. If they're stuck, narrow the search space by one step.

You will receive: the circuit description, the solver's computed node voltages and
currents, any detected problems ("reasons"), and the student's question. Coach them."""


CORS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Methods": "OPTIONS,POST",
}


def build_user_message(payload):
    circuit = payload.get("circuit", {})
    result = payload.get("result", {})
    question = payload.get("question", "Why isn't my circuit working?")
    return (
        f"STUDENT QUESTION: {question}\n\n"
        f"CIRCUIT (components): {json.dumps(circuit.get('components', []))}\n\n"
        f"SOLVER RESULT:\n"
        f"  node_voltages: {json.dumps(result.get('node_voltages', {}))}\n"
        f"  currents (A): {json.dumps(result.get('currents', {}))}\n"
        f"  LED states: {json.dumps(result.get('leds', {}))}\n"
        f"  detected issues: {json.dumps(result.get('reasons', []))}\n\n"
        f"Give ONE Socratic hint (2-4 sentences). Do not reveal the full fix."
    )


def handler(event, context):
    if event.get("httpMethod") == "OPTIONS":
        return {"statusCode": 200, "headers": CORS, "body": ""}
    try:
        payload = json.loads(event.get("body") or "{}")
        user_msg = build_user_message(payload)

        # Bedrock Converse API — one format for Nova, Claude, Llama, etc.
        resp = bedrock.converse(
            modelId=MODEL_ID,
            system=[{"text": SYSTEM_PROMPT}],
            messages=[{"role": "user", "content": [{"text": user_msg}]}],
            inferenceConfig={"maxTokens": 300, "temperature": 0.6},
        )
        hint = resp["output"]["message"]["content"][0]["text"].strip()
        return {"statusCode": 200, "headers": {**CORS, "Content-Type": "application/json"},
                "body": json.dumps({"ok": True, "hint": hint})}
    except Exception as e:  # noqa
        return {"statusCode": 500, "headers": {**CORS, "Content-Type": "application/json"},
                "body": json.dumps({"ok": False, "error": "coach_error", "reason": str(e)})}
