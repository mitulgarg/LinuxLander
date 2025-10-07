import subprocess
from pynput import keyboard
from langchain_core.messages import HumanMessage

# Import our tools and agent components
from agent import app
from schemas import TroubleshootingGuide
from tools import get_current_window_context

def show_notification(title, message):
    """Sends a desktop notification."""
    try:
        subprocess.run(['notify-send', title, message, '--urgency=critical'], check=True)
    except Exception as e:
        print(f"Failed to send notification: {e}")

def run_troubleshooter():
    print("\n\033[94mHotkey Activated! Running Linux Troubleshooter...\033[0m")

    # STEP 1: Get current app/window
    active_window = get_current_window_context.invoke({})
    print(f"--- Context Captured: '{active_window}' ---")

    # STEP 2: Run agent deterministically with context
    inputs = {
        "messages": [HumanMessage(content=f"Analyze logs for '{active_window}'")],
        "context": active_window
    }

    final_output = None
    for output in app.stream(inputs, stream_mode="values"):
        final_output = output['messages'][-1]

    # STEP 3: Display results
    if isinstance(final_output, TroubleshootingGuide):
        title = f"💡 Error Found: {final_output.error_summary}"
        message = (
            f"<b>Context:</b> {active_window}\n"
            f"<b>Cause:</b> {final_output.suspected_cause}\n"
            f"<b>Log File:</b> {final_output.log_file_path or 'journalctl'}\n"
            f"<b>Entry:</b> <code>{final_output.relevant_log_entry}</code>\n"
            f"<b>Suggested Fix:</b> <code>{final_output.suggested_command or 'N/A'}</code>"
        )
        show_notification(title, message)
    else:
        text = getattr(final_output, "content", "No actionable logs found.")
        show_notification("System Scan Complete", text)

# Hotkey: Space + M
HOTKEY = {keyboard.Key.space, keyboard.KeyCode.from_char('m')}
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
    print("Press Space + M to analyze recent system errors.")
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()




# import subprocess
# from pynput import keyboard
# from langchain_core.messages import HumanMessage

# # Import our tools and agent components
# from agent import app
# from schemas import TroubleshootingGuide
# from tools import get_current_window_context # Import the new tool

# def show_notification(title, message):
#     """Sends a desktop notification."""
#     try:
#         subprocess.run(['notify-send', title, message, '--urgency=critical'], check=True)
#     except Exception as e:
#         print(f"Failed to send notification: {e}")

# def run_troubleshooter():
#     """Gets context, builds a prompt, and runs the agent."""
#     print("\n\033[94mHotkey Activated! Running Linux Troubleshooter...\033[0m")
    
#     # STEP 1: Get the current application context
#     active_window = get_current_window_context.invoke({})
#     print(f"--- Context Captured: Active window is '{active_window}' ---")

#     # STEP 2: Build a dynamic prompt with the context
#     prompt = f"The user was working in '{active_window}'. Diagnose issues from recent logs."

#     prompt = f"""
#                 The user was working in '{active_window}'. 
#                 Call the `get_contextual_logs` tool using this context, 
#                 then analyze the returned logs for errors."""


#     inputs = {"messages": [HumanMessage(content=prompt)]}
#     final_output = None
    
#     # STEP 3: Run the agent
#     for output in app.stream(inputs, stream_mode="values"):
#         final_output = output['messages'][-1]

#     # STEP 4: Show the result
#     if isinstance(final_output, TroubleshootingGuide):
#         title = f"💡 Error Found: {final_output.error_summary}"
#         message = (
#             f"<b>Context:</b> {active_window}\n"
#             f"<b>Cause:</b> {final_output.suspected_cause}\n"
#             f"<b>Log File:</b> {final_output.log_file_path or 'journalctl'}\n"
#             f"<b>Entry:</b> <code>{final_output.relevant_log_entry}</code>\n"
#             f"<b>Suggested Fix:</b> <code>{final_output.suggested_command or 'N/A'}</code>"
#         )
#         show_notification(title, message)
#     else:
#         if hasattr(final_output, 'content') and isinstance(final_output.content, str):
#             show_notification("System Scan Complete", final_output.content)
#         else:
#             show_notification("Scan Error", "Could not generate a troubleshooting guide.")


# # # Define the hotkey combination (Spacebar key + M)
# HOTKEY = {keyboard.Key.space, keyboard.KeyCode.from_char('m')}
# current_keys = set()

# def on_press(key):
#     if key in HOTKEY:
#         current_keys.add(key)
#         if all(k in current_keys for k in HOTKEY):
#             run_troubleshooter()

# def on_release(key):
#     try:
#         current_keys.remove(key)
#     except KeyError:
#         pass


# if __name__ == "__main__":
#     print("Linux Troubleshooting Agent is active.")
#     print(f"Press Super+M to analyze recent system errors.")
#     # You will no longer need to run this with sudo if the service is set up correctly
#     with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
#         listener.join()
