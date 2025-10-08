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





# import subprocess
# from langchain_core.tools import tool

# # Optional mapping for common apps as fallback or to override weird process names
# CONTEXT_TO_PROCESS_NAME = {
#     "visual studio code": "code",
#     "terminal": "gnome-terminal-",  # Use a partial name to catch different terminal processes
#     "firefox": "firefox",
# }

# @tool
# def get_current_window_context() -> str:
#     """
#     Gets the title of the currently active window on the desktop. This should be
#     called first to understand the user's context.
#     """
#     print("--- Tool: Getting active window title ---")
#     try:
#         command = "xdotool getactivewindow getwindowname"
#         result = subprocess.run(
#             command, shell=True, capture_output=True, text=True, check=True
#         )
#         return result.stdout.strip()
#     except Exception as e:
#         return f"Could not determine the active window: {e}. Is xdotool installed?"

# def _detect_active_process_name() -> str:
#     """
#     Uses xdotool and ps to detect the process name of the currently active window dynamically.
#     Falls back to None if detection fails.
#     """
#     try:
#         # Get PID of the active window
#         pid_command = "xdotool getactivewindow getwindowpid"
#         pid_result = subprocess.run(
#             pid_command, shell=True, capture_output=True, text=True, check=True
#         )
#         pid = pid_result.stdout.strip()

#         if not pid:
#             print("[DEBUG] Could not determine active PID.")
#             return None

#         # Get process name from PID
#         proc_command = f"ps -p {pid} -o comm="
#         proc_result = subprocess.run(
#             proc_command, shell=True, capture_output=True, text=True, check=True
#         )
#         proc_name = proc_result.stdout.strip()
#         print(f"[DEBUG] Detected active process name: {proc_name}")
#         return proc_name if proc_name else None
#     except Exception as e:
#         print(f"[DEBUG] Failed to detect active process: {e}")
#         return None

# @tool
# def get_contextual_logs(application_context: str) -> str:
#     """
#     Searches system logs (journalctl) for entries related to the currently active process.
#     Attempts to detect the process dynamically. If that fails, falls back to
#     known mappings or general error logs.
#     """
#     print(f"--- Tool: Getting contextual logs for '{application_context}' ---")
#     context_lower = application_context.lower()

#     # 1. Try dynamic detection
#     process_name = _detect_active_process_name()

#     # 2. If dynamic detection failed, try known mappings
#     if not process_name:
#         for key, name in CONTEXT_TO_PROCESS_NAME.items():
#             if key in context_lower:
#                 process_name = name
#                 print(f"[DEBUG] Using fallback mapping for '{key}' → '{name}'")
#                 break

#     try:
#         if process_name:
#             print(f"--- Searching logs for process: '{process_name}' ---")
#             command = f"journalctl _COMM={process_name} -n 50 --no-pager"
#         else:
#             print("--- No process match found. Searching general system errors. ---")
#             command = "journalctl -p err..emerg -n 50 --no-pager"

#         result = subprocess.run(
#             command, shell=True, capture_output=True, text=True, check=True
#         )
#         logs = result.stdout.strip()

#         if not logs:
#             return f"No recent logs found for the context: {application_context}."
            
#         return f"--- System Logs (Context: {application_context}) ---\n{logs}"
#     except Exception as e:
#         return f"Error accessing system journal: {e}."

# @tool
# def read_specific_log_file(file_path: str, lines: int = 50) -> str:
#     """
#     Reads the last N lines from a specific log file path. This is useful for
#     deep-diving into a specific log file (e.g., /var/log/kern.log) after an error
#     has been identified in the general system journal.
#     """
#     print(f"--- Tool: Reading specific file: {file_path} ---")
#     try:
#         command = f"sudo tail -n {lines} {file_path}"
#         result = subprocess.run(
#             command, shell=True, capture_output=True, text=True, check=True
#         )
#         return result.stdout.strip()
#     except Exception as e:
#         return f"Error reading file {file_path}: {e}. Please ensure the path is correct."




# # # tools.py

# # import subprocess
# # from langchain_core.tools import tool

# # # A mapping from keywords in a window title (lowercase) to the process name used in logs.
# # # This can be expanded over time.
# # CONTEXT_TO_PROCESS_NAME = {
# #     "visual studio code": "code",
# #     "terminal": "gnome-terminal-", # Use a partial name to catch different terminal processes
# #     "firefox": "firefox",
# # }

# # @tool
# # def get_current_window_context() -> str:
# #     """
# #     Gets the title of the currently active window on the desktop. This should be
# #     called first to understand the user's context.
# #     """
# #     print("--- Tool: Getting active window title ---")
# #     try:
# #         command = "xdotool getactivewindow getwindowname"
# #         result = subprocess.run(
# #             command, shell=True, capture_output=True, text=True, check=True
# #         )
# #         return result.stdout.strip()
# #     except Exception as e:
# #         return f"Could not determine the active window: {e}. Is xdotool installed?"

# # @tool
# # def get_contextual_logs(application_context: str) -> str:
# #     """
# #     Searches system logs (journalctl) for entries related to a specific application context.
# #     If the context is recognized (e.g., 'Visual Studio Code'), it searches for logs from that app's process.
# #     Otherwise, it falls back to a general search for recent system-wide errors.
# #     The 'application_context' should be the title of the window from get_active_window_title.
# #     """
# #     print(f"--- Tool: Getting contextual logs for '{application_context}' ---")
# #     context_lower = application_context.lower()
# #     process_name = None

# #     for key, name in CONTEXT_TO_PROCESS_NAME.items():
# #         if key in context_lower:
# #             process_name = name
# #             break
    
# #     try:
# #         if process_name:
# #             # If we have a specific app, search for *any* logs from its process (not just errors)
# #             # to give the LLM the fullest possible context.
# #             print(f"--- Found mapping: '{process_name}'. Searching specific logs. ---")
# #             command = f"journalctl _COMM={process_name} -n 50 --no-pager"
# #         else:
# #             # Fallback for unrecognized apps: search for general high-priority errors
# #             print("--- No specific mapping. Searching general system errors. ---")
# #             command = "journalctl -p err..emerg -n 50 --no-pager"

# #         result = subprocess.run(
# #             command, shell=True, capture_output=True, text=True, check=True
# #         )
# #         logs = result.stdout.strip()
        
# #         if not logs:
# #             return f"No recent logs found for the context: {application_context}."
            
# #         return f"--- System Logs (Context: {application_context}) ---\n{logs}"
# #     except Exception as e:
# #         return f"Error accessing system journal: {e}."

# # @tool
# # def read_specific_log_file(file_path: str, lines: int = 50) -> str:
# #     """
# #     Reads the last N lines from a specific log file path. This is useful for
# #     deep-diving into a specific log file (e.g., /var/log/kern.log) after an error
# #     has been identified in the general system journal.
# #     """
# #     print(f"--- Tool: Reading specific file: {file_path} ---")
# #     try:
# #         command = f"sudo tail -n {lines} {file_path}"
# #         result = subprocess.run(
# #             command, shell=True, capture_output=True, text=True, check=True
# #         )
# #         return result.stdout.strip()
# #     except Exception as e:
# #         return f"Error reading file {file_path}: {e}. Please ensure the path is correct."


