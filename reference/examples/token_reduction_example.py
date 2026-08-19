"""
Example: Token-Optimized Multi-Agent Debate

This example demonstrates the session token reduction features
in the Parliament of Chaos system.
"""

from reference.deliberation.core.context_manager import ContextManager
from reference.deliberation.core.token_counter import SessionTokenMonitor, TokenBudgetEnforcer
from reference.deliberation.models.schemas import DebateStatement, RoundSummary, AgentPosition


def run_token_optimized_debate():
    """Run a multi-round debate with token optimization."""
    
    print("=" * 60)
    print("Token-Optimized Multi-Agent Debate Example")
    print("=" * 60)
    
    # Initialize components
    context_manager = ContextManager(
        max_historical_rounds=3,
        model_name="gpt-4",
        enable_deduplication=True,
        enable_pruning=True,
        min_confidence=0.5
    )
    
    monitor = SessionTokenMonitor(
        max_tokens_per_round=10000,
        compression_threshold=0.8
    )
    
    enforcer = TokenBudgetEnforcer(max_tokens_per_agent=500)
    
    # Simulate 3 rounds of debate
    for round_num in range(3):
        print(f"\n{'=' * 60}")
        print(f"Round {round_num + 1}")
        print(f"{'=' * 60}")
        
        # Start new round
        context_manager.start_new_round(round_num)
        
        # Simulate agent statements
        agents = ["security-knight", "backend-goblin", "data-warlock"]
        
        for agent_id in agents:
            # Create statement
            statement = DebateStatement(
                agent_id=agent_id,
                position=f"Position from {agent_id} in round {round_num + 1}",
                argument=f"This is a detailed argument from {agent_id} " * 10,
                confidence=0.7 + (round_num * 0.1)
            )
            
            # Add to context (with automatic deduplication)
            context_manager.add_statement(statement)
            
            # Build agent context
            agent_position = AgentPosition(
                stance=statement.position,
                confidence=statement.confidence,
                influence_score=0.8,
                stability_index=0.9
            )
            
            context = context_manager.build_agent_context(
                agent_id=agent_id,
                agent_position=agent_position,
                topic="System Architecture Design"
            )
            
            # Check token budget
            fits, token_count = enforcer.check_budget(context)
            if not fits:
                print(f"  ⚠️  {agent_id}: Context exceeds budget ({token_count} tokens)")
                context = enforcer.compress_if_needed(context)
                _, new_count = enforcer.check_budget(context)
                print(f"  ✓  Compressed to {new_count} tokens")
            else:
                print(f"  ✓  {agent_id}: Context within budget ({token_count} tokens)")
            
            # Track token usage
            monitor.track_agent_tokens(agent_id, token_count)
            context_manager.track_token_usage(agent_id)
        
        # Check if compression should be triggered
        if monitor.should_compress():
            print("\n  ⚠️  Approaching token budget - compression recommended")
        
        # Compress round
        summary = RoundSummary(
            core_positions=[f"Position-{i}" for i in range(3)],
            major_conflicts=["Architecture approach", "Performance vs simplicity"],
            amendments=[f"Amendment-{round_num}"],
            consensus_level=0.6 + (round_num * 0.1)
        )
        
        context_manager.compress_round(summary)
        monitor.end_round()
        
        # Show round statistics
        print(f"\n  Round {round_num + 1} Statistics:")
        ctx_stats = context_manager.estimate_context_tokens(agents[0])
        print(f"    Context tokens: {ctx_stats['total']}")
        print(f"    Token reduction: {ctx_stats['reduction_vs_full']:.1%}")
    
    # Final statistics
    print(f"\n{'=' * 60}")
    print("Final Statistics")
    print(f"{'=' * 60}")
    
    # Context manager stats
    ctx_stats = context_manager.get_token_statistics()
    print(f"\nContext Manager:")
    print(f"  Average tokens per agent: {ctx_stats['average_total']:.0f}")
    print(f"  Max tokens used: {ctx_stats['max_total']}")
    print(f"  Min tokens used: {ctx_stats['min_total']}")
    print(f"  Calls tracked: {ctx_stats['calls_tracked']}")
    
    # Session monitor stats
    monitor_stats = monitor.get_statistics()
    print(f"\nSession Monitor:")
    print(f"  Total tokens: {monitor_stats['total_tokens']}")
    print(f"  Rounds completed: {monitor_stats['rounds_completed']}")
    print(f"  Average per round: {monitor_stats['average_tokens_per_round']:.0f}")
    print(f"  Budget utilization: {monitor_stats['budget_utilization']:.1%}")
    print(f"  Warnings issued: {monitor_stats['warnings_issued']}")
    
    # Budget enforcer stats
    enforcer_stats = enforcer.get_enforcement_stats()
    print(f"\nBudget Enforcer:")
    print(f"  Max tokens per agent: {enforcer_stats['max_tokens_per_agent']}")
    print(f"  Budget enforcements: {enforcer_stats['enforcement_count']}")
    
    # Agent-specific stats
    if "agent_statistics" in monitor_stats:
        print(f"\nPer-Agent Statistics:")
        for agent_id, agent_stats in monitor_stats["agent_statistics"].items():
            print(f"  {agent_id}:")
            print(f"    Total tokens: {agent_stats['total_tokens']}")
            print(f"    Average: {agent_stats['average_tokens']:.0f}")
            print(f"    Calls: {agent_stats['calls']}")
    
    print(f"\n{'=' * 60}")
    print("✓ Debate completed with token optimization")
    print(f"{'=' * 60}\n")


