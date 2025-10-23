"""
Tennis terminology mapping tools for natural language processing.
Extracted from agent_setup.py for better modularity.
"""

from langchain_core.tools import tool
from typing import Dict, Any, List
import pandas as pd


# --- Centralized Mapping Dictionaries ---

ROUND_MAPPINGS = {
    # Finals
    "final": "F", "finals": "F", "championship": "F", "champion": "F", "winner": "F",
    
    # Semi-Finals
    "semi-final": "SF", "semi finals": "SF", "semifinal": "SF", "semifinals": "SF",
    "semi": "SF", "last four": "SF", "last 4": "SF",
    
    # Quarter-Finals
    "quarter-final": "QF", "quarter finals": "QF", "quarterfinal": "QF", "quarterfinals": "QF",
    "quarter": "QF", "quarters": "QF", "last eight": "QF", "last 8": "QF",
    
    # Round of 16
    "round of 16": "R16", "round 16": "R16", "last 16": "R16", "fourth round": "R16", "4th round": "R16",
    
    # Round of 32
    "round of 32": "R32", "round 32": "R32", "third round": "R32", "3rd round": "R32",
    
    # Round of 64
    "round of 64": "R64", "round 64": "R64", "second round": "R64", "2nd round": "R64",
    
    # Round of 128
    "round of 128": "R128", "round 128": "R128", "first round": "R128", "1st round": "R128",
    
    # Qualifying rounds
    "qualifying": "Q1", "qualifier": "Q1", "qualifying 1": "Q1", "qualifying 2": "Q2", "qualifying 3": "Q3",
    
    # Round Robin
    "round robin": "RR", "group stage": "RR", "group": "RR",
    
    # Other rounds
    "bronze": "BR", "playoff": "PR", "consolation": "CR", "exhibition": "ER"
}

SURFACE_MAPPINGS = {
    # Clay courts
    "clay": "Clay", "clay court": "Clay", "red clay": "Clay", "terre battue": "Clay",
    "dirt": "Clay", "slow court": "Clay",
    
    # Hard courts
    "hard": "Hard", "hard court": "Hard", "concrete": "Hard", "asphalt": "Hard",
    "acrylic": "Hard", "deco turf": "Hard", "plexicushion": "Hard", "fast court": "Hard",
    "indoor hard": "Hard", "outdoor hard": "Hard",
    
    # Grass courts
    "grass": "Grass", "grass court": "Grass", "lawn": "Grass", "natural grass": "Grass",
    "very fast court": "Grass", "quick court": "Grass",
    
    # Carpet courts
    "carpet": "Carpet", "carpet court": "Carpet", "indoor carpet": "Carpet",
    "synthetic": "Carpet", "artificial": "Carpet"
}

TOUR_MAPPINGS = {
    # Main tours
    "atp": "ATP", "atp tour": "ATP", "men's tour": "ATP", "men tour": "ATP", "men": "ATP", "male": "ATP",
    "wta": "WTA", "wta tour": "WTA", "women's tour": "WTA", "women tour": "WTA", "women": "WTA", "female": "WTA", "ladies": "WTA",
    
    # Development tours
    "challenger": "Challenger", "atp challenger": "Challenger", "challenger tour": "Challenger", "development tour": "Challenger",
    "futures": "Futures", "atp futures": "Futures", "futures tour": "Futures", "itf futures": "Futures",
    "itf": "ITF", "itf tour": "ITF", "junior tour": "ITF", "development": "ITF",
    
    # Combined
    "both": "Both", "combined": "Both", "men and women": "Both", "atp and wta": "Both"
}

HAND_MAPPINGS = {
    # Right-handed
    "right": "R", "right-handed": "R", "right hand": "R", "righty": "R", "right handed": "R",
    
    # Left-handed
    "left": "L", "left-handed": "L", "left hand": "L", "lefty": "L", "left handed": "L", "southpaw": "L",
    
    # Ambidextrous
    "ambidextrous": "A", "both": "A", "either": "A", "switch": "A",
    
    # Unknown
    "unknown": "U", "unclear": "U", "not specified": "U"
}

