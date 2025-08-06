""" 
Core orchestrator for multi-agent research system.

This module coordinates the execution of multiple agents in sequence,
handles exceptions, caches intermediate outputs, and provides UI callbacks
for real-time progress updates.
"""

import importlib
import logging
from typing import Any, Dict, List, Optional, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import traceback
import json
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the ordered sequence of agents to execute
AGENT_SEQUENCE = [
    "agents.trend_idea.TrendIdeaAgent",
    "agents.user_input.UserInputAgent",
    "agents.keyword_mining.KeywordMiningAgent",
    "agents.competitor_scan.CompetitorScanAgent",
    "agents.outline_generator.OutlineGeneratorAgent",
    "agents.draft_writer.DraftWriterAgent",
    "agents.keyword_enrichment.KeywordEnrichmentAgent",
    "agents.readability.ReadabilityAgent",
    "agents.humanization.HumanizationAgent",
    "agents.style_consistency.StyleConsistencyAgent",
    "agents.tone_check.ToneCheckAgent",
    "agents.internal_linking.InternalLinkingAgent",
    "agents.external_link_vetting.ExternalLinkVettingAgent",
    "agents.image_optimization.ImageOptimizationAgent",
    "agents.alt_text.AltTextAgent",
    "agents.onpage_seo.OnPageSEOAgent",
    "agents.technical_seo.TechnicalSEOAgent",
    "agents.schema_enhancement.SchemaEnhancementAgent",
    "agents.qa_validation.QAValidationAgent",
    "agents.final_assembly.FinalAssemblyAgent"
]

