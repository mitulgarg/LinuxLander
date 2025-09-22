# agent.py

from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode #replaced ToolExecutor with  ToolNode (newer langgraph version)
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

# Custom modules
from schemas import TroubleshootingGuide
from tools import get_recent_system_logs

# 1. Define the Agent's State
class AgentState(TypedDict):
    messages: Annotated[list, lambda x, y: x + y]


load_dotenv()
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY") # Use .get for safer access



# 2. Set up the LLM with the structured output schema
llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.1,
    max_tokens=None,
    timeout=None,
    max_retries=2,

)

structured_llm = llm.with_structured_output(TroubleshootingGuide)

# 3. Create the tools and tool executor
tools = [get_recent_system_logs]

# tool_executor = ToolExecutor(tools) (Not needed once we switched to ToolNode)

# 4. Define the graph nodes
def call_model(state):
    """The node that invokes the LLM to generate the analysis."""
    print("--- Node: Calling Model ---")
    messages = state['messages']
    # The LLM will decide if it needs to call a tool or if it can answer directly
    response = structured_llm.invoke(messages)
    return {"messages": [response]}

#Not needed once we switched from ToolExecutor to ToolNode
# def call_tool(state):
#     """The node that executes the log reading tool."""
#     last_message = state['messages'][-1]
#     # The LLM's last message should contain a tool call
#     tool_call = last_message.tool_calls[0]
#     action_result = tool_executor.invoke(tool_call)
#     return {"messages": [action_result]}

# 5. Define the routing logic (conditional edges)
def should_continue(state):
    """Determines whether to call a tool or end the process."""
    last_message = state['messages'][-1]
    if not hasattr(last_message, 'tool_calls') or not last_message.tool_calls:
        # If the model did not request a tool call, we are done
        return "end"
    else:
        # Otherwise, we need to call the tool
        return "continue"

# 6. Construct the Graph
workflow = StateGraph(AgentState)

workflow.add_node("agent", call_model)
workflow.add_node("action", ToolNode(tools))

workflow.set_entry_point("agent")

workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "continue": "action",
        "end": END,
    },
)

workflow.add_edge("action", "agent")

# Compile the graph into a runnable app
app = workflow.compile()