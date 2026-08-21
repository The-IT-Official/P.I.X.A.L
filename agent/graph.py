from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage, SystemMessage
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
import operator

from llm import llm_with_tools, SYSTEM_PROMPT
from tools import agent_tools
from memory import memory_tools

all_tools = agent_tools + memory_tools

class AgentState(TypedDict):
    messages: Annotated[list, operator.add]

def agent_node(state: AgentState):
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

def should_continue(state: AgentState):
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    return END

tool_node = ToolNode(all_tools)

workflow = StateGraph(AgentState)
workflow.add_node("agent", agent_node)
workflow.add_node("tools", tool_node)

workflow.set_entry_point("agent")
workflow.add_conditional_edges("agent", should_continue)
workflow.add_edge("tools", "agent")

app = workflow.compile()

if __name__ == "__main__":
    user_input = input("User: ")  # ← add this line
    for chunk in app.stream({"messages": [HumanMessage(content=user_input)]}):
        for node, values in chunk.items():
            print(f"\n[{node}]")
            msg = values["messages"][-1]
            print(msg.content if msg.content else "[tool call]")
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                for tc in msg.tool_calls:
                    print(f"  → {tc['name']}({tc['args']})") 