import streamlit as st
from orchestrator.orchestrator import Orchestrator
import os
import json

# --- Page Configuration ---
st.set_page_config(
    page_title="AI SEO Content Generator",
    page_icon="🤖",
    layout="wide",
)

st.title("🤖 AI SEO Content Generator")
st.markdown("This tool uses a multi-agent workflow to generate a comprehensive, SEO-optimized blog post.")

# --- Session State Initialization ---
if 'process_started' not in st.session_state:
    st.session_state.process_started = False
    st.session_state.final_state = None
    st.session_state.error = None
    st.session_state.api_key_configured = False

# --- API Key Configuration ---
with st.sidebar:
    st.header("🔑 API Configuration")
    st.markdown("You must provide a Google Gemini API Key to run the agent workflow.")
    gemini_api_key = st.text_input(
        "Google Gemini API Key",
        value=os.getenv("GEMINI_API_KEY", ""),
        type="password",
        help="Your Google Gemini API key is required to run the agents."
    )
    if st.button("Save API Key"):
        if gemini_api_key:
            os.environ['GEMINI_API_KEY'] = gemini_api_key
            st.session_state.api_key_configured = True
            st.success("API Key configured!")
        else:
            st.session_state.api_key_configured = False
            st.error("Please enter a valid API Key.")

# Check if key is configured in session
if not st.session_state.api_key_configured and os.getenv("GEMINI_API_KEY"):
    st.session_state.api_key_configured = True

# --- Main Application ---
st.header("1. Enter Your Topic")
topic = st.text_input("Blog Post Topic:", placeholder="e.g., The Future of Renewable Energy")

if st.button("🚀 Generate Article", disabled=not topic or not st.session_state.api_key_configured):
    st.session_state.process_started = True
    st.session_state.final_state = None
    st.session_state.error = None

    with st.spinner("Orchestrating AI agents... This may take several minutes."):
        try:
            # Instantiate and run the orchestrator
            orchestrator = Orchestrator()
            final_state = orchestrator.run(topic)

            if "error" in final_state:
                st.session_state.error = final_state["error"]
            else:
                st.session_state.final_state = final_state

        except Exception as e:
            st.session_state.error = f"A critical error occurred: {e}"
            import traceback
            st.error(traceback.format_exc())


# --- Display Results ---
if st.session_state.process_started:
    st.markdown("---")
    st.header("2. Results")

    if st.session_state.error:
        st.error(f"An error occurred during generation: {st.session_state.error}")

    elif st.session_state.final_state:
        st.success("🎉 Content generation complete!")

        final_package = st.session_state.final_state.get('final_package', {})
        html_file_path = final_package.get('html_file')
        zip_file_path = final_package.get('zip_archive')

        st.subheader("Final Article Preview")
        if html_file_path and os.path.exists(html_file_path):
            with open(html_file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            st.components.v1.html(html_content, height=600, scrolling=True)
        else:
            st.warning("Could not find HTML file to preview.")

        st.subheader("Download Your Content")
        if zip_file_path and os.path.exists(zip_file_path):
            with open(zip_file_path, "rb") as f:
                st.download_button(
                    label="📦 Download Complete Package (.zip)",
                    data=f,
                    file_name=os.path.basename(zip_file_path),
                    mime="application/zip"
                )
        else:
            st.warning("Could not find zip archive to download.")
            st.json(st.session_state.final_state) # Display final state for debugging

    else:
        # This part will show while the spinner is active
        st.info("Generation in progress... Please wait for the process to complete.")
