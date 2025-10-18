import streamlit as st
from sqlalchemy import create_engine

# Modern imports for the LangChain Agent framework
from langsmith import Client
from langchain.agents import create_agent
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain_perplexity.chat_models import ChatPerplexity

# --- Page Configuration ---
st.set_page_config(page_title="AskTennis AI", layout="wide")
st.title("🎾 AskTennis: The Advanced AI Engine")
st.markdown("#### Powered by Perplexity & LangChain")
st.markdown("This app uses a Large Language Model to answer natural language questions about tennis data.")

# --- Database and LLM Setup (Cached for performance) ---

@st.cache_resource
def setup_agent():
    """
    Sets up the database, LLM, and the ReAct agent.
    This is cached to avoid re-initializing on every interaction.
    """
    print("--- Initializing AI Agent ---")
    
    # Check for the API key in Streamlit's secrets
    try:
        pplx_api_key = st.secrets["PPLX_API_KEY"]
    except (KeyError, FileNotFoundError):
        st.error("Perplexity API key not found! Please create a `.streamlit/secrets.toml` file and add your key.")
        st.stop()

    # Setup database connection
    db_engine = create_engine("sqlite:///tennis_data.db")
    db = SQLDatabase(engine=db_engine)

    # Instantiate the Perplexity Chat Model with the ideal reasoning model
    llm = ChatPerplexity(pplx_api_key=pplx_api_key, model="sonar-reasoning-pro", temperature=0)

    # --- Build the Agent using the Modern LangChain Framework ---

    # 1. Create the SQL Toolkit: This contains tools the agent can use (e.g., query SQL).
    print("Creating SQL toolkit...")
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    tools = toolkit.get_tools()
    print(f"Created {len(tools)} tools: {[tool.name for tool in tools]}")

    # 2. Get the ReAct Agent Prompt: A battle-tested prompt for reasoning.
    try:
        client = Client()
        prompt = client.pull_prompt("hwchase17/react-chat")
    except Exception as e:
        print(f"Warning: Could not pull prompt from langsmith: {e}")
        print("Using default ReAct prompt...")
        # Fallback to a basic system prompt
        prompt = """You are a helpful assistant that can answer questions about tennis data using SQL queries.

You have access to these SQL tools:
- sql_db_list_tables: List all tables in the database
- sql_db_schema: Get schema and sample data for specific tables  
- sql_db_query: Execute SQL queries
- sql_db_query_checker: Check if a SQL query is valid before executing

When answering questions about tennis data:
1. First, explore the database structure to understand what data is available
2. Then formulate appropriate SQL queries to answer the user's question
3. Execute the queries and provide clear, informative answers
4. If you're unsure about the data structure, use the schema tools to investigate

Always be helpful and provide detailed explanations of your findings."""

    # 3. Create a simple function-based agent that works with Perplexity
    print("Creating simple agent...")
    
    def process_question_with_tools(question):
        """Process a question using SQL tools in a ReAct-like manner"""
        conversation_history = []
        max_iterations = 5
        iteration = 0
        
        while iteration < max_iterations:
            # Create context from conversation history
            context = ""
            if conversation_history:
                context = "\\n\\nPrevious steps:\\n" + "\\n".join(conversation_history)
            
            # Create prompt for the LLM
            available_tools = [tool.name for tool in tools]
            prompt_text = f"""{prompt}

Current question: {question}
{context}

Available tools: {available_tools}

Think step by step. If you need to use a tool, respond with:
TOOL: tool_name
INPUT: tool_input

If you have enough information to answer the question, respond with:
FINAL_ANSWER: your answer

What should you do next?"""
            
            # Get LLM response
            response = llm.invoke(prompt_text)
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            # Check if it's a tool call
            if "TOOL:" in response_text:
                try:
                    # Extract tool name and input
                    import re
                    tool_match = re.search(r"TOOL:\\s*(\\w+)\\s*\\nINPUT:\\s*(.+)", response_text, re.DOTALL)
                    if tool_match:
                        tool_name = tool_match.group(1).strip()
                        tool_input = tool_match.group(2).strip()
                        
                        # Find and execute the tool
                        tool_lookup = {tool.name: tool for tool in tools}
                        if tool_name in tool_lookup:
                            tool = tool_lookup[tool_name]
                            result = tool.invoke(tool_input)
                            conversation_history.append(f"Used {tool_name} with input: {tool_input}")
                            conversation_history.append(f"Result: {result}")
                        else:
                            conversation_history.append(f"Unknown tool: {tool_name}. Available tools: {list(tool_lookup.keys())}")
                    else:
                        conversation_history.append(f"Could not parse tool call: {response_text}")
                except Exception as e:
                    conversation_history.append(f"Error using tool: {str(e)}")
            elif "FINAL_ANSWER:" in response_text:
                # Extract final answer
                import re
                answer_match = re.search(r"FINAL_ANSWER:\\s*(.+)", response_text, re.DOTALL)
                if answer_match:
                    return answer_match.group(1).strip()
                else:
                    return response_text
            else:
                conversation_history.append(f"LLM response: {response_text}")
            
            iteration += 1
        
        return "I was unable to find a complete answer to your question."
    
    # 4. The agent is ready to use directly
    agent_executor = process_question_with_tools
    
    print("--- AI Agent Initialized Successfully ---")
    return agent_executor

# Initialize the agent
try:
    agent_executor = setup_agent()
except Exception as e:
    st.error(f"Failed to initialize the AI agent: {e}")
    st.stop()

# --- Main App UI & Logic ---

st.markdown("##### Example Questions:")
st.markdown("""
- *How many matches did Roger Federer win in 2006?*
- *Who won the most matches on clay in 2010?*
- *Compare the number of wins for Iga Swiatek and Aryna Sabalenka in 2023.*
- *What was the score of the Wimbledon final in 2008?*
""")

user_question = st.text_input(
    "Ask your tennis question:",
    placeholder="e.g., 'How many tournaments did Serena Williams win on hard court?'"
)

if user_question:
    with st.spinner("The AI is analyzing your question and querying the database..."):
        try:
            # Invoke the agent with the user's question
            answer = agent_executor(user_question)
            
            st.success("Here's what I found:")
            st.markdown(answer)

        except Exception as e:
            st.error(f"An error occurred while processing your request: {e}")
            st.error(f"Error type: {type(e).__name__}")
            import traceback
            st.error(f"Full traceback: {traceback.format_exc()}")

