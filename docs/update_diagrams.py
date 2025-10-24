#!/usr/bin/env python3
"""
Script to add ASCII art diagrams to documentation files.
This ensures diagrams are visible in all text viewers.
"""

import os
import re

def add_ascii_art_to_file(file_path):
    """Add ASCII art diagrams to a markdown file."""
    
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add ASCII art for Data Model
    if "03_Data_Model.md" in file_path:
        ascii_art = """
### **Visual Database Schema**
```
┌─────────────────────────────────────────────────────────────────┐
│                        MATCHES TABLE                           │
├─────────────────────────────────────────────────────────────────┤
│  tourney_id  │  winner_id  │  loser_id   │  surface  │  score  │
│  tourney_name │  winner_name │  loser_name │  round    │  minutes │
│  event_year  │  event_month │  event_date │  w_ace    │  l_ace   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        PLAYERS TABLE                           │
├─────────────────────────────────────────────────────────────────┤
│  player_id  │  name_first  │  name_last  │  hand     │  height  │
│  dob        │  ioc         │  wikidata_id │  tour      │  full_name │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                       RANKINGS TABLE                           │
├─────────────────────────────────────────────────────────────────┤
│  ranking_date │  rank  │  player  │  points  │  tournaments  │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     DOUBLES_MATCHES TABLE                      │
├─────────────────────────────────────────────────────────────────┤
│  tourney_id  │  winner1_id │  winner2_id │  loser1_id │  loser2_id │
│  winner1_name │  winner2_name │  loser1_name │  loser2_name │  score │
└─────────────────────────────────────────────────────────────────┘
```

### **Table Relationships**
```
MATCHES ──┐
          ├── PLAYERS (winner_id, loser_id)
          └── RANKINGS (player)
                │
                ▼
DOUBLES_MATCHES ──┐
                  ├── PLAYERS (winner1_id, winner2_id, loser1_id, loser2_id)
                  └── RANKINGS (player)
```
"""
        
        # Insert ASCII art after the first diagram section
        if "## 📊 Database Schema Diagram" in content:
            content = content.replace(
                "## 📊 Database Schema Diagram",
                "## 📊 Database Schema Diagram" + ascii_art
            )
    
    # Add ASCII art for Use Case Diagram
    elif "05_Use_Case_Diagram.md" in file_path:
        ascii_art = """
### **Visual Use Case Overview**
```
┌─────────────────────────────────────────────────────────────────┐
│                        ACTORS                                  │
├─────────────────────────────────────────────────────────────────┤
│  Tennis Enthusiast  │  Tennis Analyst  │  Tennis Researcher    │
│  Tennis Journalist  │  Tennis Coach    │  Tennis Player       │
│  System Admin       │  Data Admin      │  AI System           │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      USE CASES                                 │
├─────────────────────────────────────────────────────────────────┤
│  Ask Questions     │  Statistical Analysis │  Research         │
│  Get Player Info    │  Generate Reports     │  Historical Data  │
│  View Results       │  Analyze Trends       │  Academic Study   │
│  Compare Players    │  Export Data          │  Performance      │
└─────────────────────────────────────────────────────────────────┘
```

### **User Interaction Flow**
```
Tennis Enthusiast ──┐
                    ├── Ask Basic Questions ──┐
Tennis Analyst ─────┤                        ├── AI System ──┐
                    ├── Statistical Analysis ──┤              │
Tennis Researcher ──┤                        │              │
                    ├── Research Queries ──────┤              │
Tennis Journalist ──┤                        │              │
                    ├── Fact Checking ────────┤              │
Tennis Coach ───────┤                        │              │
                    ├── Performance Analysis ──┤              │
Tennis Player ──────┤                        │              │
                    └── Personal Analysis ────┘              │
                                                             │
                                                             ▼
                    ┌─────────────────────────────────────────┐
                    │              RESPONSES                  │
                    ├─────────────────────────────────────────┤
                    │  Formatted Data  │  Charts & Graphs    │
                    │  Text Summary    │  Export Options     │
                    └─────────────────────────────────────────┘
```
"""
        
        if "## 📊 Use Case Diagram" in content:
            content = content.replace(
                "## 📊 Use Case Diagram",
                "## 📊 Use Case Diagram" + ascii_art
            )
    
    # Add ASCII art for State Diagram
    elif "06_State_Diagram.md" in file_path:
        ascii_art = """
### **Visual State Flow**
```
┌─────────────────────────────────────────────────────────────────┐
│                    SYSTEM STATES                                │
├─────────────────────────────────────────────────────────────────┤
│  [*] ──→ Initialization ──→ Ready ──→ ProcessingQuery ──→ Ready │
│         │                │           │                        │
│         ▼                ▼           ▼                        │
│    ErrorState ──────────┐           │                        │
│         │               │           │                        │
│         ▼               │           ▼                        │
│    FatalError ──────────┘      ErrorState ──────────────────┘
└─────────────────────────────────────────────────────────────────┘
```

### **State Transition Flow**
```
1. [*] (Start)
   │
   ▼
2. Initialization
   │
   ▼
3. Ready
   │
   ▼
4. ProcessingQuery
   │
   ▼
5. Ready (Success)
   │
   ▼
6. ErrorState (if error)
   │
   ▼
7. FatalError (if critical)
   │
   ▼
8. [*] (End)
```
"""
        
        if "## 🎯 System State Diagram" in content:
            content = content.replace(
                "## 🎯 System State Diagram",
                "## 🎯 System State Diagram" + ascii_art
            )
    
    # Add ASCII art for UI/UX Design
    elif "07_UI_UX_Design.md" in file_path:
        ascii_art = """
### **Visual UI Layout**
```
┌─────────────────────────────────────────────────────────────────┐
│                        HEADER                                  │
├─────────────────────────────────────────────────────────────────┤
│  Logo & Title  │  Navigation Menu  │  User Profile            │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    MAIN CONTENT AREA                           │
├─────────────────────────────────────────────────────────────────┤
│  Search Interface  │  Query Input  │  Example Questions       │
│  Results Display   │  Data Tables  │  Charts & Graphs         │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        SIDEBAR                                 │
├─────────────────────────────────────────────────────────────────┤
│  Quick Stats  │  Recent Queries  │  Help & Tips              │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        FOOTER                                  │
├─────────────────────────────────────────────────────────────────┤
│  System Status  │  Version Info  │  Contact Info             │
└─────────────────────────────────────────────────────────────────┘
```

### **Component Hierarchy**
```
UI Application
├── Header Component
│   ├── Logo
│   ├── Title
│   └── User Menu
├── Main Content
│   ├── Search Interface
│   ├── Query Input
│   └── Results Display
├── Sidebar
│   ├── Quick Stats
│   ├── Recent Queries
│   └── Help & Tips
└── Footer
    ├── System Status
    ├── Version Info
    └── Contact Info
```
"""
        
        if "## 🎨 UI/UX Design Diagram" in content:
            content = content.replace(
                "## 🎨 UI/UX Design Diagram",
                "## 🎨 UI/UX Design Diagram" + ascii_art
            )
    
    # Write the updated content back to the file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Updated {file_path} with ASCII art diagrams")

def main():
    """Update all documentation files with ASCII art."""
    
    docs_dir = "/Users/ajitbehera/Codes/AskTennis_Streamlit/docs"
    
    files_to_update = [
        "03_Data_Model.md",
        "05_Use_Case_Diagram.md", 
        "06_State_Diagram.md",
        "07_UI_UX_Design.md"
    ]
    
    for filename in files_to_update:
        file_path = os.path.join(docs_dir, filename)
        add_ascii_art_to_file(file_path)
    
    print("✅ All documentation files updated with ASCII art diagrams!")
    print("📊 Diagrams are now visible in all text viewers")

if __name__ == "__main__":
    main()
