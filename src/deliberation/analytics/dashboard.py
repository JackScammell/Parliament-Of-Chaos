"""
Markdown dashboard generator for debate analytics.
"""

from typing import Dict, List, Optional
from datetime import datetime, timezone


class DebateDashboard:
    """
    Generate markdown dashboards for debate analytics.
    """
    
    def __init__(self):
        """Initialize dashboard generator."""
        pass
    
    def generate_dashboard(self, debate_results: Dict, 
                          analytics: Optional[Dict] = None) -> str:
        """
        Generate a complete debate analytics dashboard.
        
        Args:
            debate_results: Complete debate results
            analytics: Additional analytics data
            
        Returns:
            Markdown-formatted dashboard
        """
        lines = []
        
        # Header
        lines.append("# Debate Analytics Dashboard")
        lines.append("")
        lines.append(f"**Topic:** {debate_results.get('topic', 'N/A')}")
        lines.append(f"**Generated:** {datetime.now(timezone.utc).isoformat()}Z")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # Outcome section
        lines.extend(self._generate_outcome_section(debate_results.get("outcome", {})))
        lines.append("")
        
        # Metrics section
        metrics = debate_results.get("metrics", {})
        lines.extend(self._generate_metrics_section(metrics))
        lines.append("")
        
        # Analytics section (if provided)
        if analytics:
            lines.extend(self._generate_analytics_section(analytics))
            lines.append("")
        
        # Configuration
        lines.extend(self._generate_config_section(debate_results.get("config", {})))
        
        return "\n".join(lines)
    
    def _generate_outcome_section(self, outcome: Dict) -> List[str]:
        """Generate outcome section."""
        lines = ["## Debate Outcome", ""]
        
        result = outcome.get("result", "unknown")
        approved = outcome.get("approved", False)
        
        emoji = "✅" if approved else "❌"
        lines.append(f"{emoji} **Result:** {result.upper()}")
        lines.append("")
        
        votes = outcome.get("votes", {})
        lines.append("### Voting Results")
        lines.append("")
        lines.append("| Vote Type | Count |")
        lines.append("|-----------|-------|")
        lines.append(f"| Approve   | {votes.get('approve', 0)} |")
        lines.append(f"| Reject    | {votes.get('reject', 0)} |")
        lines.append(f"| Abstain   | {votes.get('abstain', 0)} |")
        lines.append(f"| **Total** | **{votes.get('total', 0)}** |")
        lines.append("")
        
        return lines
    
    def _generate_metrics_section(self, metrics: Dict) -> List[str]:
        """Generate metrics section."""
        lines = ["## Performance Metrics", ""]
        
        lines.append("| Metric | Value |")
        lines.append("|--------|-------|")
        lines.append(f"| Total Tokens | {metrics.get('total_tokens', 0):,} |")
        lines.append(f"| Average Latency | {metrics.get('average_latency', 0):.2f}s |")
        
        convergence = metrics.get('rounds_to_convergence')
        if convergence:
            lines.append(f"| Rounds to Convergence | {convergence} |")
        
        lines.append(f"| Position Entropy | {metrics.get('position_entropy', 0):.3f} |")
        lines.append(f"| Argument Redundancy | {metrics.get('argument_redundancy_score', 0):.2%} |")
        lines.append("")
        
        # Consensus score if available
        consensus = metrics.get('consensus_score')
        if consensus is not None:
            lines.append(f"**Consensus Score:** {consensus:.2%}")
            lines.append("")
        
        return lines
    
    def _generate_analytics_section(self, analytics: Dict) -> List[str]:
        """Generate analytics section."""
        lines = ["## Advanced Analytics", ""]
        
        # Agent influence
        influence = analytics.get("agent_influence_scores", {})
        if influence:
            lines.append("### Agent Influence Scores")
            lines.append("")
            lines.append("| Agent | Influence |")
            lines.append("|-------|-----------|")
            for agent, score in sorted(influence.items(), key=lambda x: x[1], reverse=True):
                lines.append(f"| {agent} | {score:.3f} |")
            lines.append("")
        
        # Novelty scores
        novelty = analytics.get("argument_novelty_scores", [])
        if novelty:
            lines.append("### Argument Novelty by Round")
            lines.append("")
            for i, score in enumerate(novelty):
                bar = "█" * int(score * 20)
                lines.append(f"Round {i+1}: {bar} {score:.2f}")
            lines.append("")
        
        # Time to convergence
        time_conv = analytics.get("time_to_convergence")
        if time_conv:
            lines.append(f"**Time to Convergence:** {time_conv:.1f}s")
            lines.append("")
        
        return lines
    
    def _generate_config_section(self, config: Dict) -> List[str]:
        """Generate configuration section."""
        lines = ["## Configuration", ""]
        
        lines.append("| Setting | Value |")
        lines.append("|---------|-------|")
        lines.append(f"| Mode | {config.get('mode', 'N/A')} |")
        lines.append(f"| Max Rounds | {config.get('max_rounds', 'N/A')} |")
        lines.append(f"| Voting System | {config.get('voting_system', 'N/A')} |")
        lines.append(f"| Convergence Threshold | {config.get('convergence_threshold', 0):.2f} |")
        lines.append("")
        
        return lines
    
    def generate_summary(self, debate_results: Dict) -> str:
        """
        Generate a brief summary of debate results.
        
        Args:
            debate_results: Debate results
            
        Returns:
            Brief markdown summary
        """
        outcome = debate_results.get("outcome", {})
        metrics = debate_results.get("metrics", {})
        
        approved = outcome.get("approved", False)
        emoji = "✅" if approved else "❌"
        
        summary = f"""
{emoji} **{debate_results.get('topic', 'Debate')}**

Result: {outcome.get('result', 'unknown').upper()}
Votes: {outcome.get('votes', {}).get('approve', 0)} approve, {outcome.get('votes', {}).get('reject', 0)} reject
Tokens: {metrics.get('total_tokens', 0):,}
Rounds: {metrics.get('rounds_to_convergence', 'N/A')}
"""
        return summary.strip()
