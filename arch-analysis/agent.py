import uuid
from typing import Dict, Any, Callable, Optional
from langgraph.types import Command

class ArchitectureProcessor:
    """
    A class to handle the architecture processing with feedback loops.
    This maintains state between calls to make the pattern clearer.
    """
    
    def __init__(self, graph):
        """Initialize with the LangGraph graph object"""
        self.graph = graph
        self.thread_id = None
        self.thread_config = None
    
    def start_processing(
        self, 
        user_input: str,
        message_callback: Callable[[str], None],
        status_callback: Optional[Callable[[str], None]] = None
    ) -> Dict[str, Any]:
        """
        Start processing an architecture request.
        
        Args:
            user_input: The initial user prompt as a string
            message_callback: Function to call with message updates
            status_callback: Function to call with status updates
            
        Returns:
            Either the final state (dict) or a status object indicating feedback is needed
        """
        # Generate a thread ID for this session
        self.thread_id = str(uuid.uuid4())
        self.thread_config = {"configurable": {"thread_id": self.thread_id}}
        
        # Create the initial state
        initial_state = {
            "raw_input": user_input,
            "refined_description": "",
            "architecture_spec": "",
            "mermaid_code": "",
            "current_state": "",
            "next_state": "",
            "messages": [{"role": "user", "content": user_input}],
            "human_feedback": []
        }
        
        if status_callback:
            status_callback("Analyzing architecture description...")
        
        current_message = ""
        
        # Process the stream
        for mode, data in self.graph.stream(
            initial_state,
            config=self.thread_config,
            stream_mode=["messages", "updates"]
        ):
            if mode == "messages":
                msg, metadata = data
                if hasattr(msg, "content"):
                    current_message += msg.content
                    message_callback(current_message)
            
            elif mode == "updates" and "__interrupt__" in data:
                # Get the current state
                current_state = self.graph.get_state(self.thread_config)
                if hasattr(current_state, "values"):
                    current_state = current_state.values
                
                # Check if human review is required
                if (current_state.get("next_state", "") == "human_review" or 
                    current_state.get("current_state", "") == "human_review"):
                    
                    if status_callback:
                        status_callback("Human review required")
                    
                    # Return a status object with all necessary info
                    return {
                        "status": "feedback_required",
                        "message": current_message,
                        "state": current_state
                    }
        
        # If we get here, processing completed without requiring feedback
        final_state = self.graph.get_state(self.thread_config)
        if hasattr(final_state, "values"):
            final_state = final_state.values
        
        if status_callback:
            status_callback("Architecture analysis completed!")
        
        return {
            "status": "completed",
            "message": current_message,
            "state": final_state
        }
    
    def continue_with_feedback(
        self,
        feedback: str,
        message_callback: Callable[[str], None],
        status_callback: Optional[Callable[[str], None]] = None
    ) -> Dict[str, Any]:
        """
        Continue processing with user feedback.
        
        Args:
            feedback: The user feedback as a string
            message_callback: Function to call with message updates
            status_callback: Function to call with status updates
            
        Returns:
            Either the final state (dict) or a status object indicating more feedback is needed
        """
        if not self.thread_id or not self.thread_config:
            raise ValueError("No active session. Call start_processing first.")
        
        if status_callback:
            status_callback("Processing feedback...")
        
        # Resume the graph with the feedback
        self.graph.invoke(Command(resume=feedback), self.thread_config)
        
        current_message = ""
        
        # Continue processing from where we left off
        for mode, data in self.graph.stream(
            None,  # No initial state needed when continuing
            config=self.thread_config,
            stream_mode=["messages", "updates"]
        ):
            if mode == "messages":
                msg, metadata = data
                if hasattr(msg, "content"):
                    current_message += msg.content
                    message_callback(current_message)
            
            elif mode == "updates" and "__interrupt__" in data:
                # Get the current state
                current_state = self.graph.get_state(self.thread_config)
                if hasattr(current_state, "values"):
                    current_state = current_state.values
                
                # Check if more feedback is needed
                if (current_state.get("next_state", "") == "human_review" or 
                    current_state.get("current_state", "") == "human_review"):
                    
                    if status_callback:
                        status_callback("Additional human review required")
                    
                    # Return a status object indicating more feedback is needed
                    return {
                        "status": "feedback_required",
                        "message": current_message,
                        "state": current_state
                    }
        
        # If we get here, processing has completed
        final_state = self.graph.get_state(self.thread_config)
        if hasattr(final_state, "values"):
            final_state = final_state.values
        
        if status_callback:
            status_callback("Architecture analysis completed!")
        
        return {
            "status": "completed",
            "message": current_message,
            "state": final_state
        }


