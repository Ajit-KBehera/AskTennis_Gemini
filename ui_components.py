"""
UI components and main app logic for AskTennis AI application.
Handles Streamlit interface, user interactions, and response processing.
"""

import streamlit as st
from datetime import datetime
from langchain_core.messages import HumanMessage, AIMessage
from logging_config import log_user_query, log_llm_interaction, log_final_response, log_error
from ml_analytics import TennisLogAnalyzer


def display_example_questions():
    """Display example questions for users."""
    st.markdown("##### Example Questions:")
    st.markdown("""
    - *How many matches did Roger Federer win in 2006?*
    - *Who won the most matches on clay in 2010?*
    - *What was the score of the Wimbledon final in 2008?*
    """)


def get_user_input():
    """Get user input question."""
    return st.text_input(
        "Ask your tennis question:",
        placeholder="e.g., 'How many tournaments did Serena Williams win on hard court?'"
    )


def process_agent_response(response, logger):
    """Process and format the agent's response."""
    # The final answer is in the content of the last AIMessage.
    # Parse Gemini's structured output format
    last_message = response["messages"][-1]
    logger.info(f"Last message type: {type(last_message)}")
    logger.info(f"Last message content: {last_message.content}")
    logger.info(f"Last message content type: {type(last_message.content)}")
    
    if isinstance(last_message.content, list) and last_message.content:
        # For Gemini, content is a list of dicts. We want the text from the first part.
        final_answer = last_message.content[0].get("text", "")
        if logger is not None:
            logger.info(f"Extracted from list content: {final_answer}")
    else:
        # Fallback for standard string content
        final_answer = last_message.content
        if logger is not None:
            logger.info(f"Using string content: {final_answer}")
    
    # If no final answer found, try to extract from tool messages and format properly
    if not final_answer or not final_answer.strip():
        if logger is not None:
            logger.info("No clear final answer found, attempting to parse database results...")
        # First, try to parse database results from AI messages
        for i, message in enumerate(reversed(response["messages"])):
            if isinstance(message, AIMessage) and message.content:
                if logger is not None:
                    logger.info(f"Checking AI message {i}: {message.content}")
                try:
                    import ast
                    content_str = str(message.content)
                    if logger is not None:
                        logger.info(f"Content string: {content_str}")
                    if content_str.startswith('[') and content_str.endswith(']'):
                        if logger is not None:
                            logger.info("Found list-like content, attempting to parse...")
                        data = ast.literal_eval(content_str)
                        if logger is not None:
                            logger.info(f"Parsed data: {data}")
                        if data and len(data) > 0:
                            # Format the result properly based on the query type
                            if len(data) == 1 and len(data[0]) == 1:
                                # Single result (like winner name)
                                result = data[0][0]
                                final_answer = f"The answer is: {result}"
                                if logger is not None:
                                    logger.info(f"✅ Formatted single result: {final_answer}")
                            elif len(data) == 1 and len(data[0]) > 1:
                                # Multiple columns, single row
                                final_answer = f"Result: {', '.join(map(str, data[0]))}"
                                if logger is not None:
                                    logger.info(f"✅ Formatted multi-column result: {final_answer}")
                            else:
                                # Multiple rows
                                final_answer = f"Found {len(data)} result(s): {', '.join([str(row[0]) for row in data[:5]])}"
                                if logger is not None:
                                    logger.info(f"✅ Formatted multi-row result: {final_answer}")
                            break
                except Exception as e:
                    if logger is not None:
                        logger.info(f"Failed to parse message {i}: {e}")
                    continue
        
        # If still no answer, try tool messages
        if not final_answer or not final_answer.strip():
            for message in reversed(response["messages"]):
                if hasattr(message, 'type') and message.type == 'tool' and 'sql_db_query' in str(message.name):
                    try:
                        import ast
                        if message.content.startswith('[') and message.content.endswith(']'):
                            data = ast.literal_eval(message.content)
                            if data and len(data) > 0:
                                # Format the result properly based on the query type
                                if len(data) == 1 and len(data[0]) == 1:
                                    # Single result (like winner name)
                                    result = data[0][0]
                                    final_answer = f"The answer is: {result}"
                                elif len(data) == 1 and len(data[0]) > 1:
                                    # Multiple columns, single row
                                    final_answer = f"Result: {', '.join(map(str, data[0]))}"
                                else:
                                    # Multiple rows
                                    final_answer = f"Found {len(data)} result(s): {', '.join([str(row[0]) for row in data[:5]])}"
                                break
                    except:
                        continue
    
    return final_answer


