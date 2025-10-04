from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

# Custom modules
from schemas import TroubleshootingGuide
from tools import get_contextual_logs, get_current_window_context, read_specific_log_file



# 1. Define the Agent's State
class AgentState(TypedDict):
    messages: Annotated[list, lambda x, y: x + y]

load_dotenv()
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# 2. Set up two LLM instances
# Regular LLM for general reasoning and tool calling
llm = ChatOpenAI(model="gpt-4o", temperature=0)
# Structured LLM specifically for parsing logs into the final format
structured_llm = llm.with_structured_output(TroubleshootingGuide)

# 3. Create the tools
tools = [get_contextual_logs, get_current_window_context,read_specific_log_file]
tool_node = ToolNode(tools)

# 4. Define the graph nodes

def agent_node(state):
    """Node that decides which action to take."""
    print("--- Node: Agent ---")
    response = llm.invoke(state['messages'])
    # The agent will now exclusively be used for deciding to call a tool
    return {"messages": [response]}

def parser_node(state):
    """
    Parses the output of the tool. If logs are found, it uses the
    structured LLM to create a guide. Otherwise, it returns a simple message.
    """
    print("--- Node: Parser ---")
    # The last message is the output from the tool
    tool_output = state['messages'][-1].content

    if "No recent errors or warnings found" in tool_output:
        print("--- Parser: No errors found in logs. ---")
        return {"messages": [HumanMessage(content="No recent errors were found in the system journal.")]}

    print("--- Parser: Logs found, generating guide. ---")
    # If we have logs, create a new prompt for the structured LLM to parse them
    parsing_prompt = f"""
    You are an expert at parsing Linux log files. Based on the following log data from journalctl,
    please generate a concise TroubleshootingGuide. Focus on the most critical and
    likely root cause reflected in the logs.

    Logs:
    {tool_output}
    """
    
    guide = structured_llm.invoke(parsing_prompt)
    return {"messages": [guide]}

# 5. Construct the Graph with the new logic
workflow = StateGraph(AgentState)

workflow.add_node("agent", agent_node)
workflow.add_node("action", tool_node)
workflow.add_node("parser", parser_node)

workflow.set_entry_point("agent")

# Define the edges for the "Decide -> Act -> Parse" flow
workflow.add_edge("agent", "action")
workflow.add_edge("action", "parser")
workflow.add_edge("parser", END)

# Compile the graph into a runnable app
app = workflow.compile()

