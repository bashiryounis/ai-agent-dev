import streamlit as st
from agent import ArchitectureProcessor
import streamlit.components.v1 as components
from workflow import create_agent_graph
from helper import render_mermaid_code, display_mermaid  # Import the new function

# Page configuration
st.set_page_config(page_title="Architecture Analysis Agent", layout="wide")

# Hide Streamlit's default top bar and footer
st.markdown(
    """
    <style>
        header {visibility: hidden;}
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True
)

# ----- Session State Initialization -----
if 'processor' not in st.session_state:
    graph = create_agent_graph()
    st.session_state.processor = ArchitectureProcessor(graph)

defaults = {
    "processing": False,
    "feedback_requested": False,
    "mermaid_code": None,
    "user_input": "",
    "current_message": "",
    "messages": [],
    "form_submitted": False,
    "result": None,
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ----- Callbacks -----
def handle_submit():
    text = st.session_state.get("input_area", "").strip()
    if text:
        st.session_state.user_input = text
        st.session_state.messages.append({"role": "user", "content": text})
        st.session_state.processing = True
        st.session_state.form_submitted = True

def handle_feedback():
    feedback_text = st.session_state.get("feedback_input", "").strip()
    if feedback_text:
        st.session_state.messages.append({"role": "user", "content": feedback_text})
        st.session_state.feedback_requested = False
        st.session_state.processing = True
        st.session_state.feedback_text = feedback_text

def message_handler(message):
    """Updates the streaming placeholder with partial assistant messages."""
    st.session_state.current_message = message
    if "streaming_placeholder" in st.session_state:
        st.session_state.streaming_placeholder.markdown(
            f"<div class='assistant-message'><strong>Assistant:</strong> {message}</div>",
            unsafe_allow_html=True
        )

def status_handler(status):
    st.session_state.status = status

# ----- Custom CSS -----
st.markdown("""
<style>
    /* Keep the main title but modify styling as needed */
    .main-title {
        margin-bottom: 0 !important;
    }

    /* Remove any extra decorative bars */
    .decoration {
        display: none !important;
    }
    .css-1dp5vir, .css-1v3fvcr, .css-1wrcr25, .block-container::before {
        display: none !important;
    }

    /* Additional styles for UI components */
    .stTextArea textarea {
        min-height: 200px !important;
    }
    .message-container {

    }
    .assistant-message {
        line-height: 1.6;
        white-space: pre-wrap;
        margin-bottom: 1rem;
    }
    .stButton button {
        width: 100%;
    }
    
    /* Improved mermaid container styling */
    .mermaid-container {
        width: 100%;
        height: 600px;
        overflow: auto;
        background-color: white;
        border: 1px solid #f0f2f6;
        border-radius: 5px;
        padding: 10px;
        margin: auto;
        position: relative;
    }
    
    /* Make sure SVG elements are visible */
    .mermaid-container svg {
        max-width: 100%;
        height: auto !important;
        display: block;
        margin: 0 auto;
    }
    
    /* Better tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 40px;
        white-space: pre-wrap;
        border-radius: 4px 4px 0 0;
    }
    
    /* Loading state improvement */
    .stSpinner {
        text-align: center;
        margin: 20px 0;
    }
    
    /* Feedback box styling */
    .feedback-box {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 10px;
        margin-top: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# ----- Page Title -----
st.markdown("<h1 class='main-title'>Real-Time Architecture Analysis Agent</h1>", unsafe_allow_html=True)

# ----- Layout: Two Columns -----
col1, col2 = st.columns([1.5, 1])  # Slightly wider left column

# ================================
# LEFT COLUMN (Conversation & Form)
# ================================
with col1:
    # If not submitted yet, show the input form
    if not st.session_state.form_submitted:
        with st.form("input_form"):
            st.text_area(
                "Describe your system architecture in detail:",
                placeholder="Enter your project description here...",
                height=200,
                key="input_area"
            )
            st.form_submit_button("Start Architecture Analysis", on_click=handle_submit)

    # Conversation container
    conversation_box = st.container()
    with conversation_box:
        st.markdown("<div class='message-container'>", unsafe_allow_html=True)

        # Show only assistant messages (skip user messages)
        for msg in st.session_state.messages:
            if msg.get("role") == "assistant":
                st.markdown(
                    f"<div class='assistant-message'><strong>Assistant:</strong> {msg.get('content', '')}</div>",
                    unsafe_allow_html=True
                )

        # Placeholder for streaming text
        if "streaming_placeholder" not in st.session_state:
            st.session_state.streaming_placeholder = st.empty()

        # After all messages, show status messages here
        if st.session_state.result:
            # If feedback is required
            if st.session_state.feedback_requested:
                st.info("Human review required. Please provide feedback below.")
            # If analysis completed
            elif st.session_state.result.get("status") == "completed":
                st.success("Architecture analysis completed!")

        st.markdown("</div>", unsafe_allow_html=True)

# ================================
# RIGHT COLUMN (Diagram & Code)
# ================================
with col2:
    st.subheader("Visualization")
    diagram_tab, code_tab = st.tabs(["Diagram", "Mermaid Code"])

    with diagram_tab:
        if st.session_state.mermaid_code:
            # Use the new client-side rendering method with fullscreen support
            html_content = display_mermaid(st.session_state.mermaid_code)
            if html_content:
                components.html(
                    html_content,
                    height=1000,
                    scrolling=True
                )
            else:
                st.error("There was an error rendering the Mermaid diagram.")
        else:
            st.info("The architecture diagram will appear here once generated.")

    with code_tab:
        if st.session_state.mermaid_code:
            st.code(st.session_state.mermaid_code, language="mermaid")
        else:
            st.info("The Mermaid code will appear here once generated.")

# ================================
# PROCESSING LOGIC
# ================================
if st.session_state.processing:
    # Add a spinner to show visual feedback during processing
    with st.spinner("Processing architecture..."):
        if hasattr(st.session_state, "feedback_text") and st.session_state.feedback_text:
            # Continue with feedback
            try:
                result = st.session_state.processor.continue_with_feedback(
                    st.session_state.feedback_text,
                    message_callback=message_handler,
                    status_callback=status_handler
                )
                del st.session_state.feedback_text
            except Exception as e:
                st.error(f"Error processing feedback: {str(e)}")
                result = {
                    "status": "error",
                    "message": f"Error: {str(e)}",
                    "state": st.session_state.result.get("state", {}) if st.session_state.result else {}
                }
        else:
            # Initial processing
            try:
                result = st.session_state.processor.start_processing(
                    st.session_state.user_input,
                    message_callback=message_handler,
                    status_callback=status_handler
                )
            except Exception as e:
                st.error(f"Error processing input: {str(e)}")
                result = {
                    "status": "error", 
                    "message": f"Error: {str(e)}",
                    "state": {}
                }

        st.session_state.result = result

        # Check if more feedback is needed
        if result["status"] == "feedback_required":
            st.session_state.feedback_requested = True
        else:
            st.session_state.feedback_requested = False

        # Save final assistant message
        st.session_state.messages.append({"role": "assistant", "content": result["message"]})

        # Save mermaid code if available
        if "mermaid_code" in result.get("state", {}):
            st.session_state.mermaid_code = result["state"]["mermaid_code"]

    # Set processing to false after all work is done
    st.session_state.processing = False
    st.rerun()  # Use a single rerun at the end of processing

# ================================
# FEEDBACK SECTION
# ================================
if st.session_state.feedback_requested and st.session_state.form_submitted:
    feedback_container = st.container()
    with feedback_container:
        st.markdown("<div class='feedback-box'>", unsafe_allow_html=True)
        col_input, col_button = st.columns([4, 1])

        with col_input:
            st.text_input(
                "Your feedback:",
                placeholder="Provide feedback or type 'done'",
                key="feedback_input"
            )

        with col_button:
            st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)
            if st.button("Submit", on_click=handle_feedback):
                pass  # No need for rerun here as handle_feedback sets processing=True

        st.markdown("</div>", unsafe_allow_html=True)

# ================================
# RESET BUTTON
# ================================
if st.session_state.form_submitted:
    if st.button("Start Over"):
        processor = st.session_state.processor
        for key in list(st.session_state.keys()):
            if key != "processor":
                del st.session_state[key]
        st.session_state.processor = processor
        st.rerun()

# Removed the extra horizontal rule ("---") at the bottom
st.markdown("Architecture Analysis Agent - Built with Streamlit, LangGraph and LLMs")