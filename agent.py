from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

# Custom modules
from schemas import TroubleshootingGuide
from tools import get_contextual_logs, read_specific_log_file

# Load environment
load_dotenv()
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Define agent state (add context)
class AgentState(TypedDict):
    messages: Annotated[list, lambda x, y: x + y]
    context: str  # active window or app name

# Initialize LLMs
llm = ChatOpenAI(model="gpt-4o", temperature=0)
structured_llm = llm.with_structured_output(TroubleshootingGuide)

# --- Helper: Check if logs are sufficient ---
def logs_insufficient(log_output: str) -> bool:
    if not log_output.strip():
        return True
    keywords = ["error", "fail", "exception", "panic", "segfault"]
    return not any(k in log_output.lower() for k in keywords)

# --- Node 1: Get contextual logs deterministically ---
def get_logs_node(state: AgentState):
    print(f"--- Node: Getting contextual logs for '{state['context']}' ---")
    logs = get_contextual_logs.invoke({"application_context": state["context"]})
    return {"messages": [HumanMessage(content=logs)]}

# --- Node 2: Fallback log reader ---
def read_logfile_node(state: AgentState):
    print("--- Node: Fallback: Reading /var/log/syslog ---")
    logs = read_specific_log_file.invoke({"file_path": "/var/log/syslog", "lines": 100})
    return {"messages": [HumanMessage(content=logs)]}

# --- Node 3: Parse logs into structured guide ---
def parser_node(state: AgentState):
    print("--- Node: Parser ---")
    tool_output = state['messages'][-1].content

    if "No recent logs found" in tool_output or logs_insufficient(tool_output):
        print("--- Parser: Logs insufficient or empty ---")
        return {"messages": [HumanMessage(content="No meaningful logs found. Try checking /var/log manually.")]}

    print("--- Parser: Generating TroubleshootingGuide ---")
    parsing_prompt = f"""
    You are an expert at diagnosing Linux system issues.
    Analyze the following logs and produce a concise TroubleshootingGuide.

    Logs:
    {tool_output}
    """
    guide = structured_llm.invoke(parsing_prompt)
    return {"messages": [guide]}

# --- Graph setup ---
workflow = StateGraph(AgentState)
workflow.add_node("get_logs", get_logs_node)
workflow.add_node("read_logfile", read_logfile_node)
workflow.add_node("parser", parser_node)

workflow.set_entry_point("get_logs")

# Conditional routing
def check_log_quality(state: AgentState):
    log_output = state["messages"][-1].content
    if logs_insufficient(log_output):
        print("--- Condition: Logs insufficient → fallback to /var/log/syslog ---")
        return "read_logfile"
    else:
        print("--- Condition: Logs sufficient → parse directly ---")
        return "parser"

workflow.add_conditional_edges("get_logs", check_log_quality)
workflow.add_edge("read_logfile", "parser")
workflow.add_edge("parser", END)

app = workflow.compile()
