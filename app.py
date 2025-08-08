"""Streamlit front end for the BlogSEO multi‑agent system.

This module exposes a simple user interface that collects an article topic and
an API key, then delegates the heavy lifting to the :class:`Orchestrator`.
The previous implementation grew organically and was difficult to maintain.
This rewrite focuses on clarity, modularity and resilient error handling.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict

import streamlit as st

from orchestrator.orchestrator import Orchestrator


# ---------------------------------------------------------------------------
# Session state helpers
# ---------------------------------------------------------------------------

def init_session_state() -> None:
    """Populate default keys used across the application.

    Streamlit persists ``st.session_state`` between reruns.  Initialising the
    keys up‑front keeps the rest of the code tidy and guards against ``KeyError``
    instances if Streamlit is forced to rerun mid‑process.
    """

    defaults = {
        "api_key_configured": bool(os.getenv("GEMINI_API_KEY")),
        "process_started": False,
        "final_state": None,
        "error": None,
    }

    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


# ---------------------------------------------------------------------------
# Sidebar configuration
# ---------------------------------------------------------------------------

def render_sidebar() -> None:
    """Render the API key configuration controls in the sidebar."""

    with st.sidebar:
        st.header("🔑 API Configuration")
        st.markdown(
            "A valid Google Gemini API key is required to run the agent "
            "workflow."
        )

        api_key = st.text_input(
            "Google Gemini API Key",
            value=os.getenv("GEMINI_API_KEY", ""),
            type="password",
            help="Your Google Gemini API key",
        )

        if st.button("Save API Key"):
            if api_key:
                os.environ["GEMINI_API_KEY"] = api_key
                st.session_state.api_key_configured = True
                st.success("API Key configured!")
            else:
                st.session_state.api_key_configured = False
                st.error("Please enter a valid API Key.")


# ---------------------------------------------------------------------------
# Generation logic
# ---------------------------------------------------------------------------

def run_generation(topic: str) -> None:
    """Execute the orchestrator and persist results in session state."""

    st.session_state.process_started = True
    st.session_state.final_state = None
    st.session_state.error = None

    with st.spinner("Orchestrating AI agents... This may take several minutes."):
        try:
            orchestrator = Orchestrator()
            final_state = orchestrator.run(topic)

            if isinstance(final_state, dict) and "error" in final_state:
                st.session_state.error = final_state["error"]
            else:
                st.session_state.final_state = final_state
        except Exception as exc:  # pragma: no cover - defensive
            st.session_state.error = str(exc)


# ---------------------------------------------------------------------------
# Result rendering
# ---------------------------------------------------------------------------

def render_results() -> None:
    """Display the generation results or any encountered errors."""

    if not st.session_state.process_started:
        return

    st.markdown("---")
    st.header("2. Results")

    if st.session_state.error:
        st.error(f"An error occurred during generation: {st.session_state.error}")
        return

    final_state: Dict[str, Any] | None = st.session_state.final_state
    if not final_state:
        st.info("Generation in progress... Please wait for completion.")
        return

    st.success("🎉 Content generation complete!")
    final_package = final_state.get("final_package", {})

    html_file = final_package.get("html_file")
    if html_file and Path(html_file).exists():
        st.subheader("Final Article Preview")
        with open(html_file, "r", encoding="utf-8") as handle:
            st.components.v1.html(handle.read(), height=600, scrolling=True)
    else:
        st.warning("Could not find HTML file to preview.")

    zip_file = final_package.get("zip_archive")
    if zip_file and Path(zip_file).exists():
        st.subheader("Download Your Content")
        with open(zip_file, "rb") as handle:
            st.download_button(
                label="📦 Download Complete Package (.zip)",
                data=handle,
                file_name=Path(zip_file).name,
                mime="application/zip",
            )
    else:
        st.warning("Could not find zip archive to download.")


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Entry point for the Streamlit application."""

    st.set_page_config(
        page_title="AI SEO Content Generator",
        page_icon="🤖",
        layout="wide",
    )

    st.title("🤖 AI SEO Content Generator")
    st.markdown(
        "This tool uses a multi-agent workflow to generate a comprehensive, "
        "SEO-optimised blog post."
    )

    init_session_state()
    render_sidebar()

    st.header("1. Enter Your Topic")
    with st.form("topic_form"):
        topic = st.text_input(
            "Blog Post Topic:",
            placeholder="e.g., The Future of Renewable Energy",
        )
        submitted = st.form_submit_button(
            "🚀 Generate Article",
            disabled=not st.session_state.api_key_configured,
        )

        if submitted:
            if not topic:
                st.error("Please provide a topic before generating.")
            else:
                run_generation(topic)

    render_results()


if __name__ == "__main__":  # pragma: no cover
    main()

