"""
Planner Agent
PRD Section 13.4 - Task decomposition and mode determination
"""

from typing import List, Dict, Any
from loguru import logger

from app.agents.base import (
    BaseAgent,
    AgentRole,
    AgentContext,
    AgentResponse,
    QueryMode,
)


class PlannerAgent(BaseAgent):
    """
    Plans and decomposes complex queries into executable tasks
    
    Responsibilities:
    - Determine if STANDARD or LIVE mode is needed
    - Decompose complex queries into subtasks
    - Route tasks to appropriate domain agents
    - Manage task dependencies
    """
    
    def __init__(self, llm_client=None):
        super().__init__(AgentRole.PLANNER, llm_client)
    
    async def process(self, context: AgentContext) -> AgentResponse:
        """
        Create execution plan for user query
        """
        
        logger.info(f"Planning for intent: {context.intent}, mode: {context.query_mode.value}")
        
        # Determine if live data is needed
        requires_live = self._requires_live_data(context)
        
        # Decompose into tasks
        tasks = self._decompose_query(context, requires_live)
        
        # Create execution plan
        plan = {
            "query_mode": QueryMode.LIVE if requires_live else QueryMode.STANDARD,
            "requires_live_data": requires_live,
            "tasks": tasks,
            "reasoning": self._explain_plan(context, tasks),
        }
        
        logger.info(f"Generated plan with {len(tasks)} tasks, live_data={requires_live}")
        
        return AgentResponse(
            agent_role=self.role,
            message=f"Created execution plan with {len(tasks)} tasks",
            requires_live_data=requires_live,
            metadata=plan,
        )
    
    def _requires_live_data(self, context: AgentContext) -> bool:
        """
        Determine if query requires live data retrieval
        
        PRD Section 13.4.1 - STANDARD vs LIVE mode decision
        """
        
        # Force LIVE mode if explicitly requested
        if context.query_mode == QueryMode.LIVE:
            return True
        
        # Intents that typically require live data
        live_intents = {
            "pfz_query",
            "weather_query",
            "ocean_query",
            "warning_query",
            "route_query",
        }
        
        if context.intent in live_intents:
            # Check if query is about current/future conditions
            message = context.user_message.lower()
            
            temporal_keywords = [
                "now", "current", "today", "tomorrow",
                "latest", "recent", "forecast", "will be",
            ]
            
            if any(keyword in message for keyword in temporal_keywords):
                return True
        
        # Intents that don't need live data
        knowledge_intents = {
            "greeting",
            "help",
            "status_query",
            "general_query",
        }
        
        if context.intent in knowledge_intents:
            return False
        
        # Default to STANDARD for safety
        return False
    
    def _decompose_query(
        self,
        context: AgentContext,
        requires_live: bool,
    ) -> List[Dict[str, Any]]:
        """
        Decompose query into executable tasks
        """
        
        tasks = []
        
        # Map intent to domain agents
        intent_to_agent = {
            "pfz_query": AgentRole.PFZ_INTELLIGENCE,
            "weather_query": AgentRole.WEATHER_INTELLIGENCE,
            "ocean_query": AgentRole.OCEAN_INTELLIGENCE,
            "warning_query": AgentRole.RISK_ASSESSMENT,
            "route_query": AgentRole.ROUTE_OPTIMIZATION,
            "status_query": AgentRole.CONVERSATION,
            "greeting": AgentRole.CONVERSATION,
            "help": AgentRole.CONVERSATION,
        }
        
        agent_role = intent_to_agent.get(context.intent, AgentRole.CONVERSATION)
        
        # Create primary task
        task = {
            "task_id": "task_1",
            "agent_role": agent_role,
            "intent": context.intent,
            "requires_live_data": requires_live,
            "entities": context.entities,
            "location": context.location,
            "time_range": context.time_range,
        }
        
        tasks.append(task)
        
        # Check if additional supporting tasks are needed
        # For example, a PFZ query might need weather and ocean data
        
        if context.intent == "pfz_query" and requires_live:
            # PFZ needs ocean and weather data
            tasks.append({
                "task_id": "task_2",
                "agent_role": AgentRole.OCEAN_INTELLIGENCE,
                "intent": "ocean_query",
                "requires_live_data": True,
                "entities": context.entities,
                "location": context.location,
            })
            
            tasks.append({
                "task_id": "task_3",
                "agent_role": AgentRole.WEATHER_INTELLIGENCE,
                "intent": "weather_query",
                "requires_live_data": True,
                "entities": context.entities,
                "location": context.location,
            })
        
        elif context.intent == "route_query" and requires_live:
            # Route optimization needs weather and ocean data
            tasks.append({
                "task_id": "task_2",
                "agent_role": AgentRole.WEATHER_INTELLIGENCE,
                "intent": "weather_query",
                "requires_live_data": True,
                "entities": context.entities,
                "location": context.location,
            })
            
            tasks.append({
                "task_id": "task_3",
                "agent_role": AgentRole.RISK_ASSESSMENT,
                "intent": "warning_query",
                "requires_live_data": True,
                "entities": context.entities,
                "location": context.location,
            })
        
        return tasks
    
    def _explain_plan(self, context: AgentContext, tasks: List[Dict]) -> str:
        """
        Generate human-readable explanation of the plan
        """
        
        agent_names = {
            AgentRole.PFZ_INTELLIGENCE: "Fishing Zone Intelligence",
            AgentRole.WEATHER_INTELLIGENCE: "Weather Intelligence",
            AgentRole.OCEAN_INTELLIGENCE: "Ocean Intelligence",
            AgentRole.RISK_ASSESSMENT: "Risk Assessment",
            AgentRole.ROUTE_OPTIMIZATION: "Route Optimization",
            AgentRole.GEOSPATIAL: "Geospatial Analysis",
            AgentRole.CONVERSATION: "Conversation",
        }
        
        task_descriptions = []
        for task in tasks:
            agent_name = agent_names.get(task["agent_role"], "Unknown")
            mode = "live data" if task.get("requires_live_data") else "knowledge"
            task_descriptions.append(f"- {agent_name} ({mode})")
        
        return f"Query will be handled by:\n" + "\n".join(task_descriptions)


class PlannerPrompts:
    """
    LLM prompts for planner agent
    """
    
    MODE_DETERMINATION = """
You are a query planner for a marine intelligence system.

Determine if this query requires LIVE data retrieval or can be answered from STANDARD knowledge.

LIVE mode is needed when:
- User asks about current or future conditions
- Query involves time-sensitive data (weather, ocean state)
- Specific locations or time ranges are mentioned

STANDARD mode is sufficient when:
- General knowledge questions
- Historical or conceptual information
- Greetings or help requests

User query: {user_message}
Intent: {intent}

Respond with ONLY "LIVE" or "STANDARD".
"""
    
    TASK_DECOMPOSITION = """
You are a task planner for a marine intelligence system.

Break down this query into executable tasks for specialized agents:

Available agents:
- PFZ Intelligence: Fishing zone recommendations
- Weather Intelligence: Marine weather data
- Ocean Intelligence: Ocean conditions (SST, currents, salinity)
- Risk Assessment: Warnings and advisories
- Route Optimization: Safe and efficient routing
- Geospatial: Geographic analysis

User query: {user_message}
Intent: {intent}
Entities: {entities}

Create a task list in JSON format:
[
  {{
    "agent": "agent_name",
    "action": "description",
    "requires_live_data": true/false
  }}
]
"""
