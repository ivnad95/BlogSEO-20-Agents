# Technical Implementation Brief: 20-Agent SEO Workflow with Streamlit UI

This document provides the definitive guidance for developers implementing the **20-agent SEO workflow** in the Streamlit application. The system relies on **LangChain** and **Google Gemini** models for each AI agent. Streamlit acts as the orchestrator, invoking agents sequentially while maintaining state between reruns.

## 1. Core Streamlit Integration Principles

### 1.1 State Management with `st.session_state`
The workflow persists progress and intermediate results using `st.session_state` to survive Streamlit's rerun behaviour.

```python
import streamlit as st

if "process_started" not in st.session_state:
    st.session_state.process_started = False
    st.session_state.current_agent_index = 0
    st.session_state.content_brief = {}
    st.session_state.ui_logs = []
    st.session_state.final_output = None
```

### 1.2 Asynchronous Execution and User Feedback
Each interaction triggers only the next agent to keep the UI responsive. Use a progress bar, status text, and log expander to inform the user.

```python
progress_bar = st.progress(0)
status_text = st.empty()
log_container = st.expander("View Detailed Logs")

percent = st.session_state.current_agent_index / 20
progress_bar.progress(percent)
status_text.info(f"⏳ Running: {current_agent_name}...")
log_container.write(st.session_state.ui_logs)
```

### 1.3 Caching Strategy
Two caching layers keep the app efficient:

1. **`langchain.llm_cache`** – configure a SQLite cache for Gemini calls.
2. **`@st.cache_resource`** – cache heavy objects such as LanguageTool or BERTopic models.

```python
@st.cache_resource
def load_language_tool():
    return LanguageTool('en-US')
```

## 2. The 20-Agent Workflow in Streamlit

| # | Agent | Gemini Model | UI Feedback |
|---|------|--------------|-------------|
|A1|Input Processor|`gemini-2.0-flash-lite`|User enters topic; "Generate" starts chain|
|A2|Trend & Angle Hunter|`gemini-2.0-flash-lite`|Status: "Running Trend & Angle Hunter"|
|A3|Search Intent Classifier|`gemini-2.0-flash-lite`|Display detected intent|
|A4|Competitor Scraper|`gemini-2.0-flash-lite`|Log "Scraped competitors"|
|A5|Keyword Extraction|`gemini-2.5-flash`|Show keyword cluster in expander|
|A6|Topical Authority Modeler|`gemini-2.5-flash`|List topic clusters|
|A7|Outline Architect|`gemini-2.5-flash`|Render markdown outline|
|A8|Expert Draft Writer|`gemini-2.5-flash`|Notify when draft ready|
|A9|Humanization Agent|`gemini-2.5-flash`|Log "Draft humanized"|
|A10|Readability Improver|`gemini-2.5-flash`|Log "Readability improved"|
|A11|Tone & Style Agent|`gemini-2.5-flash`|Log "Tone applied"|
|A12|Grammar & Syntax Agent|`gemini-2.0-flash-lite`|Log "Grammar checked"|
|A13|Keyword Integration Agent|`gemini-2.5-flash`|Log "Keywords integrated"|
|A14|Fact-Checking Agent|`gemini-2.5-flash`|Show verification report|
|A15|Image Prompt Engineer|`gemini-2.5-flash`|Log "Image prompts generated"|
|A16|Image & Alt Text Agent|`gemini-2.0-flash-preview-image-generation` + `gemini-2.0-flash-lite`|Display images and alt text|
|A17|Linking Strategist|`gemini-2.5-flash`|Log link strategy|
|A18|Schema & HTML Assembler|`gemini-2.0-flash-lite`|Log "HTML assembled"|
|A19|Originality & QA Agent|`gemini-2.5-flash`|Show QA metrics|
|A20|Final Package Agent|N/A|Render final article and download button|

## 3. Project Directory Structure

```
BlogSEO-20-Agents/
├── app.py                # Streamlit UI orchestrator
├── orchestrator/         # Orchestration logic
│   ├── orchestrator.py
│   └── enhanced_orchestrator.py
├── agents/               # 20 agent modules
│   ├── base_agent.py     # LangChain + Gemini setup
│   ├── trend_idea.py
│   ├── keyword_mining.py
│   └── ... up to final_assembly.py
├── utilities/            # Shared helpers and exporters
├── requirements.txt      # Dependencies including langchain-google-genai
└── TECHNICAL_BRIEF.md    # This guide
```

## 4. Agent Template Example

Each agent subclasses `BaseAgent` to access Gemini models through LangChain.

```python
from agents.base_agent import BaseAgent

class IntentClassifierAgent(BaseAgent):
    def run(self, state: dict) -> dict:
        system = "You are an expert SEO analyst."
        user = f"Classify search intent for: {state['topic']}"
        response = self.execute_prompt(system, user)
        state['search_intent'] = self.parse_json_response(response)
        return state
```

## 5. Streamlit Orchestrator Pattern

`app.py` imports a list of agent modules and runs them sequentially while updating `st.session_state`.

```python
import importlib
from config import AGENT_MODULE_LIST

if st.button("Generate Article"):
    st.session_state.process_started = True
    st.session_state.content_brief = {"topic": user_topic}

if st.session_state.process_started:
    name = AGENT_MODULE_LIST[st.session_state.current_agent_index]
    agent_module = importlib.import_module(f"agents.{name}")
    st.session_state.content_brief = agent_module.run_agent(st.session_state.content_brief)
    st.session_state.current_agent_index += 1
    st.rerun()
```

## 6. Key Takeaways

- **LangChain + Gemini:** Every agent uses Gemini models via LangChain for consistency and caching.
- **Session State:** Maintains long-running workflow across Streamlit reruns.
- **Modularity:** Each agent lives in its own file under `agents/`.
- **User Feedback:** Progress bar, status messages, and logs keep users informed.
- **Caching:** Combine `langchain.llm_cache` and `st.cache_resource` for speed and cost control.

This brief serves as the primary reference for developing and maintaining the 20-agent Streamlit application.
