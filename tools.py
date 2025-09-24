# tools.py

import subprocess
from langchain_core.tools import tool

@tool
def get_recent_system_logs(lines: int = 50) -> str:
    """
    Retrieves recent system logs from journalctl with error or higher priority.
    This is the modern and preferred way to get logs on systemd-based systems like Ubuntu.
    """
    print("--- Tool: Reading System Logs via journalctl ---")
    try:
        # journalctl is the standard.
        # -p err..emerg : Filter for messages with priority from "error" (3) to "emerg" (0).
        # -n {lines}      : Get the last N lines.
        # --no-pager    : Direct output to stdout without interactive paging.
        command = f"journalctl -p err..emerg -n {lines} --no-pager"
        
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True,
            check=True # We want it to raise an error if the command fails
        )
        
        logs = result.stdout.strip()

        if not logs:
            return "No recent errors or warnings found in the system journal."
            
        # We no longer need to filter for keywords because journalctl already did it by priority!
        return f"--- Critical System Logs from journalctl ---\n{logs}"

    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        return f"Error accessing system journal: {e}. Is journalctl available?"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

# import subprocess
# from langchain_core.tools import tool

# # Add paths to any other log files you want to monitor
# LOG_FILES_TO_CHECK = [
#     "/var/log/syslog",
#     "/var/log/auth.log",
#     "/var/log/apt/history.log",
#     "/var/log/dmesg",
# ]

# @tool
# def get_recent_system_logs(lines_per_file: int = 50) -> str:
#     """
#     Retrieves the most recent log entries from key system files in Ubuntu.
#     Focuses on lines containing 'error', 'warning', or 'failed'.
#     """
#     print("--- Tool: Reading System Logs ---")
#     all_logs = ""
#     for log_file in LOG_FILES_TO_CHECK:
#         try:
#             # Using 'tail' is efficient for getting the end of files rather than loading the entire file into RAM when using f.read().
#             # We add 'sudo' because these files often require root access.
#             command = f"sudo tail -n {lines_per_file} {log_file}"
            
#             result = subprocess.run(
#                 command, 
#                 shell=True, 
#                 capture_output=True, 
#                 text=True,
#                 check=False # Set to False to not raise an error if tail fails (e.g., file not found)
#             )

#             if result.returncode == 0: # if subprocess ran with no errors
#                 # Filter for relevant lines to keep the context for the LLM clean
#                 filtered_lines = [
#                     line for line in result.stdout.splitlines() 
#                     if 'error' in line.lower() or 'warning' in line.lower() or 'failed' in line.lower()
#                 ]

#                 if filtered_lines:
#                     all_logs += f"\n--- Logs from {log_file} ---\n"
#                     all_logs += "\n".join(filtered_lines)

#                 print(result)
            
#         except FileNotFoundError:
#             # Silently ignore if a log file doesn't exist
#             pass
            
#     if not all_logs:
#         return "No recent errors or warnings found in the monitored system logs."
        
#     return all_logs