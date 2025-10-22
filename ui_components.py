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


def is_list_query(user_question):
    """Detect if the user is asking for a list of items."""
    list_keywords = ['list', 'all', 'every', 'complete', 'full', 'entire', 'chronological', 'chronologically']
    return any(keyword in user_question.lower() for keyword in list_keywords)

def format_match_result(data, query_context=""):
    """Format match results in a user-friendly way."""
    if not data or len(data) == 0:
        return "No results found"
    
    result = data[0]  # Get first result
    
    # Handle different result formats
    if len(result) >= 3:  # winner, loser, score format
        winner, loser = result[0], result[1]
        # Filter out None values and format score
        score_parts = [str(s) for s in result[2:] if s is not None]
        score = " ".join(score_parts) if score_parts else "Score not available"
        
        # Add context if available
        context = f" in {query_context}" if query_context else ""
        return f"{winner} defeated {loser} {score}{context}"
    
    elif len(result) == 2:  # winner, score format
        winner, score = result[0], result[1]
        return f"{winner} won with score {score}"
    
    else:  # Single value
        return str(result[0])

def format_tournament_results(data, tournament_name=""):
    """Format tournament results with proper context."""
    if not data or len(data) == 0:
        return "No results found"
    
    if len(data) == 1:
        result = data[0]
        if len(result) >= 3:  # winner, loser, score format
            winner, loser = result[0], result[1]
            score_parts = [str(s) for s in result[2:] if s is not None]
            score = " ".join(score_parts) if score_parts else "Score not available"
            context = f" in {tournament_name}" if tournament_name else ""
            return f"{winner} defeated {loser} {score}{context}"
        else:
            return str(result[0])
    else:
        # Multiple results - format as list
        results = []
        for i, row in enumerate(data, 1):
            if len(row) >= 3:
                winner, loser = row[0], row[1]
                score_parts = [str(s) for s in row[2:] if s is not None]
                score = " ".join(score_parts) if score_parts else "Score not available"
                results.append(f"{i}. {winner} defeated {loser} {score}")
            else:
                results.append(f"{i}. {row[0]}")
        
        context = f" in {tournament_name}" if tournament_name else ""
        return f"Found {len(data)} result(s){context}:\n\n" + "\n".join(results)

def format_database_result(data, query_type="general"):
    """Format database results based on query type."""
    if not data or len(data) == 0:
        return "No results found"
    
    # Filter out None values from the result
    filtered_data = []
    for row in data:
        filtered_row = [str(item) for item in row if item is not None]
        filtered_data.append(filtered_row)
    
    if len(filtered_data) == 1:
        result = filtered_data[0]
        if len(result) >= 3:  # winner, loser, score format
            winner, loser = result[0], result[1]
            score = " ".join(result[2:]) if len(result) > 2 else "Score not available"
            return f"{winner} defeated {loser} {score}"
        elif len(result) == 2:
            return f"{result[0]} - {result[1]}"
        else:
            return str(result[0])
    else:
        # Multiple results
        results = []
        for i, row in enumerate(filtered_data, 1):
            if len(row) >= 3:
                winner, loser = row[0], row[1]
                score = " ".join(row[2:]) if len(row) > 2 else "Score not available"
                results.append(f"{i}. {winner} defeated {loser} {score}")
            elif len(row) == 2:
                results.append(f"{i}. {row[0]} - {row[1]}")
            else:
                results.append(f"{i}. {row[0]}")
        
        return f"Found {len(filtered_data)} result(s):\n\n" + "\n".join(results)

