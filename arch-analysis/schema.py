from langgraph.graph import add_messages
from typing import Dict, TypedDict, List, Any
from pydantic import BaseModel , Field
from typing_extensions import TypedDict, Annotated

def replace_operator(old, new):
    return new



class AgentState(TypedDict):
    raw_input: Annotated[str, replace_operator]
    refined_description: Annotated[str, replace_operator]
    architecture_spec: Annotated[str, replace_operator]
    mermaid_code: Annotated[str, replace_operator]
    current_state: Annotated[str, replace_operator] 
    next_state: Annotated[str, replace_operator] 
    human_feedback: Annotated[List[Dict], replace_operator]
    messages: Annotated[List[Dict], add_messages]

class HumanFeedback(BaseModel): 
    is_satisfied: bool = Field(
        description="Whether the current output meets the user's requirements"
    )
    specific_feedback: str = Field(
        description="Detailed feedback or suggestions for improvement"
    )