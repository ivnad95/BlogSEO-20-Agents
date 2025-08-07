"""
Core orchestrator for the multi-agent SEO content generation system.
This module coordinates the sequential execution of agents, manages the
evolving state of the content brief, and handles logging and error reporting.
"""

import importlib
import logging
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime
import traceback
import json
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# The correct, logical sequence of agents for the full workflow
AGENT_SEQUENCE = [
    "agents.user_input.UserInputAgent",
    "agents.trend_idea.TrendIdeaAgent",
    "agents.intent_classifier.IntentClassifierAgent",
    "agents.competitor_scan.CompetitorScanAgent",
    "agents.keyword_mining.KeywordMiningAgent",
    "agents.outline_generator.OutlineGeneratorAgent",
    "agents.draft_writer.DraftWriterAgent",
    "agents.humanization.HumanizationAgent",
    "agents.readability.ReadabilityAgent",
    "agents.tone_check.ToneCheckAgent",
    "agents.style_consistency.StyleConsistencyAgent",
    "agents.qa_validation.QAValidationAgent",
    "agents.keyword_enrichment.KeywordEnrichmentAgent",
    "agents.internal_linking.InternalLinkingAgent",
    "agents.external_link_vetting.ExternalLinkVettingAgent",
    "agents.onpage_seo.OnPageSEOAgent",
    "agents.technical_seo.TechnicalSEOAgent",
    "agents.schema_enhancement.SchemaEnhancementAgent",
    "agents.image_optimization.ImageOptimizationAgent",
    "agents.alt_text.AltTextAgent",
    "agents.final_assembly.FinalAssemblyAgent",
]


class Orchestrator:
    """Orchestrates the sequential execution of the agent workflow."""
    
    def __init__(self, cache_dir: Optional[Path] = None):
        """Initializes the orchestrator and loads the agent classes."""
        self.cache_dir = cache_dir or Path("cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.agents = self._load_agents()
    
    def _load_agents(self) -> List[Dict[str, Any]]:
        """Dynamically loads agent classes from the AGENT_SEQUENCE."""
        loaded_agents = []
        for agent_path in AGENT_SEQUENCE:
            try:
                module_path, class_name = agent_path.rsplit(".", 1)
                module = importlib.import_module(module_path)
                agent_class = getattr(module, class_name)
                loaded_agents.append({
                    "path": agent_path,
                    "class": agent_class,
                    "name": class_name
                })
                logger.info(f"Successfully loaded agent: {class_name}")
            except Exception as e:
                logger.error(f"Failed to load agent {agent_path}: {e}")
                raise ImportError(f"Cannot load agent {agent_path}: {e}")
        return loaded_agents
    
    def _log_state(self, agent_name: str, state: Dict[str, Any]) -> None:
        """Logs the output of an agent for debugging and caching."""
        try:
            topic = state.get('topic', 'unknown_topic').replace(' ', '_')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            cache_file = self.cache_dir / f"{topic}_{agent_name}_{timestamp}.json"

            # Create a serializable version of the state
            loggable_state = {}
            for key, value in state.items():
                try:
                    json.dumps(value)
                    loggable_state[key] = value
                except (TypeError, OverflowError):
                    loggable_state[key] = str(value)

            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(loggable_state, f, indent=2)
            logger.info(f"State after {agent_name} cached to {cache_file}")
        except Exception as e:
            logger.warning(f"Failed to log state for {agent_name}: {e}")
    
    def run(self, topic: str, ui_callback: Optional[Callable[[Dict], None]] = None) -> Dict[str, Any]:
        """
        Runs the full agent pipeline for a given topic.

        Args:
            topic: The initial topic for content generation.
            ui_callback: An optional function to call for UI updates.
                         It receives a dictionary with progress and status.

        Returns:
            The final state dictionary after all agents have run.
        """
        # Initialize the state
        master_state = {"topic": topic}
        total_agents = len(self.agents)
        start_time = datetime.now()
        
        logger.info(f"Orchestration started for topic: '{topic}'")
        if ui_callback:
            ui_callback({"progress": 0, "status": f"Starting process for '{topic}'..."})

        for i, agent_info in enumerate(self.agents):
            agent_name = agent_info["name"]
            agent_class = agent_info["class"]
            
            logger.info(f"--- Running Agent {i+1}/{total_agents}: {agent_name} ---")
            if ui_callback:
                ui_callback({"progress": (i / total_agents), "status": f"Running: {agent_name}..."})

            try:
                # Instantiate and run the agent
                agent_instance = agent_class()
                master_state = agent_instance.run(master_state.copy()) # Pass a copy to prevent side effects

                # Check for errors returned by the agent
                if isinstance(master_state, dict) and 'error' in master_state:
                    raise Exception(master_state['error'])
                
                self._log_state(agent_name, master_state)
                logger.info(f"Successfully completed agent: {agent_name}")

            except Exception as e:
                error_message = f"Agent '{agent_name}' failed: {e}"
                logger.error(error_message)
                logger.error(traceback.format_exc())
                if ui_callback:
                    ui_callback({"progress": ((i + 1) / total_agents), "status": f"ERROR in {agent_name}: {e}", "error": True})
                # Terminate the process on failure
                return {"error": error_message, "final_state": master_state}

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        logger.info(f"Orchestration completed successfully in {duration:.2f} seconds.")
        if ui_callback:
            ui_callback({"progress": 1.0, "status": "Process complete!", "final_state": master_state})

        return master_state
