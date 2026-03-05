import subprocess
import time
import datetime
import os

def run_to_the_limit():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    duration_hours = 3.5 # Run for 3.5 hours
    start_time = datetime.datetime.now()
    end_time = start_time + datetime.timedelta(hours=duration_hours)
    
    print(f"Master Orchestrator started at {start_time.strftime('%H:%M:%S')}.")
    print(f"Training will run for {duration_hours} hours, until {end_time.strftime('%H:%M:%S')}...")
    
    scripts = [
        "training/tool_distiller.py",
        "training/cerebro_train.py"
    ]
    
    audit_script = "training/super_audit.py"
    
    while True:
        now_dt = datetime.datetime.now()
        
        if now_dt >= end_time:
            print(f"Duration of {duration_hours} hours reached! Stopping training cycle.")
            break
            
        for script in scripts:
            script_path = os.path.join(root, script)
            print(f"Processing cognitive block: {script}")
            try:
                subprocess.run(["python", script_path], check=True)
            except Exception as e:
                print(f"Error in block {script}: {e}")
        
        print(f"Cycle finished. Waiting for next block... (Current time: {datetime.datetime.now().strftime('%H:%M:%S')})")
        time.sleep(120) # 2 minute pause
        
    print("TRIGGERING SUPER AUDIT & STRESS TEST...")
    try:
        subprocess.run(["python", os.path.join(root, audit_script)], check=True)
        print("SUPER AUDIT COMPLETED.")
    except Exception as e:
        print(f"Error during Audit: {e}")

if __name__ == "__main__":
    run_to_the_limit()
