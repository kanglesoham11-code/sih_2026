"""
Conversation & Language Agent
PRD Section 13.3 - Intent classification, NLU, response synthesis
"""

import json
from typing import Dict, Any
from loguru import logger

from app.agents.base import BaseAgent, AgentRole, AgentContext, AgentResponse


class ConversationAgent(BaseAgent):
    """
    Handles natural language understanding and response generation
    
    Responsibilities:
    - Intent classification
    - Entity extraction (location, time, species, etc.)
    - Response synthesis from domain agent outputs
    - Multi-lingual support (future)
    """
    
    # Intent categories
    INTENTS = {
        "pfz_query": ["fishing zone", "pfz", "catch location", "where to fish"],
        "weather_query": ["weather", "forecast", "wind", "wave", "storm"],
        "ocean_query": ["ocean", "sst", "temperature", "current", "salinity"],
        "warning_query": ["warning", "alert", "advisory", "cyclone", "danger"],
        "route_query": ["route", "navigate", "path", "journey", "travel"],
        "status_query": ["status", "health", "available", "working"],
        "greeting": ["hello", "hi", "hey", "good morning", "namaste"],
        "help": ["help", "how", "what can you do", "capabilities"],
    }
    
    def __init__(self, llm_client=None):
        super().__init__(AgentRole.CONVERSATION, llm_client)
    
    async def process(self, context: AgentContext) -> AgentResponse:
        """
        Process conversational task
        
        Tasks:
        1. Intent classification (if not already done)
        2. Entity extraction (if not already done)
        3. Response synthesis (if domain responses available)
        """
        
        # Check if this is a synthesis task
        if context.metadata.get("domain_responses"):
            return await self._synthesize_response(context)
        
        # Otherwise, perform NLU
        return await self._extract_intent_and_entities(context)
    
    async def _extract_intent_and_entities(self, context: AgentContext) -> AgentResponse:
        """
        Extract intent and entities from user message
        """
        
        message = context.user_message.lower()
        
        # Simple keyword-based intent classification
        # TODO: Replace with LLM-based classification for production
        detected_intent = self._classify_intent(message)
        
        # Extract entities
        entities = self._extract_entities(message)
        
        logger.info(f"Intent: {detected_intent}, Entities: {entities}")
        
        return AgentResponse(
            agent_role=self.role,
            message="Intent and entities extracted",
            metadata={
                "intent": detected_intent,
                "entities": entities,
            },
        )
    
    def _classify_intent(self, message: str) -> str:
        """
        Classify user intent
        
        TODO: Replace with LLM-based classification
        """
        
        # Check each intent category
        for intent, keywords in self.INTENTS.items():
            for keyword in keywords:
                if keyword in message:
                    return intent
        
        # Default to general query
        return "general_query"
    
    def _extract_entities(self, message: str) -> Dict[str, Any]:
        """
        Extract entities from message
        
        TODO: Replace with NER model or LLM-based extraction
        """
        
        entities = {}
        
        # Simple pattern matching (placeholder)
        # Location extraction would use NER
        # Time extraction would use date parsers
        # Species extraction would use domain vocabulary
        
        # Placeholder: Extract numbers as potential coordinates
        import re
        numbers = re.findall(r'\b\d+\.?\d*\b', message)
        if len(numbers) >= 2:
            try:
                lat = float(numbers[0])
                lon = float(numbers[1])
                if -90 <= lat <= 90 and -180 <= lon <= 180:
                    entities["location"] = {"latitude": lat, "longitude": lon}
            except:
                pass
        
        # Check for time-related keywords
        if any(word in message for word in ["today", "tomorrow", "next week"]):
            entities["time_reference"] = "relative"
        
        return entities
    
    async def _synthesize_response(self, context: AgentContext) -> AgentResponse:
        """
        Synthesize final response from domain agent outputs
        """
        
        domain_responses = context.metadata.get("domain_responses", [])
        
        if not domain_responses:
            return AgentResponse(
                agent_role=self.role,
                message="I don't have enough information to answer your question.",
                confidence=0.5,
            )
        
        # TODO: Use LLM to generate natural language response
        # For now, simple concatenation
        
        messages = []
        all_sources = []
        all_data = {}
        
        for response in domain_responses:
            if response.message:
                messages.append(response.message)
            if response.sources_used:
                all_sources.extend(response.sources_used)
            if response.data:
                all_data[response.agent_role.value] = response.data
        
        # Simple synthesis
        synthesized_message = " ".join(messages)
        
        return AgentResponse(
            agent_role=self.role,
            message=synthesized_message,
            data=all_data if all_data else None,
            sources_used=list(set(all_sources)),
            confidence=0.8,
        )


class PromptTemplates:
    """
    LLM prompt templates for conversation agent
    """
    
    INTENT_CLASSIFICATION = """
You are an intent classifier for a marine and fishing intelligence system.

Classify the user's intent into one of these categories:
- pfz_query: Questions about fishing zones or where to fish
- weather_query: Questions about weather, forecasts, wind, waves
- ocean_query: Questions about ocean conditions (temperature, currents, salinity)
- warning_query: Questions about warnings, alerts, advisories
- route_query: Questions about navigation or route planning
- status_query: Questions about system status or data availability
- greeting: Greetings or casual conversation
- help: Requests for help or information about capabilities
- general_query: Other questions

User message: {user_message}

Respond with ONLY the intent category name.
"""
    
    ENTITY_EXTRACTION = """
You are an entity extractor for a marine and fishing intelligence system.

Extract the following entities from the user's message:
- location: Latitude and longitude coordinates
- time_range: Start and end time for queries
- species: Fish species mentioned
- vessel_type: Type of vessel (fishing, cargo, etc.)

User message: {user_message}

Respond with a JSON object containing the extracted entities.
Example: {{"location": {{"latitude": 19.0, "longitude": 72.8}}, "species": ["tuna", "sardine"]}}
"""
    
    RESPONSE_SYNTHESIS = """
You are a friendly marine intelligence assistant.

Synthesize a natural language response based on the following information from specialized agents:

{domain_responses}

User's original question: {user_message}

Provide a clear, helpful response that:
1. Directly answers the user's question
2. Highlights key information from the data
3. Includes relevant recommendations or warnings
4. Is conversational and easy to understand

Response:
"""
