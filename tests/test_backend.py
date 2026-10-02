"""
Zero-Dependency Integration Test Suite
"""
import urllib.request
import json
import time

BASE = "http://localhost:8000/api/v1"

def api_request(url, method="GET", payload=None, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    data_bytes = json.dumps(payload).encode("utf-8") if payload else None
    req = urllib.request.Request(url, data=data_bytes, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req, timeout=5) as res:
            raw = res.read().decode("utf-8")
            return res.getcode(), json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8")
        try:
            body = json.loads(raw) if raw else {"detail": e.reason}
        except Exception:
            body = {"detail": raw or str(e)}
        return e.code, body
    except Exception as e:
        return 500, {"detail": str(e)}

def test_health():
    code, data = api_request("http://localhost:8000/health")
    assert code == 200, f"Health check failed: {code}"
    print("[PASS] Health checkpoint verified.")

def test_login():
    payload = {"username": "admin", "password": "admin123"}
    code, data = api_request(f"{BASE}/auth/login", "POST", payload)
    assert code == 200, f"Login failed ({code}): {data}"
    assert "access_token" in data, "Token missing from response"
    print("[PASS] System authentication verified.")
    return data["access_token"]

def test_grid_state(token):
    code, data = api_request(f"{BASE}/grid/state", "GET", token=token)
    assert code == 200, f"Grid state failed ({code}): {data}"
    print("[PASS] Digital Twin Grid status reporting validated.")

def test_fault_injection(token):
    payload = {
        "component_id": "LINE_7",
        "fault_type": "TRANSMISSION_LINE_FAILURE",
        "severity": 0.85,
        "duration": 60
    }
    code, data = api_request(f"{BASE}/faults/inject", "POST", payload, token=token)
    assert code == 200, f"Fault injection failed ({code}): {data}"
    assert "fault_id" in data, "fault_id missing from response"
    print(f"[PASS] Anomaly injection pipeline operational: {data['fault_id']}")
    return data["fault_id"]

def test_recovery_plans(fault_id, token):
    code, data = api_request(f"{BASE}/recovery/plans?fault_id={fault_id}", "GET", token=token)
    assert code == 200, f"Recovery plans failed ({code}): {data}"
    assert len(data) >= 1, "No recovery plans generated"
    print(f"[PASS] Self-healing logic generated {len(data)} constraint-aware plans.")

def test_analytics(token):
    code, data = api_request(f"{BASE}/analytics/summary", "GET", token=token)
    assert code == 200, f"Analytics failed ({code}): {data}"
    print("[PASS] Analytic telemetry and event history checked.")

if __name__ == "__main__":
    print("=" * 60)
    print("  GRIDSHIELD SYSTEM INTEGRATION & COMPLIANCE VERIFICATION  ")
    print("=" * 60)
    try:
        test_health()
        tok = test_login()
        test_grid_state(tok)
        fid = test_fault_injection(tok)
        time.sleep(1)
        test_recovery_plans(fid, tok)
        test_analytics(tok)
        print("-" * 60)
        print("Verification complete: ALL SYSTEMS PASSED COMPLIANCE STAGE.")
        print("=" * 60)
    except AssertionError as e:
        print(f"[FAIL] Check failed: {e}")
    except Exception as e:
        print(f"[CRITICAL ERROR] Test suite aborted: {e}")
