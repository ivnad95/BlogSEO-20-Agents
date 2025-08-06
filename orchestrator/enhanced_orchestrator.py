"""
Enhanced orchestrator with lambda callback support.

This module extends the base orchestrator to support lambda functions
for progress callbacks, enabling more flexible UI updates and state tracking.
"""

from typing import Any, Dict, List, Optional, Callable, Union
from dataclasses import dataclass
import logging
from pathlib import Path

from .orchestrator import Orchestrator, AgentState, AGENT_SEQUENCE

logger = logging.getLogger(__name__)


class EnhancedOrchestrator(Orchestrator):
    """Enhanced orchestrator with lambda callback support for UI updates."""
    
    def __init__(self, cache_dir: Optional[Path] = None):
        """Initialize the enhanced orchestrator."""
        super().__init__(cache_dir)
        self.progress_callbacks: List[Callable] = []
        self.state_callbacks: List[Callable] = []
        self.agent_callbacks: Dict[str, List[Callable]] = {}
    
    def add_progress_callback(self, callback: Callable) -> None:
        """
        Add a progress callback function.
        
        Args:
            callback: Function that accepts (progress: float, total_agents: int, current_index: int)
        """
        self.progress_callbacks.append(callback)
    
    def add_state_callback(self, callback: Callable) -> None:
        """
        Add a state callback function.
        
        Args:
            callback: Function that accepts (state: AgentState)
        """
        self.state_callbacks.append(callback)
    
    def add_agent_callback(self, agent_name: str, callback: Callable) -> None:
        """
        Add a callback for a specific agent.
        
        Args:
            agent_name: Name of the agent to attach callback to
            callback: Function that accepts (agent_name: str, output: Any, state: AgentState)
        """
        if agent_name not in self.agent_callbacks:
            self.agent_callbacks[agent_name] = []
        self.agent_callbacks[agent_name].append(callback)
    
    def run_with_lambdas(
        self,
        topic: str,
        progress_lambda: Optional[Callable[[int, str, AgentState], None]] = None,
        state_lambda: Optional[Callable[[AgentState], None]] = None,
        agent_lambdas: Optional[Dict[str, Callable[[str, Any, AgentState], None]]] = None
    ) -> AgentState:
        """
        Run orchestration with lambda callbacks.
        
        Args:
            topic: The research topic to process
            progress_lambda: Lambda for progress updates, e.g., 
                            lambda i, agent, state: progress_bar.progress((i+1)/len(seq))
            state_lambda: Lambda for state updates, e.g.,
                         lambda state: st.session_state.update({'current_state': state})
            agent_lambdas: Dict of agent-specific lambdas
        
        Returns:
            AgentState: Final state containing all outputs and metadata
        
        Example:
            >>> orchestrator = EnhancedOrchestrator()
            >>> result = orchestrator.run_with_lambdas(
            ...     "AI Ethics",
            ...     progress_lambda=lambda i, agent, state: progress_bar.progress((i+1)/20),
            ...     state_lambda=lambda state: save_state(state),
            ...     agent_lambdas={
            ...         "TrendIdeaAgent": lambda name, out, state: log_trend(out)
            ...     }
            ... )
        """
        # Create a unified callback that triggers all lambdas
        def unified_callback(progress: float, state_dict: Dict[str, Any]):
            state = state_dict.get("state", {})
            current_agent = state.get("current_agent", "")
            completed_agents = state.get("completed_agents", [])
            
            # Calculate agent index
            agent_index = len(completed_agents)
            
            # Trigger progress lambda
            if progress_lambda and current_agent:
                try:
                    # Create a minimal AgentState object for the lambda
                    agent_state = AgentState(
                        topic=topic,
                        current_agent=current_agent,
                        completed_agents=completed_agents,
                        intermediate_outputs=state.get("intermediate_outputs", {})
                    )
                    progress_lambda(agent_index, current_agent, agent_state)
                except Exception as e:
                    logger.warning(f"Progress lambda failed: {e}")
            
            # Trigger state lambda
            if state_lambda:
                try:
                    agent_state = AgentState(
                        topic=topic,
                        current_agent=current_agent,
                        completed_agents=completed_agents,
                        intermediate_outputs=state.get("intermediate_outputs", {})
                    )
                    state_lambda(agent_state)
                except Exception as e:
                    logger.warning(f"State lambda failed: {e}")
            
            # Trigger agent-specific lambdas
            if agent_lambdas and current_agent in agent_lambdas:
                try:
                    outputs = state.get("intermediate_outputs", {})
                    if current_agent in outputs:
                        agent_state = AgentState(
                            topic=topic,
                            current_agent=current_agent,
                            completed_agents=completed_agents,
                            intermediate_outputs=outputs
                        )
                        agent_lambdas[current_agent](
                            current_agent,
                            outputs[current_agent],
                            agent_state
                        )
                except Exception as e:
                    logger.warning(f"Agent lambda for {current_agent} failed: {e}")
        
        # Run the base orchestrator with our unified callback
        return super().run(topic, ui_callbacks=unified_callback)
    
    def run_with_incremental_updates(
        self,
        topic: str,
        update_interval: int = 1,
        on_agent_start: Optional[Callable[[str, int, int], None]] = None,
        on_agent_complete: Optional[Callable[[str, Any, float], None]] = None,
        on_progress: Optional[Callable[[float], None]] = None
    ) -> AgentState:
        """
        Run with incremental update callbacks.
        
        Args:
            topic: The research topic to process
            update_interval: How often to trigger progress updates (in agents)
            on_agent_start: Called when an agent starts
            on_agent_complete: Called when an agent completes
            on_progress: Called for progress updates
        
        Returns:
            AgentState: Final state containing all outputs and metadata
        """
        agent_count = len(self.agents)
        
        def callback_wrapper(progress: float, state_dict: Dict[str, Any]):
            state = state_dict.get("state", {})
            message = state_dict.get("message", "")
            current_agent = state.get("current_agent", "")
            completed = len(state.get("completed_agents", []))
            
            # Handle agent start
            if message.startswith("Running") and on_agent_start:
                try:
                    on_agent_start(current_agent, completed + 1, agent_count)
                except Exception as e:
                    logger.warning(f"on_agent_start callback failed: {e}")
            
            # Handle agent completion
            if message.startswith("Completed") and on_agent_complete:
                try:
                    outputs = state.get("intermediate_outputs", {})
                    agent_output = outputs.get(current_agent, {})
                    on_agent_complete(current_agent, agent_output, progress)
                except Exception as e:
                    logger.warning(f"on_agent_complete callback failed: {e}")
            
            # Handle progress updates
            if on_progress and completed % update_interval == 0:
                try:
                    on_progress(progress)
                except Exception as e:
                    logger.warning(f"on_progress callback failed: {e}")
        
        return super().run(topic, ui_callbacks=callback_wrapper)


