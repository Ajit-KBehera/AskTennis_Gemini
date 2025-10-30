"""
Tennis Mapping Dictionaries
Contains all tennis terminology mapping dictionaries for converting user terminology to database values.
"""

# =============================================================================
# TENNIS MAPPING DICTIONARIES
# =============================================================================

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
    "clay": "Clay", "clay court": "Clay", "clay courts": "Clay", "red clay": "Clay", "terre battue": "Clay",
    "dirt": "Clay", "slow court": "Clay",
    
    # Hard courts
    "hard": "Hard", "hard court": "Hard", "hard courts": "Hard", "concrete": "Hard", "asphalt": "Hard",
    "acrylic": "Hard", "deco turf": "Hard", "plexicushion": "Hard", "fast court": "Hard",
    "indoor hard": "Hard", "outdoor hard": "Hard",
    
    # Grass courts
    "grass": "Grass", "grass court": "Grass", "grass courts": "Grass", "lawn": "Grass", "natural grass": "Grass",
    "very fast court": "Grass", "quick court": "Grass",
    
    # Carpet courts
    "carpet": "Carpet", "carpet court": "Carpet", "carpet courts": "Carpet", "indoor carpet": "Carpet",
    "synthetic": "Carpet", "artificial": "Carpet"
}

TOUR_MAPPINGS = {
    # Main tours
    "atp": "ATP", "atp tour": "ATP", "men's tour": "ATP", "men tour": "ATP", "men": "ATP", "male": "ATP",
    "wta": "WTA", "wta tour": "WTA", "women's tour": "WTA", "women tour": "WTA", "women": "WTA", "female": "WTA", "ladies": "WTA",
    "main tour": "Main Tour", "main": "Main Tour", "professional": "Main Tour", "pro tour": "Main Tour",
    
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
    # French Open variations
    "french open": "Roland Garros", "roland garros": "Roland Garros", "french": "Roland Garros",
    "French Open": "Roland Garros", "Roland Garros": "Roland Garros", "French": "Roland Garros",
    
    # Australian Open variations
    "aus open": "Australian Open", "australian open": "Australian Open", "aus": "Australian Open",
    "Australian Open": "Australian Open", "Aus Open": "Australian Open", "Australian": "Australian Open",
    
    # Wimbledon variations
    "wimbledon": "Wimbledon", "the championship": "Wimbledon", "wimby": "Wimbledon",
    "Wimbledon": "Wimbledon", "The Championship": "Wimbledon", "Wimby": "Wimbledon",
    
    # US Open variations
    "us open": "US Open", "us": "US Open",
    "US Open": "US Open", "US": "US Open"
}

TOURNEY_LEVEL_MAPPINGS = {
    # ATP Levels
    'G': 'G',  # Grand Slam
    'M': 'M',  # Masters 1000
    'A': 'A',  # ATP Tour
    'C': 'C',  # Challenger
    'D': 'D',  # Davis Cup (ATP only)
    'F': 'F',  # Tour Finals
    'E': 'E',  # Exhibition
    'J': 'J',  # Juniors
    'O': 'O',  # Olympics
    
    # WTA Levels
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
    
    # ITF Prize Money Levels
    '10': 'ITF_10K', '15': 'ITF_15K', '20': 'ITF_20K', '25': 'ITF_25K',
    '35': 'ITF_35K', '40': 'ITF_40K', '50': 'ITF_50K', '60': 'ITF_60K',
    '75': 'ITF_75K', '80': 'ITF_80K', '100': 'ITF_100K', '200': 'ITF_200K'
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

# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    'ROUND_MAPPINGS',
    'SURFACE_MAPPINGS', 
    'TOUR_MAPPINGS',
    'HAND_MAPPINGS',
    'GRAND_SLAM_MAPPINGS',
    'TOURNEY_LEVEL_MAPPINGS',
    'COMBINED_TOURNAMENT_MAPPINGS'
]

