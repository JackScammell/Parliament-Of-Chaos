"""
Team-based debate coordination.
"""

from typing import Dict, List
from ..models.schemas import DebateTeamsConfig, TeamRole


class TeamCoordinator:
    """
    Coordinate team-based debates with structured roles.
    """
    
    def __init__(self, config: DebateTeamsConfig):
        """
        Initialize team coordinator.
        
        Args:
            config: Team configuration
        """
        self.config = config
        self.teams = {team.role: team for team in config.teams}
    
    def assign_agents_to_roles(self, agents: List[str], 
                               auto_balance: bool = True) -> Dict[str, List[str]]:
        """
        Assign agents to team roles.
        
        Args:
            agents: List of agent IDs
            auto_balance: Automatically balance team sizes
            
        Returns:
            Dictionary mapping roles to agent lists
        """
        if auto_balance:
            return self._auto_assign(agents)
        else:
            return {team.role: team.agents for team in self.config.teams}
    
    def _auto_assign(self, agents: List[str]) -> Dict[str, List[str]]:
        """
        Automatically assign agents to balanced teams.
        
        Args:
            agents: List of agent IDs
            
        Returns:
            Balanced team assignments
        """
        # Default role distribution
        role_order = ["advocate", "opponent", "moderator", "synthesis"]
        assignments = {role: [] for role in role_order}
        
        # Distribute agents evenly
        for i, agent in enumerate(agents):
            role = role_order[i % len(role_order)]
            assignments[role].append(agent)
        
        return assignments
    
    def get_execution_order(self) -> List[str]:
        """
        Get the order in which teams should execute.
        
        Returns:
            Ordered list of team roles
        """
        if self.config.team_coordination_mode == "sequential":
            # Execute in priority order
            return sorted(
                [team.role for team in self.config.teams],
                key=lambda r: self.teams[r].priority
            )
        else:
            # Parallel or hybrid - all at once
            return [team.role for team in self.config.teams]
    
    def should_execute_parallel(self) -> bool:
        """
        Check if teams should execute in parallel.
        
        Returns:
            True if parallel execution
        """
        return self.config.team_coordination_mode in ["parallel", "hybrid"]
    
    def get_team_summary(self) -> Dict:
        """
        Get summary of team configuration.
        
        Returns:
            Team summary
        """
        return {
            "enabled": self.config.enable_teams,
            "mode": self.config.team_coordination_mode,
            "teams": {
                team.role: {
                    "description": team.description,
                    "agent_count": len(team.agents),
                    "priority": team.priority
                }
                for team in self.config.teams
            }
        }


def create_default_debate_teams(agents: List[str]) -> DebateTeamsConfig:
    """
    Create default debate team configuration.
    
    Args:
        agents: List of agent IDs
        
    Returns:
        Default team configuration
    """
    # Split agents into teams
    n_agents = len(agents)
    n_per_team = max(1, n_agents // 4)
    
    teams = [
        TeamRole(
            role="advocate",
            description="Present pro arguments and supporting evidence",
            agents=agents[0:n_per_team],
            priority=1
        ),
        TeamRole(
            role="opponent",
            description="Present counterarguments and challenges",
            agents=agents[n_per_team:2*n_per_team],
            priority=2
        ),
        TeamRole(
            role="moderator",
            description="Enforce rules and maintain debate structure",
            agents=agents[2*n_per_team:3*n_per_team] if 2*n_per_team < n_agents else [],
            priority=3
        ),
        TeamRole(
            role="synthesis",
            description="Synthesize arguments and find common ground",
            agents=agents[3*n_per_team:] if 3*n_per_team < n_agents else [],
            priority=4
        )
    ]
    
    return DebateTeamsConfig(
        enable_teams=True,
        teams=teams,
        team_coordination_mode="parallel"
    )
