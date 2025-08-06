# Orchestrator Module

## Overview
The orchestrator module is the core component that coordinates the execution of multiple agents in the multi-agent research system. It manages the sequential execution of agents, handles exceptions, caches intermediate outputs, and provides real-time progress updates through UI callbacks.

## Features Implemented

### 1. Dynamic Agent Loading
- Uses `importlib` to dynamically import agent classes at runtime
- Agents are loaded based on the `AGENT_SEQUENCE` configuration
- Graceful error handling if agents cannot be loaded

### 2. Ordered Agent Sequence
```python
AGENT_SEQUENCE = [
    "agents.research_agent.ResearchAgent",
    "agents.outline_agent.OutlineAgent", 
    "agents.writer_agent.WriterAgent",
    "agents.critic_agent.CriticAgent",
    "agents.revision_agent.RevisionAgent"
]
```

### 3. Core Orchestration Function
```python
def run(topic: str, ui_callbacks=None) -> AgentState
```
- Iterates through agents in sequence
- Passes outputs between agents
- Updates progress at each step
- Handles exceptions gracefully
- Caches intermediate outputs to disk
- Returns final state with all metadata

### 4. UI Callback Support
- Accepts optional `ui_callbacks` parameter
- Callback signature: `(progress: float, state: dict) -> None`
- Non-blocking updates for Streamlit integration
- Progress reported as percentage (0-100)
- State includes current agent, status, and messages

### 5. State Management
The `AgentState` dataclass tracks:
- Topic being processed
- Current agent being executed
- Completed and failed agents
- Intermediate outputs from each agent
- Error messages and tracebacks
- Start and end times
- Final output
- Overall status (initialized, running, completed, failed)

### 6. Exception Handling
- Each agent execution is wrapped in try-except
- Failures are logged with full tracebacks
- Orchestration can continue even if an agent fails (except the last one)
- All errors are captured in the state object

### 7. Output Caching
- Intermediate outputs are saved to `cache/` directory
- JSON format with timestamps
- File naming: `{topic}_{agent}_{timestamp}.json`
- Automatic directory creation

### 8. Logging
- Comprehensive logging at INFO level
- Detailed error messages at ERROR level
- Performance metrics (execution time)

## Usage Example

### Basic Usage
```python
from orchestrator import run

# Simple execution
state = run("Quantum Computing Applications")
print(state.final_output)
```

### With UI Callbacks (Streamlit Integration)
```python
from orchestrator import run

def update_ui(progress, state):
    st.progress(progress / 100)
    st.write(f"Current: {state['state']['current_agent']}")
    st.write(state['message'])

state = run("AI Ethics", ui_callbacks=update_ui)
```

### Advanced Usage with Custom Cache Directory
```python
from orchestrator import Orchestrator
from pathlib import Path

orchestrator = Orchestrator(cache_dir=Path("my_cache"))
state = orchestrator.run("Topic", ui_callbacks=my_callback)
```

## File Structure
```
orchestrator/
├── __init__.py          # Package initialization
├── orchestrator.py      # Main orchestrator implementation
├── test_orchestrator.py # Test script demonstrating features
└── README.md           # This documentation
```

## Integration with Streamlit
The orchestrator is designed to work seamlessly with Streamlit:

1. **Non-blocking updates**: UI callbacks allow real-time progress updates
2. **State management**: Complete state can be displayed in Streamlit widgets
3. **Error handling**: Errors are captured and can be displayed to users
4. **Progress tracking**: Progress percentage can drive Streamlit progress bars

## Next Steps
The orchestrator is fully implemented and ready. The next steps are:
1. Implement individual agent classes in the `agents/` directory
2. Each agent should have an `execute()` or `run()` method
3. Agents receive `topic`, `previous_output`, and `all_outputs` as inputs
4. Integrate with Streamlit UI for user interaction

## Testing
Run the test script to verify the orchestrator functionality:
```bash
python orchestrator/test_orchestrator.py
```

This will test:
- State management
- Dynamic agent loading (will fail as expected until agents are implemented)
- UI callback functionality
- Exception handling
