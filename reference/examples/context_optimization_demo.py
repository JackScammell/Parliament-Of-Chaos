"""
Example: Using Context Optimization in Parliament of Chaos

This script demonstrates how to use the context optimization system
to reduce token usage while maintaining debate quality.
"""

import asyncio
from reference.deliberation.core.context_manager import ContextManager
from reference.deliberation.models.schemas import (
    DebateStatement, RoundSummary, AgentPosition
)


def example_1_basic_usage():
    """Example 1: Basic context manager usage"""
    print("=" * 60)
    print("Example 1: Basic Context Manager Usage")
    print("=" * 60)
    
    # Create context manager
    manager = ContextManager(max_historical_rounds=3)
    
    # Start a debate round
    manager.start_new_round(0)
    print(f"✓ Started round 0")
    
    # Add agent statements
    statement1 = DebateStatement(
        agent_id="agent-1",
        position="Support the proposal",
        argument="This proposal will improve efficiency by reducing overhead and streamlining processes.",
        confidence=0.85
    )
    manager.add_statement(statement1)
    print(f"✓ Added statement from {statement1.agent_id}")
    
    statement2 = DebateStatement(
        agent_id="agent-2",
        position="Oppose the proposal",
        argument="The proposal introduces unnecessary complexity and may have unintended consequences.",
        confidence=0.75
    )
    manager.add_statement(statement2)
    print(f"✓ Added statement from {statement2.agent_id}")
    
    # Check token usage
    stats = manager.estimate_context_tokens("agent-1")
    print(f"\nToken Usage:")
    print(f"  - Immediate context: {stats['immediate']} tokens")
    print(f"  - Historical context: {stats['historical']} tokens")
    print(f"  - Total: {stats['total']} tokens")
    print(f"  - Estimated reduction: {stats['reduction_vs_full']:.1%}")
    
    # Compress round
    summary = RoundSummary(
        core_positions=["Support", "Oppose"],
        major_conflicts=["Implementation approach"],
        amendments=[],
        consensus_level=0.5
    )
    manager.compress_round(summary)
    print(f"\n✓ Compressed round 0")


def example_2_multi_round_debate():
    """Example 2: Multi-round debate with token tracking"""
    print("\n" + "=" * 60)
    print("Example 2: Multi-Round Debate with Token Tracking")
    print("=" * 60)
    
    manager = ContextManager(max_historical_rounds=3)
    
    # Simulate 5 rounds
    for round_num in range(5):
        print(f"\n--- Round {round_num} ---")
        manager.start_new_round(round_num)
        
        # Add statements
        for i in range(3):
            statement = DebateStatement(
                agent_id=f"agent-{i+1}",
                position=f"Position-{round_num}-{i+1}",
                argument=f"Argument for position {round_num}-{i+1} with detailed reasoning.",
                confidence=0.7 + i * 0.1
            )
            manager.add_statement(statement)
        
        # Track token usage
        manager.track_token_usage("agent-1")
        
        # Compress round
        summary = RoundSummary(
            core_positions=[f"Position-{round_num}"],
            major_conflicts=[],
            amendments=[],
            consensus_level=0.5 + round_num * 0.1
        )
        manager.compress_round(summary)
        
        # Show stats
        stats = manager.estimate_context_tokens("agent-1")
        print(f"  Total tokens: {stats['total']}")
    
    # Final statistics
    print("\n" + "-" * 60)
    print("Final Token Statistics:")
    final_stats = manager.get_token_statistics()
    print(f"  Average total tokens: {final_stats['average_total']:.1f}")
    print(f"  Max tokens used: {final_stats['max_total']}")
    print(f"  Min tokens used: {final_stats['min_total']}")
    print(f"  Calls tracked: {final_stats['calls_tracked']}")


