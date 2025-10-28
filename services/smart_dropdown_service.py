"""
Smart Dropdown Service for Enhanced UI
Provides intelligent dropdown options with search, filtering, and smart defaults
"""

import pandas as pd
from typing import List, Dict, Any, Optional
import streamlit as st  # pyright: ignore[reportMissingImports]
from functools import lru_cache

class SmartDropdownService:
    """Service for smart dropdown management."""
    
    def __init__(self, db_service):
        """Initialize smart dropdown service."""
        self.db_service = db_service
        
        # Popular players (most searched/important)
        self.popular_players = [
            "Roger Federer", "Rafael Nadal", "Novak Djokovic", "Serena Williams", "Venus Williams",
            "Andy Murray", "Stefanos Tsitsipas", "Carlos Alcaraz", "Jannik Sinner", "Daniil Medvedev",
            "Alexander Zverev", "Casper Ruud", "Holger Rune", "Taylor Fritz", "Frances Tiafoe"
        ]
        
        # Popular tournaments
        self.popular_tournaments = [
            "Wimbledon", "French Open", "US Open", "Australian Open",
            "Miami Masters", "Indian Wells Masters", "Monte Carlo Masters", "Madrid Masters",
            "Rome Masters", "Cincinnati Masters", "Paris Masters", "ATP Finals"
        ]
        
        # Recent years (most relevant)
        self.recent_years = [str(year) for year in range(2024, 2015, -1)]
    
    @st.cache_data(ttl=300)
    def get_smart_player_options(_self) -> Dict[str, List[str]]:
        """Get smart player options with categories."""
        try:
            # Get all players from database
            all_players = _self.db_service.get_all_players()
            all_players = [p for p in all_players if p != "All Players"]
            
            # Categorize players
            popular_in_db = [p for p in _self.popular_players if p in all_players]
            other_players = [p for p in all_players if p not in _self.popular_players]
            
            return {
                "popular": popular_in_db,
                "recent": [],  # Could be populated from session state
                "all": other_players[:50],  # Limit to top 50 others
                "total_count": len(all_players)
            }
        except Exception as e:
            st.error(f"Error getting player options: {e}")
            return {
                "popular": _self.popular_players,
                "recent": [],
                "all": [],
                "total_count": 0
            }
    
    @st.cache_data(ttl=300)
    def get_smart_tournament_options(_self) -> Dict[str, List[str]]:
        """Get smart tournament options with categories."""
        try:
            all_tournaments = _self.db_service.get_all_tournaments()
            all_tournaments = [t for t in all_tournaments if t != "All Tournaments"]
            
            # Categorize tournaments
            popular_in_db = [t for t in _self.popular_tournaments if t in all_tournaments]
            other_tournaments = [t for t in all_tournaments if t not in _self.popular_tournaments]
            
            return {
                "grand_slams": [t for t in popular_in_db if any(gs in t for gs in ["Wimbledon", "French Open", "US Open", "Australian Open"])],
                "masters": [t for t in popular_in_db if "Masters" in t],
                "other": other_tournaments[:30],  # Limit others
                "total_count": len(all_tournaments)
            }
        except Exception as e:
            st.error(f"Error getting tournament options: {e}")
            return {
                "grand_slams": ["Wimbledon", "French Open", "US Open", "Australian Open"],
                "masters": ["Miami Masters", "Indian Wells Masters"],
                "other": [],
                "total_count": 0
            }
    
    def get_search_results(self, search_term: str, category: str = "players") -> List[str]:
        """Get search results for a given term."""
        if not search_term or len(search_term) < 2:
            return []
        
        try:
            if category == "players":
                all_items = self.db_service.get_all_players()
            elif category == "tournaments":
                all_items = self.db_service.get_all_tournaments()
            else:
                return []
            
            # Filter items containing search term
            search_lower = search_term.lower()
            results = [item for item in all_items if search_lower in item.lower()]
            
            # Prioritize popular items
            if category == "players":
                popular = [p for p in self.popular_players if search_lower in p.lower()]
                other = [p for p in results if p not in self.popular_players]
                return popular + other[:20]  # Limit results
            else:
                return results[:20]
                
        except Exception as e:
            st.error(f"Error searching {category}: {e}")
            return []
    
    def get_quick_filter_buttons(self, category: str) -> Dict[str, List[str]]:
        """Get quick filter button options."""
        if category == "players":
            return {
                "🏆 Legends": ["Roger Federer", "Rafael Nadal", "Novak Djokovic", "Serena Williams"],
                "⭐ Current Stars": ["Carlos Alcaraz", "Jannik Sinner", "Stefanos Tsitsipas", "Daniil Medvedev"],
                "🇺🇸 Americans": ["Taylor Fritz", "Frances Tiafoe", "Ben Shelton", "Tommy Paul"]
            }
        elif category == "tournaments":
            return {
                "🏆 Grand Slams": ["Wimbledon", "French Open", "US Open", "Australian Open"],
                "🏟️ Masters 1000": ["Miami Masters", "Indian Wells Masters", "Monte Carlo Masters"],
                "🌍 ATP Finals": ["ATP Finals", "WTA Finals"]
            }
        elif category == "surfaces":
            return {
                "🏟️ Surfaces": ["Hard", "Clay", "Grass", "Carpet"]
            }
        return {}
    
    def get_smart_defaults(self) -> Dict[str, str]:
        """Get smart default selections."""
        return {
            "player": "All Players",
            "opponent": "All Opponents", 
            "tournament": "All Tournaments",
            "year": "All Years",
            "surface": "All Surfaces"
        }
