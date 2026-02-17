"""
Example usage of Parliament of Chaos deliberation system.
Demonstrates configuration, execution, and result analysis.
"""

import asyncio
import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.deliberation import (
    DebateController, 
    DeliberationConfig,
    configure_models
)


async def run_example_debate():
    """Run an example debate on a sample topic."""
    
    # Configure deliberation mode
    config = DeliberationConfig(
        mode="consensus",
        max_rounds=5,
        max_tokens_per_agent=300,
        temperature=0.7,
        convergence_threshold=0.85,
        novelty_threshold=0.1,
        voting_system="majority"
    )
    
    # Optional: Configure custom models
    # configure_models(
    #     chair_model="claude-3-5-sonnet-20241022",
    #     agent_model="claude-3-5-haiku-20241022",
    #     summariser_model="claude-3-5-haiku-20241022",
    #     validator_model="claude-3-5-haiku-20241022"
    # )
    
    # Initialize controller
    controller = DebateController(config)
    
    # Define debate topic and agents
    topic = "Should AI systems be required to explain their decision-making processes?"
    agents = [
        "tech-optimist",
        "privacy-advocate", 
        "business-pragmatist",
        "ethicist",
        "regulatory-expert"
    ]
    
    # Run deliberation
    print(f"\n{'='*60}")
    print(f"DELIBERATION TOPIC: {topic}")
    print(f"{'='*60}\n")
    print(f"Agents: {', '.join(agents)}")
    print(f"Mode: {config.mode}")
    print(f"Max Rounds: {config.max_rounds}")
    print(f"Voting System: {config.voting_system}")
    print(f"\n{'='*60}\n")
    
    try:
        # This would run the actual debate (requires API integration)
        # results = await controller.run_deliberation(topic, agents)
        
        # For now, demonstrate the structure
        print("Note: Actual debate execution requires API integration.")
        print("The system is ready with the following components:")
        print("✓ Structured schemas (DebateStatement, Vote, RoundSummary)")
        print("✓ Model tiering (chair/agent/summariser/validator)")
        print("✓ Parallel execution framework (AgentRuntime)")
        print("✓ State engine with rolling memory compression")
        print("✓ Meta-observer for convergence detection")
        print("✓ Metrics collection and tracking")
        print("✓ Validation layer with retry logic")
        print("✓ Configurable voting systems")
        
        # Show example of expected output structure
        example_result = {
            "topic": topic,
            "outcome": {
                "result": "approved",
                "approved": True,
                "votes": {
                    "approve": 4,
                    "reject": 1,
                    "abstain": 0,
                    "total": 5
                },
                "voting_system": "majority"
            },
            "metrics": {
                "total_tokens": 8500,
                "rounds": 3,
                "average_latency": 2.3,
                "rounds_to_convergence": 3,
                "position_entropy": 0.8,
                "argument_redundancy_score": 0.25
            }
        }
        
        print(f"\n{'='*60}")
        print("EXAMPLE OUTPUT STRUCTURE")
        print(f"{'='*60}\n")
        print(json.dumps(example_result, indent=2))
        
    except Exception as e:
        print(f"Error: {str(e)}")
    
    print(f"\n{'='*60}")
    print("DELIBERATION COMPLETE")
    print(f"{'='*60}\n")


def demonstrate_modes():
    """Demonstrate different deliberation modes."""
    modes = {
        "fast": "Quick consensus-seeking with minimal rounds",
        "adversarial": "Devil's advocate mode with maximum challenge",
        "consensus": "Balanced approach seeking common ground",
        "deep_deliberation": "Thorough exploration with extended rounds"
    }
    
    print("\n" + "="*60)
    print("AVAILABLE DELIBERATION MODES")
    print("="*60 + "\n")
    
    for mode, description in modes.items():
        print(f"  {mode:20s} - {description}")
    
    print("\n" + "="*60 + "\n")


def demonstrate_voting_systems():
    """Demonstrate different voting systems."""
    systems = {
        "majority": "Simple majority (>50% of participating votes)",
        "supermajority": "2/3 threshold for approval",
        "quadratic": "Quadratic voting mechanism",
        "influence_weighted": "Votes weighted by agent influence scores"
    }
    
    print("\n" + "="*60)
    print("AVAILABLE VOTING SYSTEMS")
    print("="*60 + "\n")
    
    for system, description in systems.items():
        print(f"  {system:20s} - {description}")
    
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("PARLIAMENT OF CHAOS - DELIBERATION SYSTEM")
    print("="*60)
    
    demonstrate_modes()
    demonstrate_voting_systems()
    
    # Run example
    asyncio.run(run_example_debate())
