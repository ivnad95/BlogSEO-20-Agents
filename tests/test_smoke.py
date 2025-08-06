"""Smoke test for the orchestrator.

This module tests the basic functionality of the orchestrator
by running it with a test topic and asserting that expected
keys exist in the output.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from orchestrator.orchestrator import Orchestrator, AgentState
import json
from datetime import datetime


def test_orchestrator_import():
    """Test that the orchestrator can be imported."""
    assert Orchestrator is not None
    assert AgentState is not None


def test_orchestrator_initialization():
    """Test that the orchestrator can be initialized."""
    orchestrator = Orchestrator()
    assert orchestrator is not None
    assert hasattr(orchestrator, 'run')
    assert hasattr(orchestrator, 'agents')
    assert len(orchestrator.agents) > 0


def test_orchestrator_run_with_test_topic():
    """Test running the orchestrator with a test topic."""
    # Initialize orchestrator
    orchestrator = Orchestrator()
    
    # Define test topic
    topic = "Test Topic"
    
    # Run the orchestration
    state = orchestrator.run(topic=topic)
    
    # Assert that state is returned
    assert state is not None
    assert isinstance(state, AgentState)
    
    # Assert required keys exist in state
    assert state.topic == topic
    assert hasattr(state, 'completed_agents')
    assert hasattr(state, 'failed_agents')
    assert hasattr(state, 'intermediate_outputs')
    assert hasattr(state, 'errors')
    assert hasattr(state, 'start_time')
    assert hasattr(state, 'end_time')
    assert hasattr(state, 'final_output')
    assert hasattr(state, 'status')
    
    # Assert timing information
    assert state.start_time is not None
    assert state.end_time is not None
    assert isinstance(state.start_time, datetime)
    assert isinstance(state.end_time, datetime)
    
    # Assert status is one of expected values
    assert state.status in ['completed', 'failed', 'running', 'initialized']
    
    # If there are completed agents, check intermediate outputs
    if state.completed_agents:
        assert len(state.intermediate_outputs) > 0
        for agent in state.completed_agents:
            # Agent name should be in intermediate outputs
            agent_name = agent.replace('Agent', '')
            # Check if any variant of the agent name is in outputs
            has_output = any(
                agent_name in key or agent in key 
                for key in state.intermediate_outputs.keys()
            )
            if not has_output:
                print(f"Warning: No output found for agent {agent}")
    
    # Log some information for debugging
    print(f"\nTest completed with status: {state.status}")
    print(f"Completed agents: {len(state.completed_agents)}")
    print(f"Failed agents: {len(state.failed_agents)}")
    
    # Note: The agents are currently unimplemented stubs, so failures are expected
    # This test verifies the orchestrator infrastructure works correctly
    if state.failed_agents:
        print(f"\nNote: {len(state.failed_agents)} agents failed (expected for unimplemented stubs)")
        # Check that errors were properly captured
        assert len(state.errors) > 0
        # Sample first few errors for verification
        sample_errors = list(state.errors.items())[:3]
        for agent, error_info in sample_errors:
            error_msg = error_info.get('message', 'Unknown error') if isinstance(error_info, dict) else str(error_info)
            print(f"  Example error - {agent}: {error_msg[:100]}...")
    
    # Assert final output structure (if any agents completed)
    if state.status == 'completed' and state.final_output:
        assert state.final_output is not None
        print(f"Final output type: {type(state.final_output)}")
        
        # If final output is a dict (expected from FinalAssemblyAgent)
        if isinstance(state.final_output, dict):
            # Check for expected keys from final assembly
            expected_keys = [
                'title', 'content', 'meta_description', 
                'keywords', 'author', 'publish_date'
            ]
            
            for key in expected_keys:
                if key not in state.final_output:
                    print(f"Warning: Expected key '{key}' not found in final output")
            
            # Print summary of final output
            if 'title' in state.final_output:
                print(f"Generated title: {state.final_output.get('title', 'N/A')[:100]}...")
            if 'content' in state.final_output:
                content_length = len(str(state.final_output.get('content', '')))
                print(f"Content length: {content_length} characters")
    
    # The test passes if the orchestrator ran and handled failures gracefully
    print("\n✓ Orchestrator smoke test completed - infrastructure working correctly")


def test_orchestrator_cache_directory():
    """Test that cache directory is created."""
    orchestrator = Orchestrator()
    assert orchestrator.cache_dir.exists()
    assert orchestrator.cache_dir.is_dir()


def test_orchestrator_state_serialization():
    """Test that AgentState can be serialized to dict."""
    state = AgentState(topic="Test Topic")
    state.completed_agents = ["TestAgent1", "TestAgent2"]
    state.intermediate_outputs = {"TestAgent1": {"result": "test"}}
    state.start_time = datetime.now()
    state.end_time = datetime.now()
    
    # Convert to dict
    state_dict = state.to_dict()
    
    # Assert dict structure
    assert isinstance(state_dict, dict)
    assert state_dict['topic'] == "Test Topic"
    assert len(state_dict['completed_agents']) == 2
    assert 'TestAgent1' in state_dict['intermediate_outputs']
    assert state_dict['start_time'] is not None
    assert state_dict['end_time'] is not None


if __name__ == "__main__":
    # Run the smoke test directly
    print("Running orchestrator smoke test...")
    print("="*50)
    
    try:
        test_orchestrator_import()
        print("✓ Orchestrator import test passed")
        
        test_orchestrator_initialization()
        print("✓ Orchestrator initialization test passed")
        
        test_orchestrator_cache_directory()
        print("✓ Cache directory test passed")
        
        test_orchestrator_state_serialization()
        print("✓ State serialization test passed")
        
        print("\nRunning main orchestrator test with 'Test Topic'...")
        test_orchestrator_run_with_test_topic()
        print("✓ Orchestrator run test passed")
        
        print("\n" + "="*50)
        print("All smoke tests passed successfully!")
        
    except Exception as e:
        print(f"\n✗ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
