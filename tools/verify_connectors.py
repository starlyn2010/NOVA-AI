
import sys
import os

# Add project root to path
sys.path.append(r"C:\Users\DELL\Desktop\inventos\Nova")

def minimal_test():
    print("Starting Orchestrator Import Test...")
    try:
        from orchestrator import Orchestrator
        print("Import successful.")
        
        # Instantiate (this triggers engine map loading)
        # We mock __init__ parts if needed, but let's try full init first
        # We need to make sure we don't start listening threads in test
        
        o = Orchestrator()
        print("Orchestrator instantiated.")
        
        # Check if engines are serving
        print(f"Engine map keys: {list(o._engine_map.keys())}")
        
        expected = [
            "telegram", "whatsapp", "vscode", "pixazo", "canva", 
            "youtube", "github", "google", "notion", "spotify", 
            "wolfram", "trello", "vercel", "crawl"
        ]
        
        missing = [k for k in expected if k not in o._engine_map]
        
        if missing:
            print(f"FAIL: Missing engines in map: {missing}")
        else:
            print("SUCCESS: All 14 connectors registered.")

    except Exception as e:
        print(f"FAIL: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    minimal_test()
