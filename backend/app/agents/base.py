"""
Base Agent Infrastructure
PRD Section 13 - Multi-Agent System

Agent types:
- Conversation & Language Agent (intent classification, NLU)
- Planner Agent (task decomposition, STANDARD vs LIVE mode)
- Domain Agents (PFZ, Ocean, Weather, Geospatial, Risk, Route)
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

from loguru import logger


class QueryMode(str, Enum):
    """Query execution mode"""
    STANDARD = "standard"  # Knowledge-based, no live data
    LIVE = "live"  # Real-time data retrieval


class AgentRole(str, Enum):
    """Agent role classification"""
    CONVERSATION = "conversation"
    PLANNER = "planner"
    PFZ_INTELLIGENCE = "pfz_intelligence"
    OCEAN_INTELLIGENCE = "ocean_intelligence"
    WEATHER_INTELLIGENCE = "weather_intelligence"
    GEOSPATIAL = "geospatial"
    RISK_ASSESSMENT = "risk_assessment"
    ROUTE_OPTIMIZATION = "route_optimization"


@dataclass
class AgentContext:
    """Shared context between agents"""
    session_id: str
    user_message: str
    query_mode: QueryMode
    intent: Optional[str] = None
    entities: Dict[str, Any] = None
    location: Optional[Dict[str, float]] = None
    time_range: Optional[Dict[str, datetime]] = None
    conversation_history: List[Dict[str, str]] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.entities is None:
            self.entities = {}
        if self.conversation_history is None:
            self.conversation_history = []
        if self.metadata is None:
            self.metadata = {}


@dataclass
class AgentResponse:
    """Agent response structure"""
    agent_role: AgentRole
    message: str
    data: Optional[Any] = None
    sources_used: List[str] = None
    confidence: float = 1.0
    requires_live_data: bool = False
    recommendations: List[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.sources_used is None:
            self.sources_used = []
        if self.recommendations is None:
            self.recommendations = []
        if self.metadata is None:
            self.metadata = {}


class BaseAgent(ABC):
    """
    Base class for all agents
    PRD Section 13.1
    """
    
    def __init__(self, role: AgentRole, llm_client=None):
        self.role = role
        self.llm_client = llm_client
        logger.info(f"Initialized agent: {role.value}")
    
    @abstractmethod
    async def process(self, context: AgentContext) -> AgentResponse:
        """
        Process agent task
        
        Args:
            context: Shared context with user query and extracted info
        
        Returns:
            AgentResponse with results
        """
        pass
    
    async def _call_llm(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
    ) -> str:
        """
        Call LLM with prompts
        
        Args:
            system_prompt: System/role prompt
            user_prompt: User query
            temperature: Sampling temperature
        
        Returns:
            LLM response text
        """
        
        if not self.llm_client:
            raise RuntimeError("LLM client not configured")
        
        # TODO: Implement actual LLM call based on provider
        # This is a placeholder structure
        
        logger.debug(f"Calling LLM for {self.role.value}")
        
        # Placeholder - replace with actual OpenAI/Anthropic/etc. call
        response = f"[LLM Response for {self.role.value}]"
        
        return response
    
    def _format_response(
        self,
        message: str,
        data: Any = None,
        sources: List[str] = None,
    ) -> AgentResponse:
        """Helper to format agent response"""
        return AgentResponse(
            agent_role=self.role,
            message=message,
            data=data,
            sources_used=sources or [],
        )


class AgentOrchestrator:
    """
    Orchestrates multi-agent workflow
    PRD Section 13.2 - Agent coordination
    """
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        self.agents: Dict[AgentRole, BaseAgent] = {}
    
    def register_agent(self, agent: BaseAgent):
        """Register an agent"""
        self.agents[agent.role] = agent
        logger.info(f"Registered agent: {agent.role.value}")
    
    async def process_query(
        self,
        user_message: str,
        session_id: str,
        query_mode: QueryMode = QueryMode.STANDARD,
    ) -> AgentResponse:
        """
        Process user query through multi-agent system
        
        Workflow:
        1. Conversation Agent: Intent classification & entity extraction
        2. Planner Agent: Task decomposition & mode determination
        3. Domain Agents: Execute specialized tasks
        4. Conversation Agent: Synthesize final response
        
        Args:
            user_message: User input
            session_id: Session identifier
            query_mode: STANDARD or LIVE mode
        
        Returns:
            Final synthesized response
        """
        
        logger.info(f"Processing query in {query_mode.value} mode: {user_message[:50]}...")
        
        # Initialize context
        context = AgentContext(
            session_id=session_id,
            user_message=user_message,
            query_mode=query_mode,
        )
        
        try:
            # Step 1: Conversation Agent - Intent & entity extraction
            conversation_agent = self.agents.get(AgentRole.CONVERSATION)
            if conversation_agent:
                intent_response = await conversation_agent.process(context)
                context.intent = intent_response.metadata.get("intent")
                context.entities = intent_response.metadata.get("entities", {})
                logger.info(f"Detected intent: {context.intent}")
            
            # Step 2: Planner Agent - Task decomposition
            planner_agent = self.agents.get(AgentRole.PLANNER)
            if planner_agent:
                plan_response = await planner_agent.process(context)
                tasks = plan_response.metadata.get("tasks", [])
                logger.info(f"Generated {len(tasks)} tasks")
                
                # Execute tasks through domain agents
                responses = []
                for task in tasks:
                    agent_role = task.get("agent_role")
                    domain_agent = self.agents.get(agent_role)
                    
                    if domain_agent:
                        # Update context with task-specific info
                        task_context = AgentContext(
                            session_id=context.session_id,
                            user_message=context.user_message,
                            query_mode=context.query_mode,
                            intent=task.get("intent"),
                            entities=task.get("entities", context.entities),
                            location=task.get("location", context.location),
                            time_range=task.get("time_range", context.time_range),
                        )
                        
                        response = await domain_agent.process(task_context)
                        responses.append(response)
                
                # Step 3: Synthesize responses
                if conversation_agent:
                    # Final synthesis by conversation agent
                    context.metadata["domain_responses"] = responses
                    final_response = await conversation_agent.process(context)
                    return final_response
                
                # Fallback: Return first response
                return responses[0] if responses else plan_response
            
            # No planner - direct execution
            return AgentResponse(
                agent_role=AgentRole.CONVERSATION,
                message="Agent system is initializing. Please try again.",
                confidence=0.5,
            )
        
        except Exception as e:
            logger.error(f"Agent orchestration error: {e}")
            return AgentResponse(
                agent_role=AgentRole.CONVERSATION,
                message=f"I encountered an error processing your request: {str(e)}",
                confidence=0.0,
            )