def detect_query_context(user_question, data):
    """Detect context from user question and data to improve formatting."""
    question_lower = user_question.lower()
    context = {}
    
    # Extract tournament name if mentioned
    tournament_keywords = ['tournament', 'final', 'won', 'champion', 'brisbane', 'auckland', 'doha', 'dubai', 'abu dhabi']
    if any(keyword in question_lower for keyword in tournament_keywords):
        # Try to extract tournament name from question
        words = question_lower.split()
        for i, word in enumerate(words):
            if word in ['won', 'champion', 'final'] and i > 0:
                # Look for tournament name before the keyword
                potential_tournament = words[i-1].title()
                if len(potential_tournament) > 2:  # Avoid short words
                    context['tournament'] = potential_tournament
                    break
        
        # Also check for specific tournament names
        for tournament in ['brisbane', 'auckland', 'doha', 'dubai', 'abu dhabi']:
            if tournament in question_lower:
                context['tournament'] = tournament.title()
                break
    
    # Extract year if mentioned
    import re
    year_match = re.search(r'\b(20\d{2})\b', user_question)
    if year_match:
        context['year'] = year_match.group(1)
    
    # Extract round if mentioned
    round_keywords = ['final', 'semifinal', 'quarterfinal', 'round']
    for keyword in round_keywords:
        if keyword in question_lower:
            context['round'] = keyword.title()
            break
    
    # Extract player names if mentioned
    player_keywords = ['gauff', 'sabalenka', 'pegula', 'swiatek', 'rybakina', 'dimitrov', 'tabilo', 'svitolina']
    for player in player_keywords:
        if player in question_lower:
            context['player'] = player.title()
            break
    
    # Also try to extract player names from the question more broadly
    words = question_lower.split()
    for i, word in enumerate(words):
        if word in ['matches', 'of'] and i > 0:
            potential_player = words[i-1].title()
            if len(potential_player) > 2:  # Avoid short words
                context['player'] = potential_player
                break
    
    # Detect query type for better formatting
    if 'who won' in question_lower:
        context['query_type'] = 'winner'
    elif 'what was the score' in question_lower:
        context['query_type'] = 'score'
    elif 'list' in question_lower or 'all' in question_lower:
        context['query_type'] = 'list'
    elif 'trend' in question_lower or 'performance' in question_lower:
        context['query_type'] = 'analysis'
    
    return context

def format_with_context(data, user_question=""):
    """Format database results with context from user question."""
    if not data or len(data) == 0:
        return "No results found"
    
    context = detect_query_context(user_question, data)
    
    # Filter out None values from the result
    filtered_data = []
    for row in data:
        filtered_row = [str(item) for item in row if item is not None]
        filtered_data.append(filtered_row)
    
    # Check if this is a list query
    is_list_query = any(keyword in user_question.lower() for keyword in ['list', 'all', 'chronologically', 'matches'])
    
    if len(filtered_data) == 1:
        result = filtered_data[0]
        if len(result) >= 3:  # winner, loser, score format
            winner, loser = result[0], result[1]
            score = " ".join(result[2:]) if len(result) > 2 else "Score not available"
            
            # Add context information
            context_parts = []
            if 'tournament' in context:
                context_parts.append(f"in {context['tournament']}")
            if 'year' in context:
                context_parts.append(f"in {context['year']}")
            if 'round' in context:
                context_parts.append(f"in the {context['round']}")
            
            context_str = f" ({' '.join(context_parts)})" if context_parts else ""
            
            # Format based on query type
            if context.get('query_type') == 'winner':
                return f"{winner} won{context_str}"
            elif context.get('query_type') == 'score':
                return f"The score was {score}{context_str}"
            else:
                return f"{winner} defeated {loser} {score}{context_str}"
        elif len(result) == 2:
            return f"{result[0]} - {result[1]}"
        else:
            return str(result[0])
    else:
        # Multiple results - enhanced formatting for list queries
        if is_list_query:
            return format_chronological_list(filtered_data, user_question, context)
        else:
            # Regular multiple results
            results = []
            for i, row in enumerate(filtered_data, 1):
                if len(row) >= 3:
                    winner, loser = row[0], row[1]
                    score = " ".join(row[2:]) if len(row) > 2 else "Score not available"
                    results.append(f"{i}. {winner} defeated {loser} {score}")
                elif len(row) == 2:
                    results.append(f"{i}. {row[0]} - {row[1]}")
                else:
                    results.append(f"{i}. {row[0]}")
            
            return f"Found {len(filtered_data)} result(s):\n\n" + "\n".join(results)

