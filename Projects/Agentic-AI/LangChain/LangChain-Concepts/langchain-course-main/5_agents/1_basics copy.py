"""
Complete LangGraph Agent Example
This code avoids the buggy langchain.agents imports by using LangGraph directly.
"""
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, List
import operator
from langchain_core.messages import HumanMessage, BaseMessage, ToolMessage
import datetime
import json
from dotenv import load_dotenv

# Load environment variables (for OPENAI_API_KEY)
load_dotenv()

# ====================== 1. DEFINE THE AGENT STATE ======================
class AgentState(TypedDict):
    """State for our agent with conversation history."""
    messages: Annotated[List[BaseMessage], operator.add]

# ====================== 2. DEFINE TOOLS ======================
@tool
def get_system_time(format: str = "%H:%M:%S") -> str:
    """Get the current system time in the specified format."""
    current_time = datetime.datetime.now()
    return current_time.strftime(format)

@tool
def calculate_time_difference(city: str) -> str:
    """
    Calculate time difference between current location (India) and target city.
    city: Name of the city (e.g., 'London', 'New York')
    """
    time_diffs = {
        "london": "5 hours and 30 minutes behind India (UTC+0)",
        "new york": "10 hours and 30 minutes behind India (UTC-5)",
        "tokyo": "3 hours and 30 minutes ahead of India (UTC+9)",
        "paris": "4 hours and 30 minutes behind India (UTC+1)",
        "dubai": "1 hour and 30 minutes behind India (UTC+4)"
    }
    
    city_lower = city.lower()
    if city_lower in time_diffs:
        return f"{city.title()} is {time_diffs[city_lower]}"
    else:
        return f"Time difference for {city} not available in database."

# List of available tools
tools = [get_system_time, calculate_time_difference]
tool_map = {tool.name: tool for tool in tools}

# ====================== 3. INITIALIZE LLM ======================
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

# Bind tools to LLM for function calling
llm_with_tools = llm.bind_tools(tools)

# ====================== 4. DEFINE GRAPH NODES ======================
def agent_node(state: AgentState) -> dict:
    """
    Node that calls the LLM. The LLM decides whether to use tools or respond directly.
    """
    print("\n=== Agent Thinking ===")
    messages = state["messages"]
    
    # Get response from LLM
    response = llm_with_tools.invoke(messages)
    print(f"LLM Response: {response.content[:100]}...")
    
    # Check if LLM wants to use tools
    if hasattr(response, 'tool_calls') and response.tool_calls:
        print(f"Agent wants to use tools: {[tc['name'] for tc in response.tool_calls]}")
    
    return {"messages": [response]}

def tool_node(state: AgentState) -> dict:
    """
    Node that executes tools when called by the agent.
    """
    print("\n=== Executing Tools ===")
    messages = state["messages"]
    last_message = messages[-1]
    
    tool_results = []
    
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        for tool_call in last_message.tool_calls:
            tool_name = tool_call['name']
            tool_args = tool_call['args']
            
            print(f"  Executing: {tool_name} with args: {tool_args}")
            
            if tool_name in tool_map:
                try:
                    # Execute the tool
                    result = tool_map[tool_name].invoke(tool_args)
                    print(f"  Result: {result}")
                    
                    # Create ToolMessage
                    tool_results.append(
                        ToolMessage(
                            content=json.dumps(result) if not isinstance(result, str) else result,
                            tool_call_id=tool_call['id']
                        )
                    )
                except Exception as e:
                    error_msg = f"Error executing {tool_name}: {str(e)}"
                    print(f"  {error_msg}")
                    tool_results.append(
                        ToolMessage(
                            content=error_msg,
                            tool_call_id=tool_call['id']
                        )
                    )
            else:
                error_msg = f"Tool {tool_name} not found"
                print(f"  {error_msg}")
                tool_results.append(
                    ToolMessage(
                        content=error_msg,
                        tool_call_id=tool_call['id']
                    )
                )
    
    return {"messages": tool_results}

# ====================== 5. BUILD THE GRAPH ======================
def route_after_agent(state: AgentState) -> str:
    """
    Routing logic: After agent runs, decide what to do next.
    """
    last_message = state["messages"][-1]
    
    # If last message has tool calls, go to tools node
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        print("\n--- Routing to Tools ---")
        return "tools"
    
    # Otherwise, end the graph
    print("\n--- Routing to END (Final Answer) ---")
    return END

