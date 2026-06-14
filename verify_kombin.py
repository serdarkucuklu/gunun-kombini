import os
import sys
import json

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def verify_files():
    print("--- Verifying Project Files ---")
    required = ["index.html", "style.css", "app.js", "data.json", "agent.py"]
    all_ok = True
    for f in required:
        if os.path.exists(f):
            print(f"[OK] File exists: {f}")
        else:
            print(f"[FAIL] Missing file: {f}")
            all_ok = False
    return all_ok

def run_agent_test():
    print("\n--- Running agent.py Local Dry Run ---")
    import agent
    
    # 1. Test Weather Fetching
    print("Testing Open-Meteo weather fetch for Istanbul...")
    try:
        temp, condition, icon = agent.get_weather(41.0082, 28.9784)
        print(f"[OK] Weather fetched successfully: {temp}, {condition}, icon: {icon}")
    except Exception as e:
        print(f"[FAIL] Weather fetch failed: {e}")
        return False

    # 2. Verify data.json structure
    print("Reading data.json content...")
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"[OK] data.json read successfully. Last updated: {data.get('last_updated')}")
        
        # Verify structure
        if "cities" in data and "istanbul" in data["cities"]:
            ist = data["cities"]["istanbul"]
            if "female" in ist and "male" in ist and "weather" in ist:
                print("[OK] data.json structure is valid.")
            else:
                print(f"[FAIL] data.json missing female/male keys: {ist.keys()}")
                return False
        else:
            print("[FAIL] data.json missing cities or istanbul keys.")
            return False
    except Exception as e:
        print(f"[FAIL] Could not read data.json: {e}")
        return False

    # 3. Test Curation Loop (Dry Run with real API call)
    print("\nRunning single city curation via Gemini (Dry Run)...")
    try:
        comb = agent.generate_combination("İzmir", "22°C", "Açık ve Güneşli")
        if comb and "female" in comb and "male" in comb:
            print("[OK] Gemini successfully returned valid structured combination JSON.")
            print(f"  Female Theme: {comb['female'].get('theme')}")
            print(f"  Male Theme: {comb['male'].get('theme')}")
            print(f"  Female Items Count: {len(comb['female'].get('items', []))}")
            return True
        else:
            print(f"[FAIL] Gemini returned invalid or empty combination structure: {comb}")
            return False
    except Exception as e:
        print(f"[FAIL] Exception during Gemini curation test: {e}")
        return False

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    files_ok = verify_files()
    if not files_ok:
        sys.exit(1)
        
    test_ok = run_agent_test()
    if test_ok:
        print("\nALL TESTS PASSED! Günün Kombini Agent is fully verified and functional.")
        sys.exit(0)
    else:
        print("\nTESTS FAILED. Please check API credentials and log errors.")
        sys.exit(1)
