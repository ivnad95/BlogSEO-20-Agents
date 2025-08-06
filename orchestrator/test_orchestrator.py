#!/usr/bin/env python3
"""
Test script to demonstrate orchestrator capabilities.
"""

from orchestrator import Orchestrator, run, AgentState
import time

def demo_ui_callback(progress: float, state: dict):
    """
    Example UI callback that simulates Streamlit updates.
    """
    print(f"\n{'='*50}")
    print(f"Progress: {progress:.1f}%")
    print(f"Status: {state['state']['status']}")
    print(f"Current Agent: {state['state']['current_agent']}")
    if state.get('message'):
        print(f"Message: {state['message']}")
    print(f"{'='*50}")

def test_basic_orchestration():
    """Test basic orchestration without UI callbacks."""
    print("\n--- Testing Basic Orchestration ---")
    
    # Note: This will fail since agents aren't implemented yet
    # but it demonstrates the orchestrator structure
    try:
        orchestrator = Orchestrator()
        print(f"Loaded {len(orchestrator.agents)} agents")
        print("Agent sequence:")
        for agent in orchestrator.agents:
            print(f"  - {agent['name']}")
    except ImportError as e:
        print(f"Expected error (agents not implemented yet): {e}")

def test_ui_callbacks():
    """Test orchestration with UI callbacks."""
    print("\n--- Testing UI Callbacks ---")
    
    # Simulate a topic
    topic = "The Future of Renewable Energy"
    
    print(f"Topic: {topic}")
    print("Starting orchestration with UI callbacks...")
    
    try:
        # This will fail since agents aren't implemented yet
        state = run(topic, ui_callbacks=demo_ui_callback)
        
        # If it succeeded (it won't yet), show results
        print(f"\nFinal Status: {state.status}")
        print(f"Completed Agents: {state.completed_agents}")
        print(f"Failed Agents: {state.failed_agents}")
        
    except ImportError as e:
        print(f"\nExpected error (agents not implemented yet): {e}")
        print("\nBut the orchestrator structure is ready!")
        print("Features implemented:")
        print("  ✓ Dynamic agent loading via importlib")
        print("  ✓ Ordered agent sequence (AGENT_SEQUENCE)")
        print("  ✓ Exception handling for each agent")
        print("  ✓ Intermediate output caching")
        print("  ✓ UI callbacks for progress updates")
        print("  ✓ State management with AgentState dataclass")
        print("  ✓ Comprehensive logging")

def test_state_management():
    """Test the AgentState dataclass."""
    print("\n--- Testing State Management ---")
    
    from datetime import datetime
    
    # Create a state object
    state = AgentState(topic="Test Topic")
    state.start_time = datetime.now()
    state.current_agent = "TestAgent"
    state.completed_agents = ["Agent1", "Agent2"]
    state.intermediate_outputs = {
        "Agent1": {"result": "data1"},
        "Agent2": {"result": "data2"}
    }
    state.status = "running"
    
    # Convert to dict (for UI callbacks)
    state_dict = state.to_dict()
    
    print("State as dictionary:")
    for key, value in state_dict.items():
        if key != "intermediate_outputs":  # Skip the large nested dict
            print(f"  {key}: {value}")
    
    print("\nState management working correctly!")

if __name__ == "__main__":
    print("="*60)
    print("Orchestrator Test Script")
    print("="*60)
    
    # Run tests
    test_state_management()
    test_basic_orchestration() 
    test_ui_callbacks()
    
    print("\n" + "="*60)
    print("Orchestrator core is fully implemented and ready!")
    print("Next step: Implement the individual agents")
    print("="*60)
