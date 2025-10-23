"""
LLM setup and configuration for the tennis AI agent.
Extracted from agent_setup.py for better modularity.
"""

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from sqlalchemy import create_engine
from typing import Dict, Any


class LLMFactory:
    """
    Factory class for creating LLM and database components.
    Centralizes LLM and database setup logic.
    """
    
    @staticmethod
    def create_llm(api_key: str, model: str = "gemini-2.5-flash-lite", temperature: float = 0) -> ChatGoogleGenerativeAI:
        """
        Create a ChatGoogleGenerativeAI instance.
        
        Args:
            api_key: Google API key
            model: Model name (default: gemini-2.5-flash-lite)
            temperature: Temperature setting (default: 0)
            
        Returns:
            Configured ChatGoogleGenerativeAI instance
        """
        return ChatGoogleGenerativeAI(
            model=model,
            google_api_key=api_key,
            temperature=temperature
        )
    
    @staticmethod
    def create_database_connection(db_path: str = "sqlite:///tennis_data_new.db") -> SQLDatabase:
        """
        Create a database connection.
        
        Args:
            db_path: Database connection string
            
        Returns:
            SQLDatabase instance
        """
        db_engine = create_engine(db_path)
        return SQLDatabase(engine=db_engine)
    
    @staticmethod
    def create_toolkit(db: SQLDatabase, llm: ChatGoogleGenerativeAI) -> SQLDatabaseToolkit:
        """
        Create a SQLDatabaseToolkit with the given database and LLM.
        
        Args:
            db: SQLDatabase instance
            llm: ChatGoogleGenerativeAI instance
            
        Returns:
            SQLDatabaseToolkit instance
        """
        return SQLDatabaseToolkit(db=db, llm=llm)
    
    @staticmethod
    def setup_llm_components(config: Dict[str, Any]) -> tuple[ChatGoogleGenerativeAI, SQLDatabase, SQLDatabaseToolkit]:
        """
        Setup all LLM components in one call.
        
        Args:
            config: Configuration dictionary with 'api_key', 'model', 'temperature', 'db_path'
            
        Returns:
            Tuple of (llm, db, toolkit)
        """
        # Create LLM
        llm = LLMFactory.create_llm(
            api_key=config['api_key'],
            model=config.get('model', 'gemini-2.5-flash-lite'),
            temperature=config.get('temperature', 0)
        )
        
        # Create database connection
        db = LLMFactory.create_database_connection(
            db_path=config.get('db_path', 'sqlite:///tennis_data_new.db')
        )
        
        # Create toolkit
        toolkit = LLMFactory.create_toolkit(db, llm)
        
        return llm, db, toolkit