def demonstrate_deduplication():
    """Demonstrate statement deduplication."""
    
    print("\n" + "=" * 60)
    print("Statement Deduplication Example")
    print("=" * 60)
    
    context_manager = ContextManager(
        enable_deduplication=True,
        enable_pruning=False
    )
    
    context_manager.start_new_round(0)
    
    # First statement
    stmt1 = DebateStatement(
        agent_id="agent-1",
        position="Support",
        argument="We need to optimize database queries for performance",
        confidence=0.8
    )
    context_manager.add_statement(stmt1)
    print("  ✓ Added first statement from agent-1")
    
    # Duplicate statement (same agent, same content)
    stmt2 = DebateStatement(
        agent_id="agent-1",
        position="Support",
        argument="We need to optimize database queries for performance",
        confidence=0.9
    )
    context_manager.add_statement(stmt2)
    print("  ✗ Skipped duplicate statement from agent-1")
    
    # Different statement
    stmt3 = DebateStatement(
        agent_id="agent-1",
        position="Support",
        argument="Caching is essential for scalability",
        confidence=0.7
    )
    context_manager.add_statement(stmt3)
    print("  ✓ Added different statement from agent-1")
    
    # Check what was actually added
    if context_manager.immediate_context:
        count = len(context_manager.immediate_context.agent_statements)
        print(f"\n  Result: {count} statements added (1 duplicate skipped)")
    
    print("=" * 60 + "\n")


def demonstrate_pruning():
    """Demonstrate context pruning."""
    
    print("\n" + "=" * 60)
    print("Context Pruning Example")
    print("=" * 60)
    
    from reference.deliberation.core.statement_pruner import ContextPruner
    
    pruner = ContextPruner(min_confidence=0.5, keep_high_influence=True)
    
    statements = [
        DebateStatement(
            agent_id="agent-1",
            position="Support",
            argument="High confidence argument",
            confidence=0.9
        ),
        DebateStatement(
            agent_id="agent-2",
            position="Oppose",
            argument="Low confidence argument",
            confidence=0.3
        ),
        DebateStatement(
            agent_id="agent-3",
            position="Support",
            argument="Medium confidence argument",
            confidence=0.6
        ),
    ]
    
    print(f"\n  Original: {len(statements)} statements")
    
    # Prune without influence scores
    pruned = pruner.prune_statements(statements)
    print(f"  After pruning: {len(pruned)} statements")
    print(f"  Pruned: {len(statements) - len(pruned)} low-confidence statements")
    
    # Show which were kept
    for stmt in pruned:
        print(f"    ✓ Kept {stmt.agent_id} (confidence: {stmt.confidence})")
    
    print("=" * 60 + "\n")


if __name__ == "__main__":
    # Run all examples
    run_token_optimized_debate()
    demonstrate_deduplication()
    demonstrate_pruning()
