import subprocess
from typing import List
from langchain_core.tools import tool

# Common Linux log files to consider
COMMON_LOG_FILES = [
    "/var/log/syslog",
    "/var/log/kern.log",
    "/var/log/auth.log",
    "/var/log/dpkg.log",
    "/var/log/Xorg.0.log",
    "/var/log/apt/history.log",
]

CONTEXT_TO_PROCESS_NAME = {
    "visual studio code": "code",
    "terminal": "gnome-terminal-",
    "firefox": "firefox",
}

def _detect_active_process_name() -> str:
    """Detect the process name of the active window using xdotool and ps."""
    try:
        pid_result = subprocess.run(
            "xdotool getactivewindow getwindowpid", shell=True, capture_output=True, text=True, check=True
        )
        pid = pid_result.stdout.strip()
        if not pid:
            return None

        proc_result = subprocess.run(
            f"ps -p {pid} -o comm=", shell=True, capture_output=True, text=True, check=True
        )
        proc_name = proc_result.stdout.strip()
        return proc_name or None
    except Exception as e:
        print(f"[DEBUG] Process detection failed: {e}")
        return None

@tool
def get_current_window_context() -> str:
    """Return the title of the currently active window."""
    print("--- Tool: Getting active window title ---")
    try:
        result = subprocess.run(
            "xdotool getactivewindow getwindowname", shell=True, capture_output=True, text=True, check=True
        )
        title = result.stdout.strip()
        proc = _detect_active_process_name()
        return f"{title} (process: {proc or 'unknown'})"
    except Exception as e:
        return f"Could not determine the active window: {e}. Is xdotool installed?"

@tool
def get_contextual_logs(application_context: str) -> str:
    """Fetch logs from journalctl relevant to the detected process or context."""
    print(f"--- Tool: Getting contextual logs for '{application_context}' ---")
    process_name = _detect_active_process_name()

    # Fallback using mapping
    if not process_name:
        for key, name in CONTEXT_TO_PROCESS_NAME.items():
            if key in application_context.lower():
                process_name = name
                break

    try:
        if process_name:
            command = f"journalctl _COMM={process_name} -n 100 --no-pager"
        else:
            command = "journalctl -p err..emerg -n 100 --no-pager"

        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        logs = result.stdout.strip()
        return logs or "No recent logs found for this application context."
    except Exception as e:
        return f"Error accessing system journal: {e}"

@tool
def list_available_log_files() -> List[str]:
    """Return a list of important log files for Linux diagnostics."""
    return [f for f in COMMON_LOG_FILES]

@tool
def read_specific_log_file(file_path: str, lines: int = 50) -> str:
    """Read the last N lines from a given log file."""
    print(f"--- Tool: Reading specific log file: {file_path} ---")
    try:
        result = subprocess.run(f"sudo tail -n {lines} {file_path}", shell=True, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except Exception as e:
        return f"Error reading file {file_path}: {e}. Check permissions or path validity."