GRAND_SLAM_MAPPINGS = {
    "french open": "Roland Garros", "roland garros": "Roland Garros",
    "aus open": "Australian Open", "australian open": "Australian Open",
    "wimbledon": "Wimbledon", "the championship": "Wimbledon",
    "us open": "US Open"
}

TOURNEY_LEVEL_MAPPINGS = {
    # ATP Levels (keep as-is)
    'G': 'G',  # Grand Slam
    'M': 'M',  # Masters 1000
    'A': 'A',  # ATP Tour
    'C': 'C',  # Challenger
    'D': 'D',  # Davis Cup (ATP only)
    'F': 'F',  # Tour Finals
    'E': 'E',  # Exhibition
    'J': 'J',  # Juniors
    'O': 'O',  # Olympics
    
    # WTA Levels - Standardize
    'PM': 'PM',  # Premier Mandatory
    'P': 'P',    # Premier
    'I': 'I',    # International
    'W': 'W',    # WTA Tour
    'CC': 'CC',  # Colgate Series
    
    # Historical WTA Tiers → Modern equivalents
    'T1': 'PM',  # Tier I → Premier Mandatory
    'T2': 'P',   # Tier II → Premier
    'T3': 'I',   # Tier III → International
    'T4': 'I',   # Tier IV → International
    'T5': 'I',   # Tier V → International
    
    # ITF Prize Money Levels → Standardized format
    '10': 'ITF_10K',
    '15': 'ITF_15K',
    '20': 'ITF_20K',
    '25': 'ITF_25K',
    '35': 'ITF_35K',
    '40': 'ITF_40K',
    '50': 'ITF_50K',
    '60': 'ITF_60K',
    '75': 'ITF_75K',
    '80': 'ITF_80K',
    '100': 'ITF_100K',
    '200': 'ITF_200K'
}

COMBINED_TOURNAMENT_MAPPINGS = {
    "rome": {"atp": "Rome Masters", "wta": "Rome"},
    "basel": {"atp": "Basel", "wta": "Basel"},
    "madrid": {"atp": "Madrid Masters", "wta": "Madrid"},
    "indian wells": {"atp": "Indian Wells Masters", "wta": "Indian Wells"},
    "miami": {"atp": "Miami Masters", "wta": "Miami"},
    "monte carlo": {"atp": "Monte Carlo Masters", "wta": "Monte Carlo"},
    "hamburg": {"atp": "Hamburg", "wta": "Hamburg"},
    "stuttgart": {"atp": "Stuttgart", "wta": "Stuttgart"},
    "eastbourne": {"atp": "Eastbourne", "wta": "Eastbourne"},
    "newport": {"atp": "Newport", "wta": "Newport"},
    "atlanta": {"atp": "Atlanta", "wta": "Atlanta"},
    "washington": {"atp": "Washington", "wta": "Washington"},
    "toronto": {"atp": "Toronto Masters", "wta": "Toronto"},
    "montreal": {"atp": "Montreal Masters", "wta": "Montreal"},
    "cincinnati": {"atp": "Cincinnati Masters", "wta": "Cincinnati"},
    "winston salem": {"atp": "Winston Salem", "wta": "Winston Salem"},
    "stockholm": {"atp": "Stockholm", "wta": "Stockholm"},
    "antwerp": {"atp": "Antwerp", "wta": "Antwerp"},
    "vienna": {"atp": "Vienna", "wta": "Vienna"},
    "paris": {"atp": "Paris Masters", "wta": "Paris"}
}


def standardize_tourney_level(level, tour=None, era=None):
    """
    Replace old tourney levels with new standardized levels.
    
    Args:
        level: The original tourney_level value
        tour: The tour (ATP or WTA) for context
        era: The era for historical context (optional)
    
    Returns:
        Standardized tourney_level value
    """
    if pd.isna(level) or level == '':
        return level
    
    level_str = str(level).strip()
    
    # Special case: WTA D level → BJK_Cup
    if level_str == 'D' and tour == 'WTA':
        return 'BJK_Cup'
    
    # Direct mapping
    if level_str in TOURNEY_LEVEL_MAPPINGS:
        return TOURNEY_LEVEL_MAPPINGS[level_str]
    
    # Handle unknown levels
    print(f"Warning: Unknown tourney_level '{level_str}' for tour '{tour}'")
    return level_str  # Keep as-is if unknown