def detect_coverage_issue_realtime(query: str) -> dict:
    """Detect potential coverage issues in real-time."""
    query_lower = query.lower()
    
    # Combined tournaments that have both ATP and WTA
    combined_tournaments = [
        'rome', 'basel', 'madrid', 'indian wells', 'miami', 'monte carlo', 
        'hamburg', 'stuttgart', 'eastbourne', 'newport', 'atlanta', 
        'washington', 'toronto', 'montreal', 'cincinnati', 'winston salem', 
        'stockholm', 'antwerp', 'vienna', 'paris'
    ]
    
    is_tournament_query = any(tournament in query_lower for tournament in combined_tournaments)
    has_gender_spec = any(gender_word in query_lower for gender_word in ['men', 'women', 'male', 'female', 'atp', 'wta'])
    
    if is_tournament_query and not has_gender_spec:
        tournament_detected = next((t for t in combined_tournaments if t in query_lower), 'unknown')
        return {
            'is_coverage_issue': True,
            'tournament': tournament_detected,
            'query': query,
            'severity': 'high' if tournament_detected in ['rome', 'basel', 'madrid'] else 'medium'
        }
    
    return {'is_coverage_issue': False}


def handle_user_query(user_question, agent_graph, logger):
    """Handle user query processing and response display."""
    # Real-time coverage issue detection
    coverage_issue = detect_coverage_issue_realtime(user_question)
    if coverage_issue['is_coverage_issue']:
        st.warning(f"🤖 ML Alert: Generic tournament query detected for {coverage_issue['tournament'].title()}. "
                  f"Consider specifying ATP/WTA for complete results.")
    
    # Log the user query
    log_user_query(user_question, "user_session")
    
    with st.spinner("The AI is analyzing your question and querying the database..."):
        try:
            start_time = datetime.now()
            
            # The config dictionary ensures each user gets their own conversation history.
            config = {"configurable": {"thread_id": "user_session"}}
            
            # Log the initial LLM interaction
            log_llm_interaction([HumanMessage(content=user_question)], "INITIAL_USER_QUERY")
            
            # --- REFINEMENT 3: The stateful graph only needs the new human message. ---
            # It loads the history from memory automatically via the checkpointer.
            response = agent_graph.invoke(
                {"messages": [HumanMessage(content=user_question)]},
                config=config
            )
            
            # Log the complete conversation flow
            log_llm_interaction(response["messages"], "COMPLETE_CONVERSATION_FLOW")
            
            # Process the response
            final_answer = process_agent_response(response, logger)
            
            # Calculate total processing time
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            if final_answer and final_answer.strip():
                # Log successful response
                log_final_response(final_answer, processing_time)
                st.success("Here's what I found:")
                st.markdown(final_answer)
            else:
                # Log warning case
                log_final_response("No clear response generated", processing_time)
                st.warning("I processed your request but couldn't generate a clear response. Please check the conversation flow below for details.")
                
                # Check if this might be a misspelling issue
                if "no results" in str(final_answer).lower() or "not found" in str(final_answer).lower():
                    st.info("💡 **Tip**: If you didn't find what you're looking for, try checking the spelling of player or tournament names. The system is case-sensitive and requires exact matches.")

        except Exception as e:
            # Log error
            log_error(e, f"Processing user query: {user_question}")
            st.error(f"An error occurred while processing your request: {e}")


def run_session_ml_analysis():
    """Run ML analysis at the start of each session."""
    if 'ml_analysis_done' not in st.session_state:
        st.session_state.ml_analysis_done = True
        
        # Initialize ML analyzer
        analyzer = TennisLogAnalyzer()
        
        # Run comprehensive analysis
        with st.spinner("🤖 Running ML analysis for session optimization..."):
            try:
                report = analyzer.generate_insights_report()
                
                if 'error' not in report:
                    # Store analysis results in session state
                    st.session_state.ml_insights = report
                    
                    # Check for coverage issues
                    if 'query_analysis' in report and 'coverage_issues' in report['query_analysis']:
                        coverage = report['query_analysis']['coverage_issues']
                        if coverage.get('total_incomplete_queries', 0) > 0:
                            st.session_state.coverage_issues = coverage
                            
                            # Display coverage issues as info
                            st.info(f"🤖 ML Analysis: Found {coverage['total_incomplete_queries']} potential coverage issues. "
                                   f"Consider specifying ATP/WTA for tournament queries like Rome, Basel, etc.")
                    
                    # Store performance insights
                    if 'performance_analysis' in report:
                        st.session_state.performance_insights = report['performance_analysis']
                        
            except Exception as e:
                st.warning(f"ML analysis encountered an issue: {e}")


def run_main_app(agent_graph, logger):
    """Run the main application logic."""
    # Run ML analysis at session start
    run_session_ml_analysis()
    
    # Display example questions
    display_example_questions()
    
    # Get user input
    user_question = get_user_input()
    
    # Handle user query if provided
    if user_question:
        handle_user_query(user_question, agent_graph, logger)