def example_3_optimized_prompts():
    """Example 3: Building optimized prompts"""
    print("\n" + "=" * 60)
    print("Example 3: Building Optimized Prompts")
    print("=" * 60)
    
    manager = ContextManager(max_historical_rounds=3)
    manager.start_new_round(0)
    
    # Add a statement
    statement = DebateStatement(
        agent_id="agent-1",
        position="Support",
        argument="This is a good approach",
        confidence=0.8
    )
    manager.add_statement(statement)
    
    # Create agent position
    position = AgentPosition(
        stance="Pro",
        confidence=0.8,
        influence_score=1.0,
        stability_index=1.0
    )
    
    # Build optimized prompt
    prompt = manager.build_prompt_with_context(
        agent_id="agent-2",
        role="Debater",
        objective="Provide your position on the proposal",
        agent_position=position,
        topic="Should we implement feature X?",
        max_tokens=500
    )
    
    print("\nOptimized Prompt:")
    print("-" * 60)
    print(prompt)
    print("-" * 60)
    
    # Estimate tokens
    prompt_tokens = len(prompt.split()) // 0.75  # Rough estimate
    print(f"\nEstimated prompt tokens: ~{int(prompt_tokens)}")


def example_4_context_comparison():
    """Example 4: Compare legacy vs optimized context"""
    print("\n" + "=" * 60)
    print("Example 4: Legacy vs Optimized Context Comparison")
    print("=" * 60)
    
    # Legacy approach (verbose)
    legacy_context = {
        "round": 5,
        "policy_vector": {"policy-1": 0.5, "policy-2": 0.7},
        "open_amendments": ["Amendment A", "Amendment B"],
        "agent_positions": {
            "agent-1": "Support with conditions",
            "agent-2": "Oppose due to cost concerns",
            "agent-3": "Neutral pending review"
        },
        "full_transcript": [
            "Agent-1 said: This is a very long argument with many detailed points...",
            "Agent-2 responded: I have concerns about the proposal...",
            # ... many more entries
        ]
    }
    
    legacy_tokens = len(str(legacy_context)) // 4
    print(f"Legacy context tokens: ~{legacy_tokens}")
    
    # Optimized approach
    manager = ContextManager(max_historical_rounds=3)
    manager.start_new_round(5)
    
    for i in range(3):
        statement = DebateStatement(
            agent_id=f"agent-{i+1}",
            position=f"Position-{i+1}",
            argument=f"Detailed argument {i+1}",
            confidence=0.7 + i * 0.1
        )
        manager.add_statement(statement)
    
    optimized_stats = manager.estimate_context_tokens("agent-1")
    optimized_tokens = optimized_stats['total']
    
    print(f"Optimized context tokens: ~{optimized_tokens}")
    
    # Calculate savings
    savings = (legacy_tokens - optimized_tokens) / legacy_tokens * 100
    print(f"\nToken savings: {savings:.1f}%")
    print(f"Reduction factor: {legacy_tokens / optimized_tokens:.2f}x")


def example_5_semantic_retrieval():
    """Example 5: Using semantic retrieval (optional)"""
    print("\n" + "=" * 60)
    print("Example 5: Semantic Retrieval (Optional)")
    print("=" * 60)
    
    manager = ContextManager()
    
    # Simulate semantic retrieval results
    # In practice, these would come from a vector database
    results = [
        {
            "text": "Previous argument about budget allocation from session-1",
            "score": 0.92,
            "round": 3,
            "agent": "agent-5"
        },
        {
            "text": "Related discussion on implementation timeline",
            "score": 0.87,
            "round": 7,
            "agent": "agent-2"
        },
        {
            "text": "Cost-benefit analysis from earlier debate",
            "score": 0.81,
            "round": 2,
            "agent": "agent-1"
        }
    ]
    
    # Add to reference context
    manager.add_semantic_retrieval_result(
        query="budget allocation and timeline",
        results=results,
        top_k=3
    )
    
    print(f"✓ Added {len(results)} semantic retrieval results")
    print(f"\nReference context size: {manager.reference_context.estimate_tokens()} tokens")
    
    # Show reference context
    ref_json = manager.reference_context.to_structured_json()
    print(f"\nRelevant arguments retrieved:")
    for i, arg in enumerate(ref_json["relevant_arguments"], 1):
        print(f"  {i}. Score: {arg['score']:.2f} - {arg['text'][:60]}...")


def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("Parliament of Chaos - Context Optimization Examples")
    print("=" * 60)
    
    example_1_basic_usage()
    example_2_multi_round_debate()
    example_3_optimized_prompts()
    example_4_context_comparison()
    example_5_semantic_retrieval()
    
    print("\n" + "=" * 60)
    print("All examples completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
