from app.agents.base import BaseWorkshopAgent


class AgentRegistry:
    def __init__(self) -> None:
        self._agents: dict[str, BaseWorkshopAgent] = {}

    def register(self, agent: BaseWorkshopAgent) -> None:
        self._agents[agent.name] = agent

    def get(self, name: str) -> BaseWorkshopAgent:
        if name not in self._agents:
            raise KeyError(f"Agent '{name}' not found in registry")
        return self._agents[name]

    def list_agents(self) -> list[str]:
        return list(self._agents.keys())

    def has_agent(self, name: str) -> bool:
        return name in self._agents


# Global registry instance
agent_registry = AgentRegistry()
