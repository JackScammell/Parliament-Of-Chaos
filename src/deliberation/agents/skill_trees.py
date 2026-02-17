"""
Agent skill trees and hierarchical expertise system.
"""

import json
from typing import Dict, List, Optional
from pathlib import Path
from ..models.schemas import AgentSkillTree


class SkillTreeManager:
    """
    Manage hierarchical skill trees for specialist agents.
    """
    
    def __init__(self, skills_path: str = ".parliament-skills"):
        """
        Initialize skill tree manager.
        
        Args:
            skills_path: Path to skill tree storage
        """
        self.skills_path = Path(skills_path)
        self.skills_path.mkdir(parents=True, exist_ok=True)
        self.skill_trees: Dict[str, AgentSkillTree] = {}
        self._load_default_skill_trees()
    
    def _load_default_skill_trees(self):
        """Load default skill trees for built-in agents."""
        # UI/UX Guru skill tree
        self.register_skill_tree(AgentSkillTree(
            agent_id="ui-ux-guru",
            primary_domain="UI/UX Design",
            skills={
                "Accessibility": ["WCAG Compliance", "Screen Reader Support", "Keyboard Navigation"],
                "Color Psychology": ["Color Theory", "Contrast Ratios", "Brand Identity"],
                "Usability Testing": ["A/B Testing", "User Feedback", "Heuristic Evaluation"],
                "Interaction Design": ["Micro-interactions", "Animations", "Gestures"],
                "Responsive Design": ["Mobile-First", "Adaptive Layouts", "Breakpoints"]
            },
            skill_level={
                "Accessibility": 5,
                "Color Psychology": 4,
                "Usability Testing": 5,
                "Interaction Design": 4,
                "Responsive Design": 5
            }
        ))
        
        # Security Knight skill tree
        self.register_skill_tree(AgentSkillTree(
            agent_id="security-knight",
            primary_domain="Security",
            skills={
                "Authentication": ["OAuth2", "JWT", "Multi-Factor Auth", "Session Management"],
                "Encryption": ["TLS/SSL", "Data at Rest", "Key Management"],
                "Vulnerabilities": ["SQL Injection", "XSS", "CSRF", "Code Injection"],
                "Compliance": ["GDPR", "HIPAA", "SOC2", "PCI-DSS"],
                "Threat Modeling": ["STRIDE", "Attack Trees", "Risk Assessment"]
            },
            skill_level={
                "Authentication": 5,
                "Encryption": 5,
                "Vulnerabilities": 5,
                "Compliance": 4,
                "Threat Modeling": 4
            }
        ))
        
        # System Architect skill tree
        self.register_skill_tree(AgentSkillTree(
            agent_id="system-architect",
            primary_domain="Architecture",
            skills={
                "Design Patterns": ["MVC", "Microservices", "Event-Driven", "CQRS"],
                "Scalability": ["Load Balancing", "Caching", "Horizontal Scaling"],
                "Integration": ["API Design", "Message Queues", "Service Mesh"],
                "Trade-offs": ["CAP Theorem", "Performance vs Consistency", "Cost Analysis"],
                "Documentation": ["Architecture Diagrams", "ADRs", "System Context"]
            },
            skill_level={
                "Design Patterns": 5,
                "Scalability": 5,
                "Integration": 4,
                "Trade-offs": 5,
                "Documentation": 4
            }
        ))
    
    def register_skill_tree(self, skill_tree: AgentSkillTree) -> bool:
        """
        Register a skill tree for an agent.
        
        Args:
            skill_tree: Agent skill tree
            
        Returns:
            True if registered successfully
        """
        self.skill_trees[skill_tree.agent_id] = skill_tree
        
        # Save to file
        tree_path = self.skills_path / f"{skill_tree.agent_id}.json"
        with open(tree_path, 'w') as f:
            json.dump(skill_tree.model_dump(), f, indent=2)
        
        return True
    
    def get_skill_tree(self, agent_id: str) -> Optional[AgentSkillTree]:
        """
        Get skill tree for an agent.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            Skill tree or None
        """
        return self.skill_trees.get(agent_id)
    
    def get_skills_for_domain(self, agent_id: str, domain: str) -> List[str]:
        """
        Get skills for a specific domain.
        
        Args:
            agent_id: Agent identifier
            domain: Domain name
            
        Returns:
            List of skills in domain
        """
        tree = self.get_skill_tree(agent_id)
        if not tree:
            return []
        
        return tree.skills.get(domain, [])
    
    def get_agent_expertise_summary(self, agent_id: str) -> Dict:
        """
        Get summary of agent expertise.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            Expertise summary
        """
        tree = self.get_skill_tree(agent_id)
        if not tree:
            return {}
        
        return {
            "agent_id": agent_id,
            "primary_domain": tree.primary_domain,
            "skill_domains": list(tree.skills.keys()),
            "total_skills": sum(len(skills) for skills in tree.skills.values()),
            "average_skill_level": sum(tree.skill_level.values()) / len(tree.skill_level) if tree.skill_level else 0
        }
    
    def match_agent_to_task(self, task_keywords: List[str]) -> List[str]:
        """
        Find agents matching task requirements.
        
        Args:
            task_keywords: Keywords describing task
            
        Returns:
            List of matching agent IDs
        """
        matches = []
        
        for agent_id, tree in self.skill_trees.items():
            # Check if any keyword matches domains or skills
            for domain, skills in tree.skills.items():
                domain_match = any(kw.lower() in domain.lower() for kw in task_keywords)
                skill_match = any(
                    any(kw.lower() in skill.lower() for kw in task_keywords)
                    for skill in skills
                )
                
                if domain_match or skill_match:
                    matches.append(agent_id)
                    break
        
        return matches
