# Analysis of `create_system_prompt` Method
## Duplicates and Conflicts by Functionality

---

## 1. TOURNAMENT MAPPING & NAME HANDLING

### **DUPLICATE SECTIONS:**

**Section A: Tournament Name Mapping (Lines 165-176)**
- Mentions: use `get_tournament_mapping` tool
- Cached mappings for Grand Slams
- Combined tournaments (Rome, Madrid, Miami) need UNION
- States: "NEVER search only one tournament when user doesn't specify ATP/WTA"

**Section B: Tournament Case Sensitivity (Lines 178-189)**
- Mentions: use `get_tournament_case_variations` tool
- US Open case variations ("US Open" vs "Us Open")
- States: "NEVER search only one case variation for US Open"
- SQL Pattern: `WHERE (tourney_name = 'US Open' OR tourney_name = 'Us Open')`

**Section C: Grand Slam Analysis (Lines 291-320)**
- Mentions: use `get_tournament_mapping` AND `get_tournament_case_variations`
- Mentions: use `get_grand_slam_tournament_names` tool
- Repeats same mapping examples
- Repeats same "correct vs wrong approach" concept

**Section D: Combined Tournament Queries (Lines 471-481)**
- Repeats UNION pattern for ATP+WTA tournaments
- Same examples: Miami, Rome, Madrid
- Same instruction: "NEVER return only ATP or only WTA results"

### **CONFLICTS:**

1. **Tool Recommendation Conflict:**
   - Section A recommends: `get_tournament_mapping`
   - Section C recommends: `get_grand_slam_tournament_names` (alternative)
   - Both claim to handle Grand Slams, causing confusion

2. **Case Handling Conflict:**
   - Section B says: ALWAYS use `get_tournament_case_variations` for US Open
   - Section C says: Use `get_tournament_case_variations` OR `get_grand_slam_tournament_names`
   - Unclear which tool to use when

3. **Mapping Process Redundancy:**
   - Section C has TWO mapping processes (lines 307-315) for the same thing
   - Both describe how to map Grand Slams differently

---

## 2. SURFACE MAPPING & QUERIES

### **DUPLICATE SECTIONS:**

**Section A: Tennis Surface Mapping (Lines 346-363)**
- Lists surface mappings: indoor → Carpet, clay → Clay, etc.
- States: "ALWAYS use get_surface_mapping tool"
- Examples of surface queries

**Section B: Surface-Specific Queries (Lines 390-418)**
- Repeats: "ALWAYS use surface mapping"
- Repeats same mappings: grass → Grass, clay → Clay, etc.
- Adds query patterns and answer format requirements
- States: "ALWAYS use get_surface_mapping tool"

**Section C: Tennis Surface Terminology (Lines 495-508)**
- Repeats: "ALWAYS use get_tennis_surface_mapping tool" (NOTE: different tool name!)
- Lists mappings again: "Clay Court" → "Clay", "Red Clay" → "Clay"
- More detailed mappings than Section A
- Uses different tool name: `get_tennis_surface_mapping` vs `get_surface_mapping`

### **CONFLICTS:**

1. **Tool Name Conflict:**
   - Section A & B: `get_surface_mapping`
   - Section C: `get_tennis_surface_mapping`
   - Which tool actually exists?

2. **Mapping Detail Conflict:**
   - Section A: Simple mappings (indoor → Carpet)
   - Section C: More detailed (Clay Court → Clay, Red Clay → Clay, Terre Battue → Clay)
   - Unclear which mappings are correct

3. **Redundant Instructions:**
   - All three sections say "ALWAYS use [tool]"
   - Same concept repeated three times with minor variations

---

## 3. TOUR FILTERING (ATP vs WTA)

### **DUPLICATE SECTIONS:**

**Section A: Tournament Winner Queries (Lines 276-289)**
- Mentions: "When user specifies ATP/WTA, ALWAYS filter by tour column"
- Examples: ATP Indian Wells, WTA Indian Wells
- States: "ALWAYS check if user specifies ATP/WTA"

**Section B: Tour Filtering (Lines 483-493)**
- Repeats: "When user specifies ATP/WTA, ALWAYS filter by tour column"
- Same examples: ATP Indian Wells, WTA Indian Wells
- Mentions: "use get_tennis_tour_mapping tool if needed"
- Repeats: "If user doesn't specify ATP/WTA, search both tours using UNION"

**Section C: Combined Tournament Queries (Lines 471-481)**
- Mentions: "When user asks without specifying ATP/WTA, ALWAYS search BOTH tours"
- Same UNION pattern

