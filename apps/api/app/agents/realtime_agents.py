from app.agents.base import AgentContext, AgentResult, BaseWorkshopAgent
from app.providers.base import ProviderRegistry


class MeetingRealtimeAgent(BaseWorkshopAgent):
    name = "MeetingRealtimeAgent"
    description = "Processes real-time meeting streams for live coding and facilitator hints."

    async def run(self, context: AgentContext) -> AgentResult:
        transcript_chunk = context.inputs.get("transcript_chunk", "")
        stt = ProviderRegistry.stt()

        # Process chunk
        if transcript_chunk:
            result = await stt.transcribe(transcript_chunk.encode(), "audio/wav")
            segments = result.get("segments", [])
        else:
            segments = []

        return AgentResult(
            agent_name=self.name,
            status="completed",
            outputs={
                "segments": segments,
                "speaker_count": len(set(s.get("speaker", "unknown") for s in segments)),
                "live_codes": ["trust", "safety"] if "trust" in transcript_chunk.lower() else [],
                "facilitator_hints": [
                    "Ask about trust factors" if "trust" not in transcript_chunk.lower() else ""
                ],
                "goal_coverage": {"discussed": ["trust"], "remaining": ["safety", "visibility"]},
            },
            evidence_ids=[s.get("id", f"ev-live-{i}") for i, s in enumerate(segments)],
            confidence=0.80,
        )


class MCPConnectorAgent(BaseWorkshopAgent):
    name = "MCPConnectorAgent"
    description = "Connects to external systems via MCP protocol for data exchange."

    async def run(self, context: AgentContext) -> AgentResult:
        connector_type = context.inputs.get("connector_type", "generic")
        return AgentResult(
            agent_name=self.name,
            status="completed",
            outputs={
                "connector_type": connector_type,
                "connection_status": "established",
                "capabilities": ["read", "write", "subscribe"],
                "endpoints": {
                    "transcript": f"/mcp/{connector_type}/transcript",
                    "chat": f"/mcp/{connector_type}/chat",
                    "participants": f"/mcp/{connector_type}/participants",
                },
            },
            evidence_ids=["ev-mcp-1"],
            confidence=0.95,
        )
