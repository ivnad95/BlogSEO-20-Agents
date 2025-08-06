"""
BlogSEO v3 - AI-Powered Blog Generation Application
====================================================
A comprehensive Streamlit UI for generating SEO-optimized blog content
using a multi-agent orchestration system.
"""

import streamlit as st
import os
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import base64
from dotenv import load_dotenv, set_key
import sys

# Add project root to path
sys.path.append(str(Path(__file__).parent))

# Import orchestrator and utilities
from orchestrator.orchestrator import Orchestrator, AgentState
from orchestrator.enhanced_orchestrator import EnhancedOrchestrator
from utilities.exporters import BlogExporter, StreamlitExporter
from utilities.logger import get_logger

# Initialize logger
logger = get_logger("app")

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="BlogSEO v3 - AI Blog Generator",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Main container styling */
    .main {
        padding: 1rem;
    }
    
    /* Progress bar styling */
    .stProgress > div > div > div > div {
        background-color: #4CAF50;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #f0f2f6;
        border-radius: 5px;
        padding: 0.5rem;
        margin-bottom: 0.5rem;
    }
    
    /* Button styling */
    .stButton > button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: bold;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        background-color: #45a049;
        transform: translateY(-2px);
    }
    
    /* Success/Error message styling */
    .success-message {
        padding: 1rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        color: #155724;
        margin: 1rem 0;
    }
    
    .error-message {
        padding: 1rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        color: #721c24;
        margin: 1rem 0;
    }
    
    /* Agent output container */
    .agent-output {
        background-color: #ffffff;
        border: 1px solid #dee2e6;
        border-radius: 5px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    /* Logo styling */
    .logo-container {
        text-align: center;
        padding: 1rem 0;
        margin-bottom: 2rem;
    }
    
    /* Download button container */
    .download-container {
        display: flex;
        gap: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def load_logo():
    """Load and display project logo."""
    logo_path = Path("assets/logo.png")
    if logo_path.exists():
        with open(logo_path, "rb") as f:
            logo_data = base64.b64encode(f.read()).decode()
            return f'<img src="data:image/png;base64,{logo_data}" width="200">'
    else:
        return "🚀 **BlogSEO v3**"

def save_api_keys(openai_key: str, gemini_key: str, google_cse_id: str):
    """Save API keys to .env file."""
    env_file = Path(".env")
    
    # Create .env file if it doesn't exist
    if not env_file.exists():
        env_file.touch()
    
    # Save keys
    if openai_key:
        set_key(str(env_file), "OPENAI_API_KEY", openai_key)
    if gemini_key:
        set_key(str(env_file), "GEMINI_API_KEY", gemini_key)
    if google_cse_id:
        set_key(str(env_file), "GOOGLE_CSE_ID", google_cse_id)
    
    # Reload environment variables
    load_dotenv(override=True)

def validate_api_keys():
    """Validate that required API keys are present."""
    required_keys = ["OPENAI_API_KEY", "GEMINI_API_KEY"]
    missing_keys = []
    
    for key in required_keys:
        if not os.getenv(key):
            missing_keys.append(key)
    
    return len(missing_keys) == 0, missing_keys

def format_agent_output(agent_name: str, output: Any) -> str:
    """Format agent output for display."""
    if isinstance(output, dict):
        return f"**{agent_name}**\n```json\n{json.dumps(output, indent=2)}\n```"
    elif isinstance(output, list):
        return f"**{agent_name}**\n- " + "\n- ".join(str(item) for item in output)
    else:
        return f"**{agent_name}**\n{str(output)}"

def create_html_preview(content: Dict[str, Any]) -> str:
    """Create HTML preview from final output."""
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 800px;
                margin: 0 auto;
                padding: 2rem;
                background-color: #f9f9f9;
            }}
            h1 {{
                color: #2c3e50;
                border-bottom: 3px solid #3498db;
                padding-bottom: 0.5rem;
            }}
            h2 {{
                color: #34495e;
                margin-top: 2rem;
            }}
            h3 {{
                color: #7f8c8d;
            }}
            .meta {{
                color: #95a5a6;
                font-size: 0.9rem;
                margin: 1rem 0;
            }}
            .content {{
                background: white;
                padding: 2rem;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            blockquote {{
                border-left: 4px solid #3498db;
                padding-left: 1rem;
                color: #555;
                font-style: italic;
            }}
            code {{
                background: #ecf0f1;
                padding: 0.2rem 0.4rem;
                border-radius: 3px;
                font-family: 'Courier New', monospace;
            }}
            .tags {{
                margin: 1rem 0;
            }}
            .tag {{
                display: inline-block;
                background: #3498db;
                color: white;
                padding: 0.3rem 0.8rem;
                margin: 0.2rem;
                border-radius: 15px;
                font-size: 0.85rem;
            }}
        </style>
    </head>
    <body>
        <div class="content">
            <h1>{title}</h1>
            <div class="meta">
                <span>Generated on {date}</span> | 
                <span>Reading time: {reading_time} min</span>
            </div>
            <div class="tags">
                {tags}
            </div>
            <div class="article-content">
                {content}
            </div>
        </div>
    </body>
    </html>
    """
    
    # Extract data from content
    title = content.get("title", "Untitled Blog Post")
    tags = content.get("tags", [])
    tags_html = "".join([f'<span class="tag">{tag}</span>' for tag in tags])
    
    # Calculate reading time (rough estimate)
    word_count = len(str(content).split())
    reading_time = max(1, word_count // 200)
    
    # Format content
    article_content = ""
    if "sections" in content:
        for section in content["sections"]:
            article_content += f"<h2>{section.get('heading', '')}</h2>\n"
            article_content += f"<p>{section.get('content', '')}</p>\n"
    else:
        article_content = f"<p>{json.dumps(content, indent=2)}</p>"
    
    return html_template.format(
        title=title,
        date=datetime.now().strftime("%B %d, %Y"),
        reading_time=reading_time,
        tags=tags_html,
        content=article_content
    )

def create_markdown_content(content: Dict[str, Any]) -> str:
    """Create Markdown content from final output."""
    md_content = []
    
    # Title
    title = content.get("title", "Untitled Blog Post")
    md_content.append(f"# {title}\n")
    
    # Meta information
    md_content.append(f"*Generated on {datetime.now().strftime('%B %d, %Y')}*\n")
    
    # Tags
    if "tags" in content:
        tags = " ".join([f"`{tag}`" for tag in content["tags"]])
        md_content.append(f"\n**Tags:** {tags}\n")
    
    # Content sections
    if "sections" in content:
        for section in content["sections"]:
            md_content.append(f"\n## {section.get('heading', '')}\n")
            md_content.append(f"{section.get('content', '')}\n")
    else:
        md_content.append(f"\n```json\n{json.dumps(content, indent=2)}\n```\n")
    
    return "\n".join(md_content)

@st.cache_data(ttl=3600)
def generate_blog_cached(topic: str, _orchestrator, _callback_func):
    """Cached version of blog generation.
    
    Note: Parameters with leading underscores are not hashed by Streamlit.
    """
    return _orchestrator.run(topic, ui_callbacks=_callback_func)

def main():
    """Main application function."""
    
    # Initialize session state
    if "steps" not in st.session_state:
        st.session_state.steps = []
    if "generation_complete" not in st.session_state:
        st.session_state.generation_complete = False
    if "final_output" not in st.session_state:
        st.session_state.final_output = None
    if "current_progress" not in st.session_state:
        st.session_state.current_progress = 0
    if "current_agent" not in st.session_state:
        st.session_state.current_agent = None
    if "orchestrator_state" not in st.session_state:
        st.session_state.orchestrator_state = None
    if "intermediate_states" not in st.session_state:
        st.session_state.intermediate_states = []
    if "agent_outputs" not in st.session_state:
        st.session_state.agent_outputs = {}
    if "execution_history" not in st.session_state:
        st.session_state.execution_history = []
    
    # Sidebar
    with st.sidebar:
        # Logo
        st.markdown('<div class="logo-container">', unsafe_allow_html=True)
        st.markdown(load_logo(), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # API Key Configuration
        st.header("🔑 API Configuration")
        
        with st.expander("Configure API Keys", expanded=False):
            openai_key = st.text_input(
                "OpenAI API Key",
                value=os.getenv("OPENAI_API_KEY", ""),
                type="password",
                help="Your OpenAI API key for GPT models"
            )
            
            gemini_key = st.text_input(
                "Google Gemini API Key",
                value=os.getenv("GEMINI_API_KEY", ""),
                type="password",
                help="Your Google Gemini API key"
            )
            
            google_cse_id = st.text_input(
                "Google Custom Search Engine ID",
                value=os.getenv("GOOGLE_CSE_ID", ""),
                type="password",
                help="Your Google CSE ID for search functionality"
            )
            
            if st.button("💾 Save API Keys"):
                save_api_keys(openai_key, gemini_key, google_cse_id)
                st.success("API keys saved successfully!")
                time.sleep(1)
                st.rerun()
        
        # Validate API keys
        keys_valid, missing_keys = validate_api_keys()
        if keys_valid:
            st.success("✅ All required API keys configured")
        else:
            st.error(f"❌ Missing keys: {', '.join(missing_keys)}")
        
        st.markdown("---")
        
        # Generation Settings
        st.header("⚙️ Generation Settings")
        
        cache_results = st.checkbox(
            "Enable Result Caching",
            value=True,
            help="Cache generated content to avoid redundant API calls"
        )
        
        auto_export = st.checkbox(
            "Auto-export on completion",
            value=False,
            help="Automatically export all formats when generation completes"
        )
        
        st.markdown("---")
        
        # About section
        st.header("ℹ️ About")
        st.markdown("""
        **BlogSEO v3** is an AI-powered blog generation system that uses multiple specialized agents to create high-quality, SEO-optimized content.
        
        **Features:**
        - 🤖 20+ specialized AI agents
        - 📊 Real-time progress tracking
        - 📝 Multiple export formats
        - 🎨 HTML preview
        - 🔍 SEO optimization
        - 💾 Result caching
        
        **Version:** 3.0.0  
        **Author:** BlogSEO Team
        """)
    
    # Main content area
    st.title("✍️ BlogSEO v3 - AI Blog Generator")
    st.markdown("Generate high-quality, SEO-optimized blog content with AI-powered agents")
    
    # Input section
    col1, col2 = st.columns([3, 1])
    
    with col1:
        blog_topic = st.text_input(
            "📝 Enter Blog Topic",
            placeholder="e.g., 'The Future of Artificial Intelligence in Healthcare'",
            help="Enter the topic you want to generate a blog post about"
        )
    
    with col2:
        generate_button = st.button(
            "🚀 Generate Blog",
            type="primary",
            disabled=not keys_valid or not blog_topic,
            use_container_width=True
        )
    
    # Generation process
    if generate_button and blog_topic:
        st.session_state.steps = []
        st.session_state.generation_complete = False
        st.session_state.current_progress = 0
        
        # Create progress containers
        progress_container = st.container()
        status_container = st.container()
        
        with progress_container:
            st.markdown("### 📊 Generation Progress")
            progress_bar = st.progress(0)
            progress_text = st.empty()
        
        with status_container:
            status_placeholder = st.empty()
        
        # Callback function for orchestrator updates
        def update_callback(progress: float, state: Dict[str, Any]):
            # Update session state
            st.session_state.current_progress = progress
            st.session_state.orchestrator_state = state
            
            # Extract state information
            state_dict = state.get("state", {})
            message = state.get("message", "")
            current_agent = state_dict.get("current_agent", "")
            completed = state_dict.get("completed_agents", [])
            intermediate_outputs = state_dict.get("intermediate_outputs", {})
            
            # Store intermediate state for user inspection/manual edits
            st.session_state.intermediate_states.append({
                "progress": progress,
                "message": message,
                "current_agent": current_agent,
                "timestamp": datetime.now().isoformat(),
                "state_snapshot": state_dict.copy()
            })
            
            # Update progress bar
            progress_bar.progress(min(progress / 100, 1.0))
            progress_text.text(f"Progress: {progress:.1f}% - {message}")
            
            # Store agent outputs for inspection
            if intermediate_outputs:
                st.session_state.agent_outputs = intermediate_outputs.copy()
            
            # Add to steps if new agent completed
            if current_agent and message.startswith("Completed"):
                agent_output = intermediate_outputs.get(current_agent.replace("Agent", ""), {})
                st.session_state.steps.append({
                    "agent": current_agent,
                    "status": "completed",
                    "output": agent_output,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Add to execution history
                st.session_state.execution_history.append({
                    "type": "agent_complete",
                    "agent": current_agent,
                    "timestamp": datetime.now().isoformat(),
                    "output_size": len(str(agent_output))
                })
        
        # Initialize enhanced orchestrator with lambda support
        with st.spinner("🔄 Initializing orchestrator..."):
            try:
                orchestrator = EnhancedOrchestrator()
            except Exception as e:
                # Fallback to basic orchestrator if enhanced fails
                logger.warning(f"Enhanced orchestrator failed, using basic: {e}")
                orchestrator = Orchestrator()
        
        # Run orchestration with enhanced callbacks
        with st.spinner(f"🤖 Generating blog post about '{blog_topic}'..."):
            try:
                if cache_results:
                    # For cached version, use regular callback
                    result = generate_blog_cached(blog_topic, orchestrator, update_callback)
                else:
                    # Use basic run method without caching
                    result = orchestrator.run(blog_topic, ui_callbacks=update_callback)
                
                st.session_state.final_output = result.final_output
                st.session_state.generation_complete = True
                
                # Show success message
                status_placeholder.success(f"✅ Blog post generated successfully in {(result.end_time - result.start_time).total_seconds():.1f} seconds!")
                
            except Exception as e:
                status_placeholder.error(f"❌ Generation failed: {str(e)}")
                logger.error(f"Generation error: {str(e)}")
    
    # Display results
    if st.session_state.generation_complete and st.session_state.final_output:
        st.markdown("---")
        st.header("📄 Generated Content")
        
        # Create tabs for different views
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Agent Outputs", "🔍 Intermediate States", "👁️ HTML Preview", "📝 Markdown", "📥 Export"])
        
        with tab1:
            st.markdown("### 🤖 Agent Processing Steps")
            
            # Display each agent's output in an expander
            for i, step in enumerate(st.session_state.steps, 1):
                agent_name = step["agent"]
                with st.expander(f"Step {i}: {agent_name}", expanded=False):
                    st.markdown(f"**Status:** ✅ {step['status']}")
                    st.markdown(f"**Timestamp:** {step['timestamp']}")
                    st.markdown("**Output:**")
                    
                    # Format and display output
                    if isinstance(step["output"], dict):
                        st.json(step["output"])
                    elif isinstance(step["output"], list):
                        for item in step["output"]:
                            st.write(f"- {item}")
                    else:
                        st.code(str(step["output"]))
        
        with tab2:
            st.markdown("### 🔍 Intermediate States for Inspection")
            
            # Display intermediate states for user inspection and potential manual edits
            st.info("💡 These intermediate states are stored in session state for inspection and manual editing")
            
            # Show current agent outputs
            if st.session_state.agent_outputs:
                st.subheader("📦 Current Agent Outputs")
                
                # Allow user to select which agent output to inspect
                agent_names = list(st.session_state.agent_outputs.keys())
                selected_agent = st.selectbox(
                    "Select agent output to inspect:",
                    agent_names,
                    help="Choose an agent to view its output in detail"
                )
                
                if selected_agent:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**{selected_agent} Output:**")
                    with col2:
                        if st.button("📋 Copy to Clipboard", key=f"copy_{selected_agent}"):
                            st.success("Copied!")
                    
                    # Display output with editing capability
                    agent_output = st.session_state.agent_outputs[selected_agent]
                    
                    # Show in editable text area for potential manual modifications
                    edited_output = st.text_area(
                        "Output (editable):",
                        value=json.dumps(agent_output, indent=2) if isinstance(agent_output, (dict, list)) else str(agent_output),
                        height=300,
                        key=f"edit_{selected_agent}",
                        help="You can manually edit this output if needed"
                    )
                    
                    # Save edited output back to session state
                    if st.button(f"💾 Save Changes to {selected_agent}", key=f"save_{selected_agent}"):
                        try:
                            # Try to parse as JSON first
                            st.session_state.agent_outputs[selected_agent] = json.loads(edited_output)
                            st.success(f"Changes saved to {selected_agent}")
                        except json.JSONDecodeError:
                            # If not JSON, save as string
                            st.session_state.agent_outputs[selected_agent] = edited_output
                            st.success(f"Changes saved to {selected_agent} as text")
            
            # Show intermediate state history
            if st.session_state.intermediate_states:
                st.subheader("📈 Processing History")
                
                # Create a timeline view
                for i, state in enumerate(st.session_state.intermediate_states[-10:], 1):  # Show last 10 states
                    with st.expander(f"State {i}: {state.get('message', 'Processing...')}", expanded=False):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Progress", f"{state.get('progress', 0):.1f}%")
                            st.text(f"Agent: {state.get('current_agent', 'N/A')}")
                        with col2:
                            st.text(f"Timestamp: {state.get('timestamp', 'N/A')}")
                        
                        # Show state snapshot if available
                        if 'state_snapshot' in state:
                            st.json(state['state_snapshot'])
            
            # Export intermediate states
            st.subheader("📤 Export Intermediate States")
            col1, col2 = st.columns(2)
            
            with col1:
                # Export all intermediate states
                if st.button("📥 Download All States", use_container_width=True):
                    states_export = {
                        "timestamp": datetime.now().isoformat(),
                        "topic": blog_topic if 'blog_topic' in locals() else "Unknown",
                        "intermediate_states": st.session_state.intermediate_states,
                        "agent_outputs": st.session_state.agent_outputs
                    }
                    st.download_button(
                        label="💾 Download States JSON",
                        data=json.dumps(states_export, indent=2),
                        file_name=f"intermediate_states_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
            
            with col2:
                # Clear intermediate states
                if st.button("🗑️ Clear All States", use_container_width=True):
                    st.session_state.intermediate_states = []
                    st.session_state.agent_outputs = {}
                    st.success("Intermediate states cleared")
                    st.rerun()
        
        with tab3:
            st.markdown("### 🌐 HTML Preview")
            
            # Generate HTML preview
            html_content = create_html_preview(st.session_state.final_output)
            
            # Display in iframe
            st.components.v1.html(html_content, height=800, scrolling=True)
        
        with tab4:
            st.markdown("### 📝 Markdown View")
            
            # Generate markdown content
            markdown_content = create_markdown_content(st.session_state.final_output)
            
            # Display markdown
            st.markdown(markdown_content)
        
        with tab5:
            st.markdown("### 📥 Export Options")
            
            # Prepare content for export
            final_output = st.session_state.final_output
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # HTML Export
                html_export = create_html_preview(final_output)
                st.download_button(
                    label="📄 Download HTML",
                    data=html_export,
                    file_name=f"blog_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                    mime="text/html",
                    use_container_width=True
                )
            
            with col2:
                # Markdown Export
                markdown_export = create_markdown_content(final_output)
                st.download_button(
                    label="📝 Download Markdown",
                    data=markdown_export,
                    file_name=f"blog_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                    mime="text/markdown",
                    use_container_width=True
                )
            
            with col3:
                # JSON Export
                json_export = json.dumps(final_output, indent=2, ensure_ascii=False)
                st.download_button(
                    label="📊 Download JSON",
                    data=json_export,
                    file_name=f"blog_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )
            
            # Additional export options
            st.markdown("#### 🎯 Advanced Export Options")
            
            export_cols = st.columns(2)
            
            with export_cols[0]:
                # WordPress XML Export
                if st.button("🌐 Generate WordPress XML", use_container_width=True):
                    # TODO: Implement WordPress XML generation
                    st.info("WordPress XML export will be available in the next update")
            
            with export_cols[1]:
                # Bundle Export
                if st.button("📦 Download Complete Bundle", use_container_width=True):
                    # TODO: Implement bundle creation
                    st.info("Bundle export will be available in the next update")
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #888; padding: 1rem;'>
            <p>BlogSEO v3 © 2024 | Powered by AI | Made with ❤️ using Streamlit</p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