### **CONFLICTS:**

1. **Tool Mention Conflict:**
   - Section B mentions `get_tennis_tour_mapping` tool
   - Section A doesn't mention this tool
   - Unclear if this tool exists or when to use it

2. **Repetitive Instructions:**
   - Same concept explained in multiple places
   - Same examples repeated

---

## 4. RANKING QUESTIONS

### **DUPLICATE SECTIONS:**

**Section A: Ranking Question Analysis (Lines 191-236)**
- Comprehensive decision tree for ranking questions
- Official rankings vs match-time rankings
- Tour determination
- Temporal context
- SQL construction rules
- Validation checks
- Examples

**Section B: Specific Tennis Question Patterns - Ranking (Lines 430-434)**
- "Which player has the highest ranking?"
- "Highest ranking" → Best ranking (rank = 1)
- "DON'T use UNION ALL across tours - use simple single query"

### **CONFLICTS:**

1. **Contradictory Instructions:**
   - Section A (line 213): "If user doesn't specify ATP/WTA, search both tours using UNION"
   - Section B (line 434): "DON'T use UNION ALL across tours - use simple single query"
   - **DIRECT CONFLICT!**

2. **Redundancy:**
   - Section A is comprehensive (46 lines)
   - Section B repeats ranking concepts but contradicts Section A

---

## 5. HEAD-TO-HEAD QUERIES

### **DUPLICATE SECTIONS:**

**Section A: Head-to-Head Analysis (Lines 322-344)**
- Distinguishes between specific player wins vs full head-to-head
- SQL patterns for both cases
- Keyword analysis (beaten, head-to-head, total matches)
- Examples

**Section B: Head-to-Head Queries Optimized (Lines 510-521)**
- "For head-to-head questions, use sql_db_query with optimized queries"
- Mentions: include surface column
- Exclude W/O, DEF, RET matches
- Double-check counting
- Example format

### **CONFLICTS:**

1. **Different Focus:**
   - Section A: SQL patterns and query construction
   - Section B: Response formatting and counting logic
   - Should be merged into one comprehensive section

2. **Missing Integration:**
   - Section A doesn't mention excluding walkovers
   - Section B doesn't mention the distinction between "beaten" vs "head-to-head"

---

## 6. ROUND MAPPING & HANDLING

### **DUPLICATE SECTIONS:**

**Section A: Tennis Round Terminology (Lines 453-469)**
- Use `get_tennis_round_mapping` tool
- Common mappings: Final → F, Semi-Final → SF
- Examples
- Mentions: column is 'round', NOT 'round_num'

**Section B: Grouping Matches by Round (Lines 538-574)**
- When displaying results, use 'round' column
- Round order for display
- Expected match counts per round
- Formatting instructions

### **CONFLICTS:**

1. **Different Purposes:**
   - Section A: Converting user terminology to database values
   - Section B: Displaying results grouped by rounds
   - Should be separate but currently adjacent/overlapping

---

## 7. SQL SYNTAX & QUERY PATTERNS

### **DUPLICATE SECTIONS:**

**Section A: SQL Syntax for UNION (Lines 582-586)**
- ORDER BY must come AFTER UNION
- Correct vs wrong syntax

**Section B: SQL Logical Operator Precedence (Lines 588-597)**
- Use parentheses with OR and AND
- Multiple examples

**Section C: Common Query Patterns (Lines 154-163)**
- Basic query examples
- Tournament winners, head-to-head, surface performance

**Section D: Query Optimization Tips (Lines 142-152)**
- Use event_year, event_month for date filtering
- Use set1, set2, etc. for score analysis

**Section E: Optimized Query Patterns (Lines 606-611)**
- Use specialized tools
- Include player names
- Add proper filtering

### **CONFLICTS:**

1. **Scattered Information:**
   - SQL syntax rules spread across multiple sections
   - No clear organization
   - Same concepts mentioned multiple times

---

## 8. RESPONSE FORMATTING

### **DUPLICATE SECTIONS:**

**Section A: Enhanced Response Quality (Lines 523-528)**
- Include player names
- Provide context
- Format scores clearly

**Section B: Response Formatting for Tournament Results (Lines 530-536)**
- Format as: "Player A defeated Player B 6-4, 6-4"
- Never just list scores

**Section C: Answer Format for Surface Queries (Lines 408-413)**
- Simple format: "Player: count, Player: count"
- Don't use full sentences

**Section D: Upset Analysis Answer Format (Lines 380-383)**
- Simple format: "Surface: count, Surface: count"
- Don't use full sentences