def create_streamlit_callbacks(progress_bar, status_text, session_state):
    """
    Create callbacks optimized for Streamlit UI updates.
    
    Args:
        progress_bar: Streamlit progress bar widget
        status_text: Streamlit text widget for status
        session_state: Streamlit session state
    
    Returns:
        tuple: (progress_lambda, state_lambda, agent_lambdas)
    
    Example:
        >>> progress_bar = st.progress(0)
        >>> status_text = st.empty()
        >>> callbacks = create_streamlit_callbacks(progress_bar, status_text, st.session_state)
        >>> orchestrator.run_with_lambdas("Topic", *callbacks)
    """
    # Progress lambda: Update progress bar
    progress_lambda = lambda i, agent, state: (
        progress_bar.progress((i + 1) / len(AGENT_SEQUENCE)),
        status_text.text(f"Processing: {agent} ({i+1}/{len(AGENT_SEQUENCE)})")
    )
    
    # State lambda: Store intermediate states
    state_lambda = lambda state: session_state.intermediate_states.append({
        "topic": state.topic,
        "current_agent": state.current_agent,
        "completed_agents": state.completed_agents.copy(),
        "outputs": state.intermediate_outputs.copy()
    })
    
    # Agent lambdas: Store individual agent outputs
    agent_lambdas = {}
    for agent_path in AGENT_SEQUENCE:
        agent_name = agent_path.split(".")[-1]
        agent_lambdas[agent_name] = lambda name, output, state: (
            session_state.agent_outputs.update({name: output})
        )
    
    return progress_lambda, state_lambda, agent_lambdas


def create_progress_chain(*callbacks):
    """
    Chain multiple progress callbacks together.
    
    Args:
        *callbacks: Variable number of callback functions
    
    Returns:
        Callable: A function that calls all provided callbacks
    
    Example:
        >>> update_ui = lambda p: progress_bar.progress(p/100)
        >>> log_progress = lambda p: logger.info(f"Progress: {p}%")
        >>> chained = create_progress_chain(update_ui, log_progress)
    """
    def chained_callback(progress: float, state: Dict[str, Any]):
        for callback in callbacks:
            try:
                callback(progress, state)
            except Exception as e:
                logger.warning(f"Chained callback failed: {e}")
    
    return chained_callback
