# main.py

from pynput import keyboard
from langchain_core.messages import HumanMessage

# Import your compiled agent app and schema
from agent import app
from schemas import TroubleshootingGuide

def run_troubleshooter():
    """Function to be called by the hotkey."""
    print("\n\033[94mHotkey Activated! Running Linux Troubleshooter...\033[0m")
    
    # The initial prompt for the agent
    prompt = (
        "You are a helpful Linux Ubuntu assistant. Your goal is to identify the most "
        "recent and critical error from the provided system logs and generate a "
        "TroubleshootingGuide. First, call the `get_recent_system_logs` tool to get the data. "
        "Then, analyze the output and create the final guide."
    )
    
    inputs = {"messages": [HumanMessage(content=prompt)]}
    final_output = None
    
    # The 'stream' method provides real-time output as the graph runs
    for output in app.stream(inputs, stream_mode="values"):
        # The final output will be the last message in the state
        final_output = output['messages'][-1]

    if isinstance(final_output, TroubleshootingGuide):
        print("\n--- ✅ Troubleshooting Analysis Complete ---")
        print(f"Error: {final_output.error_summary}")
        print(f"Cause: {final_output.suspected_cause}")
        print(f"Log File: {final_output.log_file_path}")
        print(f"Log Entry: `{final_output.relevant_log_entry}`")
        if final_output.suggested_command:
            # Using ANSI escape codes for green, bold text
            print(f"💡 Suggested Command: \033[1m\033[92m{final_output.suggested_command}\033[0m")
        print("------------------------------------------\n")
    else:
        print("\n--- ❌ Could not generate a troubleshooting guide. ---")
        print("The agent finished without producing the expected structured output.")


# Define the hotkey combination (Super/Windows key + M)
HOTKEY = {keyboard.Key.cmd, keyboard.KeyCode.from_char('m')}
current_keys = set()

def on_press(key):
    if key in HOTKEY:
        current_keys.add(key)
        if all(k in current_keys for k in HOTKEY):
            run_troubleshooter()

def on_release(key):
    try:
        current_keys.remove(key)
    except KeyError:
        pass

if __name__ == "__main__":
    print("Linux Troubleshooting Agent is active.")
    print(f"Press Super+M to analyze recent system errors.")
    print("Run this script with 'sudo' to grant log file access.")
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()