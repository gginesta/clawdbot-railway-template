import subprocess
import json

def run_task():
    # Step 1: Install requests library
    try:
        subprocess.run(['pip', 'install', 'requests'], check=True)
        print("Requests library installed successfully")
    except subprocess.CalledProcessError:
        print("Failed to install requests library")
        return {"status": "error", "message": "Requests library installation failed"}

    # Step 2: Run daily standup script
    try:
        result = subprocess.run(['python3', '/data/workspace/daily_standup.py'], 
                                capture_output=True, 
                                text=True, 
                                check=True)
        
        # Step 3: Prepare JSON summary
        summary = {
            "status": "success",
            "stdout": result.stdout,
            "stderr": result.stderr
        }
        
        # Write JSON summary to file for Molty to parse
        with open('/data/workspace/daily_standup_summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        print("Daily standup script executed successfully")
        return summary
    
    except subprocess.CalledProcessError as e:
        error_summary = {
            "status": "error",
            "message": "Daily standup script failed",
            "stdout": e.stdout,
            "stderr": e.stderr
        }
        
        # Write error JSON summary
        with open('/data/workspace/daily_standup_summary.json', 'w') as f:
            json.dump(error_summary, f, indent=2)
        
        print("Daily standup script execution failed")
        return error_summary

# Run the task and print result
result = run_task()
print(json.dumps(result, indent=2))