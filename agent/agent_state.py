"""
Agent state definitions for LangGraph.
Contains only the essential AgentState TypedDict.
"""

from typing import TypedDict, Annotated, List
from langchain_core.messages import BaseMessage
import operator


class AgentState(TypedDict):
    """
    Defines the state structure for the LangGraph agent.
    Contains messages that accumulate during the conversation.
    """
    messages: Annotated[List[BaseMessage], operator.add]
