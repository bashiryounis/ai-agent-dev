from langgraph.graph import StateGraph, END, START, add_messages
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import init_chat_model
from langgraph.types import interrupt , Command , Literal
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from prompt import REFINE_PROMPT, ARCH_GEN_PROMPT, ARCH_UPDATE_PROMPT, MERMAID_PROMPT
from schema import AgentState, HumanFeedback
import os



# Initialize LLM
llm = init_chat_model("gpt-4o-mini", model_provider="openai")
# initialize Prompt 
refine_prompt = ChatPromptTemplate.from_template(REFINE_PROMPT)
architecture_gen_prompt = ChatPromptTemplate.from_template(ARCH_GEN_PROMPT)
architecture_update_prompt = ChatPromptTemplate.from_template(ARCH_UPDATE_PROMPT)
mermaid_prompt = ChatPromptTemplate.from_template(MERMAID_PROMPT)




def refine_description(state: AgentState) -> AgentState:
    """Refine and improve the project description using LLM"""
    chain = refine_prompt | llm
    refined = chain.invoke({"raw_input": state["raw_input"]})
    return {
        "refined_description": refined.content,
        "messages": [{
            "role": "assistant",
            "content": f"Reined project description:\n\n{refined.content}" 
        }],
        "current_state": "refined_description",
        "next_state": "architecture"
    }

def generate_architecture(state: AgentState) -> AgentState:
    """Generate architecture specification using LLM"""
    human_feedback_list = state.get("human_feedback", [])
    
    if human_feedback_list and not human_feedback_list[-1].get("is_satisfied", True):
        print("===== Updating architecture based on feedback =====")
        specific_feedback = human_feedback_list[-1].get("specific_feedback", "")
        feedback_text = specific_feedback.specific_feedback if hasattr(specific_feedback, "specific_feedback") else specific_feedback
        
        chain = architecture_update_prompt | llm
        arch_spec = chain.invoke({
            "architecture_spec": state["architecture_spec"],
            "human_feedback": feedback_text
        })
        
        return {
            "architecture_spec": arch_spec.content,
            "messages": [{
                "role": "assistant",
                "content": f"Updated architecture specification based on your feedback:\n\n{arch_spec.content}"              
            }],
            "human_feedback": [],
            "current_state": "architecture",
            "next_state": "human_review"
        }
    else: 
        print("===== Generating initial architecture =====")
        chain = architecture_gen_prompt | llm
        arch_spec = chain.invoke({"refined_description": state["refined_description"]})
        
        return {
            "architecture_spec": arch_spec.content,
            "messages": [{
                "role": "assistant",
                "content": f"Generated architecture specification:\n\n{arch_spec.content}"
            }],
            "current_state": "architecture",
            "next_state": "human_review"
        }

def generate_mermaid(state: AgentState) -> AgentState:
    """Generate Mermaid diagram code using LLM"""
    chain = mermaid_prompt | llm
    mermaid_code = chain.invoke({"architecture_spec": state["architecture_spec"]})
    
    return {
        "mermaid_code": mermaid_code.content,
        "messages": [{
            "role": "assistant",
            "content": f"Generated Mermaid JS code for visualization:\n\n{mermaid_code.content}\n\nArchitecture visualization is complete!"
        }],
        "current_state": "mermaid_code",
        "next_state": "end"
    }



def human_review_node(state: AgentState) -> Command:
    """
    Human review node that checks the current state and provides appropriate prompts.
    """
    current_state = state["current_state"]
    next_state = state["next_state"]
    content = state.get(current_state, "")
    
    feedback_evaluator = llm.with_structured_output(HumanFeedback)
    
    human_response = interrupt(
        {"generated_content": content, "message": "Review the architecture. Provide feedback or type 'done' if satisfied."})
    
    messages = [
        SystemMessage(content=f"""
        You are an AI assistant tasked with reviewing the architecture stage of a project based on user feedback. 
        Your goal is to evaluate the provided content and determine:

        1. Whether the user is satisfied with the current architecture
        2. What specific feedback they have provided to improve it

        Architecture to review:
        {content}

        Please return your answer as a JSON object with two keys:
        - "is_satisfied": a boolean indicating if the user is satisfied (true) or wants changes (false)
        - "specific_feedback": a detailed description of what changes the user wants
        """),
        HumanMessage(content=human_response)
    ]
    
    feedback = feedback_evaluator.invoke(messages)
    
    print(f"User satisfaction: {'Satisfied' if feedback.is_satisfied else 'Not satisfied'}")
    if not feedback.is_satisfied:
        return {
            "human_feedback": [{"is_satisfied": feedback.is_satisfied, "specific_feedback": feedback}]
        }
        
    return {
        "human_feedback": [{"is_satisfied": feedback.is_satisfied, "specific_feedback": feedback}]
    }


def route_after_review(state: AgentState) -> str:
    """
    Router function that directs workflow based on the latest human feedback satisfaction.
    """
    human_feedback_list = state.get("human_feedback", [])
    
    if not human_feedback_list:
        return "architecture"
    
    latest_feedback = human_feedback_list[-1]
    is_satisfied = latest_feedback.get("is_satisfied", False)
    
    if is_satisfied:
        print("User is satisfied. Proceeding to generate Mermaid diagram...")
        return "gen_mermaid"
    else:
        print("User wants improvements. Returning to architecture generation...")
        return "architecture"


# Initialize the graph
def create_agent_graph():
    """Create and return the agent workflow graph"""
    # Initialize the graph
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("refine", refine_description)
    workflow.add_node("architecture", generate_architecture)
    workflow.add_node("human_review", human_review_node)
    workflow.add_node("gen_mermaid", generate_mermaid)

    # Define flow
    workflow.add_edge("refine", "architecture")
    workflow.add_edge("architecture", "human_review")

    # Add conditional routing after human review
    workflow.add_conditional_edges(
        "human_review",
        route_after_review,
        {
            "architecture": "architecture",
            "gen_mermaid": "gen_mermaid"
        }
    )

    workflow.add_edge("gen_mermaid", END)

    # Set the entry point
    workflow.set_entry_point("refine")

    # Set up checkpointer for state persistence
    checkpointer = MemorySaver()

    # Compile the graph
    graph = workflow.compile(interrupt_before=["human_review"], checkpointer=checkpointer)
    
    return graph