@dataclass
class AgentState:
    """Represents the state of the orchestration process."""
    topic: str
    current_agent: Optional[str] = None
    completed_agents: List[str] = field(default_factory=list)
    failed_agents: List[str] = field(default_factory=list)
    intermediate_outputs: Dict[str, Any] = field(default_factory=dict)
    errors: Dict[str, str] = field(default_factory=dict)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    final_output: Optional[Any] = None
    status: str = "initialized"  # initialized, running, completed, failed

    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary for serialization."""
        return {
            "topic": self.topic,
            "current_agent": self.current_agent,
            "completed_agents": self.completed_agents,
            "failed_agents": self.failed_agents,
            "intermediate_outputs": self.intermediate_outputs,
            "errors": self.errors,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "final_output": self.final_output,
            "status": self.status
        }


class Orchestrator:
    """Orchestrates the execution of multiple agents in sequence."""
    
    def __init__(self, cache_dir: Optional[Path] = None):
        """
        Initialize the orchestrator.
        
        Args:
            cache_dir: Directory for caching intermediate outputs
        """
        self.cache_dir = cache_dir or Path("cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.agents = []
        self._load_agents()
    
    def _load_agents(self) -> None:
        """Dynamically load agent classes from the configured sequence."""
        for agent_path in AGENT_SEQUENCE:
            try:
                module_path, class_name = agent_path.rsplit(".", 1)
                module = importlib.import_module(module_path)
                agent_class = getattr(module, class_name)
                self.agents.append({
                    "path": agent_path,
                    "class": agent_class,
                    "name": class_name
                })
                logger.info(f"Successfully loaded agent: {agent_path}")
            except Exception as e:
                logger.error(f"Failed to load agent {agent_path}: {str(e)}")
                raise ImportError(f"Cannot load agent {agent_path}: {str(e)}")
    
    def _cache_output(self, agent_name: str, output: Any, state: AgentState) -> None:
        """
        Cache intermediate output to disk.
        
        Args:
            agent_name: Name of the agent that produced the output
            output: The output to cache
            state: Current orchestration state
        """
        try:
            cache_file = self.cache_dir / f"{state.topic.replace(' ', '_')}_{agent_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            cache_data = {
                "agent": agent_name,
                "topic": state.topic,
                "timestamp": datetime.now().isoformat(),
                "output": output if isinstance(output, (dict, list, str, int, float, bool)) else str(output)
            }
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
            logger.info(f"Cached output for {agent_name} to {cache_file}")
        except Exception as e:
            logger.warning(f"Failed to cache output for {agent_name}: {str(e)}")
    
    def _update_progress(self, 
                        ui_callbacks: Optional[Callable],
                        progress: float,
                        state: AgentState,
                        message: Optional[str] = None) -> None:
        """
        Update progress via UI callbacks if provided.
        
        Args:
            ui_callbacks: Callback function for UI updates
            progress: Progress percentage (0-100)
            state: Current orchestration state
            message: Optional status message
        """
        if ui_callbacks:
            try:
                callback_data = {
                    "progress": progress,
                    "state": state.to_dict(),
                    "message": message
                }
                ui_callbacks(progress, callback_data)
            except Exception as e:
                logger.warning(f"UI callback failed: {str(e)}")
    
    def run(self, 
            topic: str, 
            ui_callbacks: Optional[Callable[[float, Dict], None]] = None) -> AgentState:
        """
        Run the orchestration process for a given topic.
        
        This method iterates through all configured agents in sequence,
        passing outputs between them, handling exceptions, and updating
        progress via callbacks.
        
        Args:
            topic: The research topic to process
            ui_callbacks: Optional callback function for UI updates.
                         Should accept (progress: float, state: dict)
        
        Returns:
            AgentState: Final state containing all outputs and metadata
        """
        # Initialize state
        state = AgentState(topic=topic)
        state.start_time = datetime.now()
        state.status = "running"
        
        logger.info(f"Starting orchestration for topic: {topic}")
        self._update_progress(ui_callbacks, 0, state, f"Starting research on: {topic}")
        
        # Calculate progress increment per agent
        progress_increment = 100.0 / len(self.agents)
        current_progress = 0.0
        
        # Previous agent's output to pass to next agent
        previous_output = None
        
        # Iterate through agents in sequence
        for i, agent_info in enumerate(self.agents):
            agent_name = agent_info["name"]
            agent_class = agent_info["class"]
            
            try:
                # Update current agent
                state.current_agent = agent_name
                logger.info(f"Executing agent: {agent_name}")
                
                # Update progress - agent starting
                self._update_progress(
                    ui_callbacks,
                    current_progress,
                    state,
                    f"Running {agent_name}..."
                )
                
                # Instantiate and run the agent
                agent_instance = agent_class()
                
                # Prepare state for agent
                agent_state = {
                    "topic": topic,
                    "previous_output": previous_output,
                    "all_outputs": state.intermediate_outputs.copy(),
                    "current_agent": agent_name,
                    "completed_agents": state.completed_agents.copy()
                }
                
                # Execute agent
                if hasattr(agent_instance, 'execute'):
                    output = agent_instance.execute(agent_state)
                elif hasattr(agent_instance, 'run'):
                    output = agent_instance.run(agent_state)
                else:
                    # Fallback to calling the instance directly
                    output = agent_instance(agent_state)
                
                # Store output
                state.intermediate_outputs[agent_name] = output
                state.completed_agents.append(agent_name)
                previous_output = output
                
                # Cache the output
                self._cache_output(agent_name, output, state)
                
                # Update progress - agent completed
                current_progress += progress_increment
                self._update_progress(
                    ui_callbacks,
                    current_progress,
                    state,
                    f"Completed {agent_name}"
                )
                
                logger.info(f"Successfully completed agent: {agent_name}")
                
            except Exception as e:
                # Handle agent failure
                error_msg = f"Agent {agent_name} failed: {str(e)}"
                error_trace = traceback.format_exc()
                
                logger.error(error_msg)
                logger.debug(error_trace)
                
                state.failed_agents.append(agent_name)
                state.errors[agent_name] = {
                    "message": str(e),
                    "traceback": error_trace
                }
                
                # Update progress with error
                self._update_progress(
                    ui_callbacks,
                    current_progress,
                    state,
                    f"Error in {agent_name}: {str(e)}"
                )
                
                # Decide whether to continue or abort
                if i < len(self.agents) - 1:  # Not the last agent
                    logger.warning(f"Continuing despite failure in {agent_name}")
                    # Still increment progress to show we're moving forward
                    current_progress += progress_increment
                else:
                    # Last agent failed, mark as failed
                    state.status = "failed"
                    break
        
        # Finalize state
        state.end_time = datetime.now()
        state.current_agent = None
        
        # Set final output and status
        if state.failed_agents and not state.completed_agents:
            state.status = "failed"
            state.final_output = None
        elif state.completed_agents:
            state.status = "completed"
            # Final output is the last successful agent's output
            if state.completed_agents:
                last_agent = state.completed_agents[-1]
                state.final_output = state.intermediate_outputs.get(last_agent)
        
        # Final progress update
        final_progress = 100.0 if state.status == "completed" else current_progress
        self._update_progress(
            ui_callbacks,
            final_progress,
            state,
            f"Orchestration {state.status}"
        )
        
        # Log summary
        duration = (state.end_time - state.start_time).total_seconds()
        logger.info(f"Orchestration completed in {duration:.2f} seconds")
        logger.info(f"Status: {state.status}")
        logger.info(f"Completed agents: {', '.join(state.completed_agents)}")
        if state.failed_agents:
            logger.warning(f"Failed agents: {', '.join(state.failed_agents)}")
        
        return state


# Convenience function for simple usage
def run(topic: str, ui_callbacks: Optional[Callable[[float, Dict], None]] = None) -> AgentState:
    """
    Run the orchestration process for a given topic.
    
    This is a convenience function that creates an Orchestrator instance
    and runs it with the provided topic and callbacks.
    
    Args:
        topic: The research topic to process
        ui_callbacks: Optional callback function for UI updates.
                     Should accept (progress: float, state: dict)
    
    Returns:
        AgentState: Final state containing all outputs and metadata
    
    Example:
        >>> state = run("Quantum Computing Applications")
        >>> print(state.final_output)
        
        >>> # With UI callbacks
        >>> def update_ui(progress, state):
        ...     print(f"Progress: {progress}%")
        >>> state = run("AI Ethics", ui_callbacks=update_ui)
    """
    orchestrator = Orchestrator()
    return orchestrator.run(topic, ui_callbacks)


if __name__ == "__main__":
    # Example usage
    def example_callback(progress: float, state: Dict):
        """Example callback for testing."""
        print(f"Progress: {progress:.1f}% - {state.get('message', '')}")
    
    # Test run
    test_topic = "Artificial Intelligence in Healthcare"
    print(f"Testing orchestrator with topic: {test_topic}")
    
    try:
        result = run(test_topic, ui_callbacks=example_callback)
        print(f"\nOrchestration completed!")
        print(f"Status: {result.status}")
        print(f"Completed agents: {result.completed_agents}")
        if result.failed_agents:
            print(f"Failed agents: {result.failed_agents}")
    except Exception as e:
        print(f"Orchestration failed: {str(e)}")