### **CONFLICTS:**

1. **Inconsistent Formatting Rules:**
   - Section A & B: Use full sentences with context
   - Section C & D: Use simple format, no full sentences
   - **CONTRADICTORY!**

2. **Different Standards:**
   - Some sections say "include context"
   - Others say "don't use full sentences"
   - Unclear which applies when

---

## 9. PERFORMANCE OPTIMIZATION

### **DUPLICATE SECTIONS:**

**Section A: Performance Optimization Rules (Lines 24-29)**
- Use cached mapping tools
- Use optimized queries
- Prefer specialized tools

**Section B: Performance Optimization Workflow (Lines 628-633)**
- Use cached mapping tools
- Use specialized tools
- Use optimized patterns
- Format results clearly

### **CONFLICTS:**

1. **Redundancy:**
   - Same concepts at beginning and end
   - Should be consolidated

---

## 10. PLAYER NAME HANDLING

### **DUPLICATE SECTIONS:**

**Section A: Always Include Player Names (Lines 576-580)**
- NEVER use queries without player names
- ALWAYS include winner_name and loser_name

**Section B: Player Name Variations (Lines 599-604)**
- Names may be different
- Use LIKE operator
- Try simpler names

**Section C: Enhanced Response Quality (Line 524)**
- ALWAYS include player names in responses

**Section D: Optimized Query Patterns (Line 608)**
- Include player names in all queries

### **CONFLICTS:**

1. **Excessive Repetition:**
   - "Include player names" mentioned 4+ times
   - Should be one clear instruction

---

## SUMMARY OF MAJOR ISSUES

### **CRITICAL CONFLICTS:**

1. **Ranking Questions - UNION Conflict:**
   - Line 213: "search both tours using UNION"
   - Line 434: "DON'T use UNION ALL across tours"
   - **DIRECT CONTRADICTION**

2. **Response Formatting - Sentence Conflict:**
   - Lines 523-528: Use full sentences with context
   - Lines 408-413: Don't use full sentences
   - **CONTRADICTORY INSTRUCTIONS**

3. **Surface Mapping Tool Name:**
   - `get_surface_mapping` vs `get_tennis_surface_mapping`
   - **UNCLEAR WHICH TOOL EXISTS**

### **MAJOR DUPLICATIONS:**

1. **Tournament Mapping:** 4 sections (165-176, 178-189, 291-320, 471-481)
2. **Surface Mapping:** 3 sections (346-363, 390-418, 495-508)
3. **Tour Filtering:** 3 sections (276-289, 471-481, 483-493)
4. **Player Names:** 4+ mentions (576-580, 524, 608, 28)
5. **Response Formatting:** 4 sections (523-528, 530-536, 408-413, 380-383)

### **ORGANIZATIONAL ISSUES:**

1. **No Clear Structure:** Sections are not grouped logically
2. **Scattered Related Info:** Related concepts appear far apart
3. **Inconsistent Formatting:** Some sections use ✅/❌, others don't
4. **Mixed Abstraction Levels:** High-level concepts mixed with specific SQL examples

---

## RECOMMENDATIONS FOR IMPROVEMENT

### **1. CONSOLIDATION STRATEGY:**

**Group by Functionality:**
- Mapping & Terminology (Tournament, Surface, Round, Tour)
- Query Construction (SQL Patterns, Syntax Rules)
- Result Formatting (Response Format, Display Rules)
- Specialized Queries (Ranking, Head-to-Head, Upsets)
- Performance Guidelines

### **2. RESOLVE CONFLICTS:**

1. **Ranking UNION:** Decide on one approach - either UNION or single query, document when to use each
2. **Response Format:** Create clear rules for when to use full sentences vs simple format
3. **Tool Names:** Verify actual tool names and standardize references

### **3. REDUCE REDUNDANCY:**

1. **Merge Duplicate Sections:** Combine related sections into one comprehensive section
2. **Cross-Reference:** Instead of repeating, reference other sections
3. **Template Format:** Create reusable instruction templates

### **4. IMPROVE ORGANIZATION:**

1. **Hierarchical Structure:** Main categories → Subcategories → Specific rules
2. **Consistent Formatting:** Use same markdown structure throughout
3. **Logical Flow:** Related concepts grouped together

### **5. CREATE REFERENCE SECTIONS:**

1. **Quick Reference:** Common patterns, SQL snippets, tool mappings
2. **Decision Trees:** Visual flowcharts for complex decisions
3. **Examples Index:** Categorized examples for quick lookup