def format_chronological_list(data, user_question, context):
    """Format chronological list of matches with proper date handling."""
    if not data:
        return "No matches found"
    
    # Parse the data with proper date handling
    matches = []
    for row in data:
        if len(row) >= 5:  # Check if we have enough fields
            tournament = row[0]
            
            # Check if we have proper date fields (year, month, day) or just day
            if len(row) >= 8 and isinstance(row[1], int) and isinstance(row[2], int):  # year, month, day format
                year = row[1]
                month = row[2] 
                day = row[3]
                round_name = row[4]
                winner = row[5]
                loser = row[6]
                # Filter out None values from scores
                score_parts = [str(item) for item in row[7:] if item is not None]
                scores = " ".join(score_parts) if score_parts else "Score not available"
                
                # Create proper date for sorting
                date_sort = (year, month, day)
            else:  # Old format with just day
                day = row[1]
                round_name = row[2]
                winner = row[3]
                loser = row[4]
                # Filter out None values from scores
                score_parts = [str(item) for item in row[5:] if item is not None]
                scores = " ".join(score_parts) if score_parts else "Score not available"
                
                # Use tournament order for sorting when we don't have proper dates
                date_sort = (0, 0, day)  # Will be overridden by tournament order
            
            matches.append({
                'tournament': tournament,
                'year': year if 'year' in locals() else 2024,
                'month': month if 'month' in locals() else 1,
                'day': day,
                'round': round_name,
                'winner': winner,
                'loser': loser,
                'score': scores,
                'date_sort': date_sort
            })
    
    # Sort tournaments by typical calendar order (approximate) - only used when we don't have proper dates
    tournament_order = {
        'Auckland': 1, 'Australian Open': 2, 'Doha': 3, 'Dubai': 4, 'Indian Wells': 5, 
        'Miami': 6, 'Stuttgart': 7, 'Madrid': 8, 'Rome': 9, 'Roland Garros': 10,
        'Berlin': 11, 'Wimbledon': 12, 'Paris Olympics': 13, 'Toronto': 14, 'Cincinnati': 15,
        'Us Open': 16, 'Beijing': 17, 'Wuhan': 18, 'Riyadh Finals': 19
    }
    
    # Sort matches by proper date if available, otherwise by tournament order
    if any(match['date_sort'][0] > 0 for match in matches):  # We have proper dates
        matches.sort(key=lambda x: x['date_sort'])
    else:  # Fall back to tournament order
        matches.sort(key=lambda x: (tournament_order.get(x['tournament'], 99), x['day']))
    
    # Format the results with proper chronological order
    result_text = f"Found {len(data)} match(es) for {context.get('player', 'the player')} in 2024:\n\n"
    
    current_tournament = None
    for match in matches:
        if match['tournament'] != current_tournament:
            if current_tournament is not None:
                result_text += "\n"
            result_text += f"**{match['tournament']}:**\n"
            current_tournament = match['tournament']
        
        result_text += f"  • {match['round']}: {match['winner']} defeated {match['loser']} {match['score']}\n"
    
    return result_text

def process_agent_response(response, logger, user_question=""):
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
                                # Multiple columns, single row - use improved formatting
                                final_answer = format_with_context(data, user_question)
                                if logger is not None:
                                    logger.info(f"✅ Formatted multi-column result: {final_answer}")
                            else:
                                # Multiple rows - use improved formatting
                                final_answer = format_with_context(data, user_question)
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
                                    # Multiple columns, single row - use improved formatting
                                    final_answer = format_with_context(data, user_question)
                                else:
                                    # Multiple rows - use improved formatting
                                    final_answer = format_with_context(data, user_question)
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
    # Real-time coverage issue detection (silent background processing)
    coverage_issue = detect_coverage_issue_realtime(user_question)
    # Store coverage issue data silently for backend analysis
    if coverage_issue['is_coverage_issue']:
        st.session_state.latest_coverage_issue = coverage_issue
    
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
            final_answer = process_agent_response(response, logger, user_question)
            
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
        
        # Run comprehensive analysis silently in background
        try:
            report = analyzer.generate_insights_report()
            
            if 'error' not in report:
                # Store analysis results in session state silently
                st.session_state.ml_insights = report
                
                # Check for coverage issues and store silently
                if 'query_analysis' in report and 'coverage_issues' in report['query_analysis']:
                    coverage = report['query_analysis']['coverage_issues']
                    if coverage.get('total_incomplete_queries', 0) > 0:
                        st.session_state.coverage_issues = coverage
                
                # Store performance insights silently
                if 'performance_analysis' in report:
                    st.session_state.performance_insights = report['performance_analysis']
                    
        except Exception as e:
            # Log error silently without showing to user
            pass


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