def route_after_tools(state: AgentState) -> str:
    """
    After tools run, always go back to the agent.
    """
    print("\n--- Routing back to Agent ---")
    return "agent"

# Build the workflow graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("agent", agent_node)
workflow.add_node("tools", tool_node)

# Set entry point
workflow.set_entry_point("agent")

# Add edges with conditional routing
workflow.add_conditional_edges(
    "agent",
    route_after_agent,
    {
        "tools": "tools",
        END: END
    }
)

workflow.add_edge("tools", "agent")

# Compile the graph
app = workflow.compile()

# ====================== 6. HELPER FUNCTION TO RUN AGENT ======================
def run_agent(query: str, max_iterations: int = 5) -> str:
    """
    Run the agent with a query and return the final answer.
    
    Args:
        query: The user's question
        max_iterations: Maximum number of agent-tool cycles
        
    Returns:
        The agent's final answer
    """
    print(f"\n{'='*60}")
    print(f"QUERY: {query}")
    print(f"{'='*60}")
    
    # Initialize state with user message
    initial_state: AgentState = {
        "messages": [HumanMessage(content=query)]
    }
    
    # Run the graph
    current_state = initial_state
    iteration = 0
    
    while iteration < max_iterations:
        iteration += 1
        print(f"\n\nIteration {iteration}:")
        
        # Run one step of the graph
        config = {"recursion_limit": 50}
        
        try:
            # Get the next node to execute
            output = app.invoke(current_state, config)
            current_state = output
            
            # Check if we have a final answer
            last_message = current_state["messages"][-1]
            
            # If the last message is from the agent and has no tool calls, we're done
            if (hasattr(last_message, 'content') and 
                not (hasattr(last_message, 'tool_calls') and last_message.tool_calls)):
                print(f"\n{'='*60}")
                print("FINAL ANSWER:")
                print(f"{'='*60}")
                print(last_message.content)
                return last_message.content
                
        except Exception as e:
            print(f"\nError in iteration {iteration}: {str(e)}")
            break
    
    # If we exit the loop, return the last message
    if current_state["messages"]:
        last_msg = current_state["messages"][-1]
        if hasattr(last_msg, 'content'):
            return last_msg.content
    
    return "Agent failed to produce an answer."

# ====================== 7. MAIN EXECUTION ======================
if __name__ == "__main__":
    # Example queries
    queries = [
        "What is the current time in London? (You are in India). Just show the current time and not the date",
        "What time would it be in New York right now?",
        "Tell me about the time difference between Tokyo and India",
        "What's the current system time and how does it compare to Paris time?"
    ]
    
    # Run for each query
    for i, query in enumerate(queries, 1):
        print(f"\n{'#'*70}")
        print(f"EXAMPLE {i}")
        print(f"{'#'*70}")
        
        answer = run_agent(query)
        
        # Small pause between examples
        if i < len(queries):
            input("\nPress Enter to continue to next example...")

# ====================== 8. SIMPLIFIED VERSION (If above is too complex) ======================
"""
If you want a simpler version without all the debugging prints, use this:

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, List
import operator
from langchain_core.messages import HumanMessage, BaseMessage, ToolMessage
import datetime
from dotenv import load_dotenv

load_dotenv()

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]

@tool
def get_system_time():
    return datetime.datetime.now().strftime("%H:%M:%S")

tools = [get_system_time]
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
llm_with_tools = llm.bind_tools(tools)

def agent_node(state):
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

def tool_node(state):
    last_msg = state["messages"][-1]
    results = []
    if hasattr(last_msg, 'tool_calls'):
        for tc in last_msg.tool_calls:
            if tc['name'] == 'get_system_time':
                result = get_system_time.invoke({})
                results.append(ToolMessage(content=result, tool_call_id=tc['id']))
    return {"messages": results}

def route_logic(state):
    last_msg = state["messages"][-1]
    if hasattr(last_msg, 'tool_calls') and last_msg.tool_calls:
        return "tools"
    return END

workflow = StateGraph(AgentState)
workflow.add_node("agent", agent_node)
workflow.add_node("tools", tool_node)
workflow.set_entry_point("agent")
workflow.add_conditional_edges("agent", route_logic, {"tools": "tools", END: END})
workflow.add_edge("tools", "agent")
app = workflow.compile()

# Run it
query = "What is the current time in London? (You are in India)"
state = {"messages": [HumanMessage(content=query)]}
result = app.invoke(state)
print(result["messages"][-1].content)
"""