class TennisMappingFactory:
    """
    Factory class for creating tennis mapping tools.
    Centralizes the creation of all tennis terminology mapping tools.
    """
    
    @staticmethod
    def create_round_mapping_tool():
        """Create the tennis round mapping tool."""
        @tool
        def get_tennis_round_mapping(round_name: str) -> str:
            """
            Map tennis fan colloquial round names to database round values.
            Handles various tennis round terminologies.
            
            Args:
                round_name: The round name to look up (e.g., 'final', 'semi-final', 'quarter-final')
                
            Returns:
                JSON string with database round value
            """
            round_lower = round_name.lower().strip()
            
            if round_lower in ROUND_MAPPINGS:
                return str({"database_round": ROUND_MAPPINGS[round_lower], "type": "tennis_round"})
            
            # Default: return as-is
            return str({"database_round": round_name, "type": "unknown"})
        
        return get_tennis_round_mapping
    
    @staticmethod
    def create_surface_mapping_tool():
        """Create the tennis surface mapping tool."""
        @tool
        def get_tennis_surface_mapping(surface: str) -> str:
            """
            Map tennis fan surface names to database surface values.
            Handles various surface terminologies.
            
            Args:
                surface: The surface name to look up (e.g., 'clay court', 'hard court', 'grass court')
                
            Returns:
                JSON string with database surface value
            """
            surface_lower = surface.lower().strip()
            
            if surface_lower in SURFACE_MAPPINGS:
                return str({"database_surface": SURFACE_MAPPINGS[surface_lower], "type": "tennis_surface"})
            
            # Default: return as-is
            return str({"database_surface": surface, "type": "unknown"})
        
        return get_tennis_surface_mapping
    
    @staticmethod
    def create_tour_mapping_tool():
        """Create the tennis tour mapping tool."""
        @tool
        def get_tennis_tour_mapping(tour: str) -> str:
            """
            Map tennis fan tour names to database tour categories.
            Handles ATP, WTA, ITF, Challenger, Futures terminology.
            
            Args:
                tour: The tour name to look up (e.g., 'atp tour', 'wta tour', 'challenger')
                
            Returns:
                JSON string with database tour information
            """
            tour_lower = tour.lower().strip()
            
            if tour_lower in TOUR_MAPPINGS:
                return str({"database_tour": TOUR_MAPPINGS[tour_lower], "type": "tennis_tour"})
            
            # Default: return as-is
            return str({"database_tour": tour, "type": "unknown"})
        
        return get_tennis_tour_mapping
    
    @staticmethod
    def create_hand_mapping_tool():
        """Create the tennis hand mapping tool."""
        @tool
        def get_tennis_hand_mapping(hand: str) -> str:
            """
            Map tennis fan hand terminology to database hand values.
            Handles handedness terminology.
            
            Args:
                hand: The hand name to look up (e.g., 'right-handed', 'left-handed', 'ambidextrous')
                
            Returns:
                JSON string with database hand value
            """
            hand_lower = hand.lower().strip()
            
            if hand_lower in HAND_MAPPINGS:
                return str({"database_hand": HAND_MAPPINGS[hand_lower], "type": "tennis_hand"})
            
            # Default: return as-is
            return str({"database_hand": hand, "type": "unknown"})
        
        return get_tennis_hand_mapping
    
    @staticmethod
    def create_tournament_mapping_tool():
        """Create the tennis tournament mapping tool."""
        @tool
        def get_tournament_mapping(tournament: str) -> str:
            """
            Map tennis fan colloquial names to database tournament names.
            Handles Grand Slams, Masters, and combined events.
            
            Args:
                tournament: The tournament name to look up (e.g., 'french open', 'aus open', 'wimbledon')
                
            Returns:
                JSON string with database tournament names
            """
            tournament_lower = tournament.lower().strip()
            
            # Check Grand Slams first
            if tournament_lower in GRAND_SLAM_MAPPINGS:
                return str({"database_name": GRAND_SLAM_MAPPINGS[tournament_lower], "type": "grand_slam"})
            
            # Check combined tournaments
            if tournament_lower in COMBINED_TOURNAMENT_MAPPINGS:
                return str(COMBINED_TOURNAMENT_MAPPINGS[tournament_lower])
            
            # Default: return as-is
            return str({"database_name": tournament, "type": "unknown"})
        
        return get_tournament_mapping
    
    @staticmethod
    def create_tourney_level_mapping_tool():
        """Create the tennis tourney level mapping tool."""
        @tool
        def get_tourney_level_mapping(level: str) -> str:
            """
            Map tennis tournament level codes to descriptions.
            Helps understand what each tourney_level code means.
            
            Args:
                level: The tourney_level code to look up (e.g., 'G', 'M', 'PM', 'ITF_25K')
                
            Returns:
                JSON string with level description
            """
            level_upper = level.upper().strip()
            
            # Level descriptions
            level_descriptions = {
                'G': 'Grand Slam tournaments (Australian Open, French Open, Wimbledon, US Open)',
                'M': 'ATP Masters 1000 tournaments (Indian Wells, Miami, Madrid, etc.)',
                'PM': 'WTA Premier Mandatory tournaments (Indian Wells, Miami, Madrid, Beijing)',
                'A': 'ATP Tour events (ATP 250, ATP 500 level tournaments)',
                'P': 'WTA Premier tournaments (500-level events)',
                'I': 'WTA International tournaments (250-level events)',
                'C': 'ATP Challenger tournaments',
                'D': 'Davis Cup (men\'s team competition)',
                'BJK_CUP': 'Billie Jean King Cup (women\'s team competition)',
                'F': 'Tour Finals (ATP Finals, WTA Finals)',
                'E': 'Exhibition events (non-sanctioned)',
                'J': 'Junior tournaments',
                'O': 'Olympic tennis events',
                'W': 'WTA Tour events (general tour level)',
                'CC': 'Colgate Series (historical WTA tournament series)',
                'ITF_10K': 'ITF $10,000 tournaments',
                'ITF_15K': 'ITF $15,000 tournaments',
                'ITF_20K': 'ITF $20,000 tournaments',
                'ITF_25K': 'ITF $25,000 tournaments',
                'ITF_35K': 'ITF $35,000 tournaments',
                'ITF_40K': 'ITF $40,000 tournaments',
                'ITF_50K': 'ITF $50,000 tournaments',
                'ITF_60K': 'ITF $60,000 tournaments',
                'ITF_75K': 'ITF $75,000 tournaments',
                'ITF_80K': 'ITF $80,000 tournaments',
                'ITF_100K': 'ITF $100,000 tournaments',
                'ITF_200K': 'ITF $200,000 tournaments'
            }
            
            if level_upper in level_descriptions:
                return str({
                    "level_code": level_upper,
                    "description": level_descriptions[level_upper],
                    "type": "tourney_level"
                })
            
            # Default: return as-is
            return str({"level_code": level, "description": "Unknown level", "type": "unknown"})
        
        return get_tourney_level_mapping
    
    @staticmethod
    def create_all_mapping_tools() -> List:
        """
        Create all tennis mapping tools.
        
        Returns:
            List of all mapping tools
        """
        return [
            TennisMappingFactory.create_round_mapping_tool(),
            TennisMappingFactory.create_surface_mapping_tool(),
            TennisMappingFactory.create_tour_mapping_tool(),
            TennisMappingFactory.create_hand_mapping_tool(),
            TennisMappingFactory.create_tournament_mapping_tool(),
            TennisMappingFactory.create_tourney_level_mapping_tool()
        ]
