import sys
import os
from pathlib import Path
import pytest

# Add project root to path to allow importing modules from the app
sys.path.insert(0, str(Path(__file__).parent.parent))
from orchestrator.orchestrator import Orchestrator

@pytest.fixture(scope="module")
def orchestrator_instance():
    """
    Pytest fixture to initialize the orchestrator once for all tests in this module.
    It sets a dummy API key to allow agent initialization without making real calls.
    """
    # This dummy key is necessary for the agent classes to be instantiated without error.
    os.environ['GEMINI_API_KEY'] = 'DUMMY_API_KEY_FOR_TESTING_PURPOSES'
    return Orchestrator()

def test_orchestrator_initialization(orchestrator_instance):
    """
    Tests that the Orchestrator class can be initialized and that it successfully
    loads the agent classes defined in the AGENT_SEQUENCE.
    """
    assert orchestrator_instance is not None, "Orchestrator instance should not be None"
    assert hasattr(orchestrator_instance, 'run'), "Orchestrator should have a 'run' method"
    assert hasattr(orchestrator_instance, 'agents'), "Orchestrator should have an 'agents' attribute"
    # Check that our full list of 18 agents was loaded
    assert len(orchestrator_instance.agents) == 18, "Orchestrator should load all 18 agents"
    print("\n✓ Orchestrator initialized and all 18 agents loaded successfully.")

def test_orchestrator_run_handles_api_error_gracefully(orchestrator_instance):
    """
    Tests that a full run of the orchestrator with a dummy API key fails gracefully.
    This is a smoke test to ensure the pipeline is wired correctly and that the
    orchestrator's error handling works as expected when an agent fails on an API call.
    """
    test_topic = "The Psychology of Color in Marketing"
    print(f"\nRunning orchestrator smoke test with topic: '{test_topic}'")
    print("Expecting a graceful failure due to dummy API key...")
    
    # Run the orchestrator. We expect it to fail when the first agent (TrendIdeaAgent)
    # tries to use the dummy API key.
    final_state = orchestrator_instance.run(topic=test_topic)

    # 1. Verify that the final state indicates an error.
    assert isinstance(final_state, dict), "Final state should be a dictionary"
    assert 'error' in final_state, "Final state should contain an 'error' key on failure"
    
    # 2. Verify that the error message is informative.
    error_message = final_state['error']
    assert "failed" in error_message, "Error message should indicate failure"
    # The first agent to make a call is TrendIdeaAgent
    assert "TrendIdeaAgent" in error_message, "Error message should name the failing agent"
    print(f"✓ Orchestrator correctly caught expected failure: {error_message}")

    # 3. Verify that the state before the error is still available for debugging.
    assert 'final_state' in final_state, "Final state should contain the last known state"
    last_known_state = final_state['final_state']
    assert last_known_state.get('topic') == test_topic, "Last known state should still contain the topic"
    print("✓ Final state dictionary contains debug information as expected.")
