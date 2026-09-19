"""LabSim Coach — /solve Lambda
Modified Nodal Analysis (MNA) DC circuit solver.
Supports: battery, resistor, LED (diode model), wire, switch.
No external deps beyond numpy (bundled as a Lambda layer or in the package).
"""
import json
import numpy as np

R_ON = 15.0      # LED on-resistance (ohms)
I_LIT = 1e-3     # >= 1 mA => visibly lit
GMIN = 1e-9      # tiny leak-to-ground to stabilize floating nodes


def solve_circuit(circuit):
    comps = circuit.get("components", [])
    nodes = circuit.get("nodes", [])

    # --- union-find: merge nodes joined by wires / closed switches ---
    parent = {}

    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        parent[find(a)] = find(b)

    for n in nodes:
        parent.setdefault(n, n)
    for c in comps:
        if c["type"] == "wire" or (c["type"] == "switch" and c.get("closed")):
            union(c["a"], c["b"])

    reps = sorted(set(find(n) for n in nodes))
    batteries = [c for c in comps if c["type"] == "battery"]
    if not batteries:
        return {"ok": False, "error": "no_source",
                "reason": "There's no battery in the circuit, so nothing can drive a current."}

    ground = find(batteries[0]["b"])          # negative terminal of first battery = ground
    free = [r for r in reps if r != ground]
    idx = {r: i for i, r in enumerate(free)}
    N = len(free)

    leds = [c for c in comps if c["type"] == "led"]
    led_on = {c["id"]: True for c in leds}     # initial guess: all conducting

    def build_and_solve(led_state):
        M = len(batteries)
        A = np.zeros((N + M, N + M))
        z = np.zeros(N + M)
        for r in free:
            A[idx[r], idx[r]] += GMIN

        def gstamp(a, b, g):
            a, b = find(a), find(b)
            if a != ground:
                A[idx[a], idx[a]] += g
            if b != ground:
                A[idx[b], idx[b]] += g
            if a != ground and b != ground:
                A[idx[a], idx[b]] -= g
                A[idx[b], idx[a]] -= g

        def isrc(a, b, i):
            a, b = find(a), find(b)
            if a != ground:
                z[idx[a]] -= i
            if b != ground:
                z[idx[b]] += i

        for c in comps:
            if c["type"] == "resistor":
                gstamp(c["a"], c["b"], 1.0 / max(float(c["value"]), 1e-9))
            elif c["type"] == "led" and led_state[c["id"]]:
                g = 1.0 / R_ON
                gstamp(c["a"], c["b"], g)
                isrc(c["a"], c["b"], -g * c.get("vf", 2.0))

        for k, b in enumerate(batteries):
            row = N + k
            pa, pb = find(b["a"]), find(b["b"])
            if pa != ground:
                A[idx[pa], row] += 1
                A[row, idx[pa]] += 1
            if pb != ground:
                A[idx[pb], row] -= 1
                A[row, idx[pb]] -= 1
            z[row] = float(b["value"])

        try:
            x = np.linalg.solve(A, z)
        except np.linalg.LinAlgError:
            return None
        v = {ground: 0.0}
        for r in free:
            v[r] = float(x[idx[r]])
        return v

    # iterate LED on/off states until self-consistent
    v = None
    for _ in range(len(leds) + 2):
        v = build_and_solve(led_on)
        if v is None:
            return {"ok": False, "error": "singular",
                    "reason": "The circuit can't be solved — check for a short across the battery."}
        changed = False
        for c in leds:
            va, vb = v[find(c["a"])], v[find(c["b"])]
            vf = c.get("vf", 2.0)
            want = (va - vb) > vf * 0.6 if not led_on[c["id"]] else (va - vb - vf) / R_ON > 0
            if want != led_on[c["id"]]:
                led_on[c["id"]] = want
                changed = True
        if not changed:
            break

    node_v = {n: round(v[find(n)], 4) for n in nodes}
    currents, led_states, reasons = {}, {}, []
    for c in comps:
        va, vb = v[find(c["a"])], v[find(c["b"])]
        if c["type"] == "resistor":
            currents[c["id"]] = round((va - vb) / max(float(c["value"]), 1e-9), 6)
        elif c["type"] == "led":
            i = (va - vb - c.get("vf", 2.0)) / R_ON if led_on[c["id"]] else 0.0
            currents[c["id"]] = round(max(i, 0.0), 6)
            if led_on[c["id"]] and i >= I_LIT:
                led_states[c["id"]] = "on"
            else:
                led_states[c["id"]] = "off"
                if (va - vb) < 0:
                    reasons.append(f"{c['id']} is reverse-biased — its anode is at a lower voltage "
                                   f"than its cathode. Try flipping the LED around.")
                else:
                    reasons.append(f"{c['id']} isn't getting enough voltage/current to light. Check "
                                   f"for an open switch, a missing wire, or a resistor that's too large.")

    return {"ok": True, "node_voltages": node_v, "currents": currents,
            "leds": led_states, "reasons": reasons}


CORS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Methods": "OPTIONS,POST",
}


def handler(event, context):
    if event.get("httpMethod") == "OPTIONS":
        return {"statusCode": 200, "headers": CORS, "body": ""}
    try:
        body = json.loads(event.get("body") or "{}")
        result = solve_circuit(body)
        return {"statusCode": 200, "headers": {**CORS, "Content-Type": "application/json"},
                "body": json.dumps(result)}
    except Exception as e:  # noqa
        return {"statusCode": 500, "headers": {**CORS, "Content-Type": "application/json"},
                "body": json.dumps({"ok": False, "error": "server", "reason": str(e)})}
