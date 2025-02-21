import code
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage

from . import llm 
from .tools import code_retriever_tool, doc_retriever_tool, csv_retriever_tool

# Define your system prompt once
system_prompt = """
You are an assistant that helps users with understanding Harry Potter books. 
Your main task is to answer any questions that the user may have regarding Harry Potter and its universe.

Reminders:
    Always remember to be kind, respectful and enthusiastic with your messages.
    Never communicate negative or harmful messages.
    
DO NOT answer any questions that are not related to Harry Potter or its universe.

Output:
    Always format your output in proper markdown format.
"""

tools = [code_retriever_tool, doc_retriever_tool, csv_retriever_tool]
llm_with_tools = llm.bind_tools(tools)

# The state holds all previous messages
class State(TypedDict):
    messages: Annotated[list, add_messages]

def call_model(state: MessagesState):
    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": response}

def tools_handler(state: State):
    # Can be used to handle post processing of tool output
    return state


# Build the graph, adding an input parameter for user input
state_graph = StateGraph(State)
state_graph.add_node("chatbot", call_model)

tool_node = ToolNode
state_graph.add_conditional_edges(
    "chatbot",
    tools_condition
)

state_graph.add_node("tools", tools_handler)
state_graph.add_edge("tools", "chatbot")
state_graph.set_entry_point("chatbot")
state_graph.add_edge("chatbot", END)

# Use MemorySaver to persist state between runs (if desired)
memory = MemorySaver()

# Compile the graph with a memory checkpointer
agent = state_graph.compile(checkpointer=memory)

# Example function to stream updates (similar to your LangChain streaming)
def stream_graph_updates(user_input: str):
    # Pass in initial state if needed; MemorySaver will restore previous state.
    # Here we assume your MemorySaver is set up to track sessions.
    for event in agent.stream({"messages": [HumanMessage(content=user_input)]},
            config={"configurable": {"thread_id": "test_123"}}):
        # Each event is a dict; print the latest AI message
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)

# Example usage (you could also integrate this into a webserver or CLI loop)
if __name__ == "__main__":
    from IPython.display import Image, display
    try:
        display(Image(agent.get_graph().draw_mermaid_png()))
    except Exception:
        # This requires some extra dependencies and is optional
        pass
    while True:
        user_input = input("User: ")
        if user_input.lower() in ["exit", "quit", "q"]:
            break
        stream_graph_updates(user_input)
