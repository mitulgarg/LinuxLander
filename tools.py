# tools.py

import subprocess
from langchain_core.tools import tool

# Add paths to any other log files you want to monitor
LOG_FILES_TO_CHECK = [
    "/var/log/syslog",
    "/var/log/auth.log",
    "/var/log/apt/history.log",
    "/var/log/dmesg",
]

@tool
def get_recent_system_logs(lines_per_file: int = 50) -> str:
    """
    Retrieves the most recent log entries from key system files in Ubuntu.
    Focuses on lines containing 'error', 'warning', or 'failed'.
    """
    print("--- Tool: Reading System Logs ---")
    all_logs = ""
    for log_file in LOG_FILES_TO_CHECK:
        try:
            # Using 'tail' is efficient for getting the end of files rather than loading the entire file into RAM when using f.read().
            # We add 'sudo' because these files often require root access.
            command = f"sudo tail -n {lines_per_file} {log_file}"
            
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True,
                check=False # Set to False to not raise an error if tail fails (e.g., file not found)
            )

            if result.returncode == 0: # if subprocess ran with no errors
                # Filter for relevant lines to keep the context for the LLM clean
                filtered_lines = [
                    line for line in result.stdout.splitlines() 
                    if 'error' in line.lower() or 'warning' in line.lower() or 'failed' in line.lower()
                ]

                if filtered_lines:
                    all_logs += f"\n--- Logs from {log_file} ---\n"
                    all_logs += "\n".join(filtered_lines)

                print(result)
            
        except FileNotFoundError:
            # Silently ignore if a log file doesn't exist
            pass
            
    if not all_logs:
        return "No recent errors or warnings found in the monitored system logs."
        
    return all_logs