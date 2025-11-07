# Tournament Mapping Improvement Plan

## Executive Summary
This plan outlines improvements to expand tournament mapping coverage from 0.13% (25 tournaments) to a more comprehensive system that handles the majority of user queries effectively.

**Current State**: 25 tournaments explicitly mapped out of 19,652 total tournaments  
**Target State**: Comprehensive mapping system with fuzzy matching and historical name support

---

## Phase 1: Expand Mapping Dictionary (Priority: HIGH)

### 1.1 Identify High-Priority Tournaments
**Objective**: Add explicit mappings for the most frequently queried tournaments

**Tasks**:
1. **Analyze Query Patterns** (Week 1)
   - Query database for tournament frequency in matches table
   - Identify top 100-200 tournaments by match count
   - Categorize by tournament level (Masters 1000, ATP 500, WTA Premier, etc.)

2. **Research Tournament Names** (Week 1)
   - Compile official tournament names from ATP/WTA websites
   - Document common user variations (e.g., "Dubai" vs "Dubai Tennis Championships")
   - Identify sponsor name changes over time

3. **Create Expanded Mapping Dictionary** (Week 2)
   - Add Masters 1000 tournaments (all 9):
     - Indian Wells Masters ✓ (already mapped)
     - Miami Masters ✓ (already mapped)
     - Monte Carlo Masters ✓ (already mapped)
     - Madrid Masters ✓ (already mapped)
     - Rome Masters ✓ (already mapped)
     - Toronto/Montreal Masters ✓ (already mapped)
     - Cincinnati Masters ✓ (already mapped)
     - Shanghai Masters (NEW)
     - Paris Masters ✓ (already mapped)
   
   - Add ATP 500 tournaments (top 10-15):
     - Barcelona Open Banc Sabadell
     - Rotterdam Open (ABN AMRO Open)
     - Dubai Tennis Championships
     - Acapulco Open
     - Queen's Club Championships
     - Halle Open
     - Hamburg European Open
     - Washington Open (Citi Open)
     - Toronto/Montreal (Rogers Cup)
     - Beijing Open
     - Vienna Open ✓ (already mapped)
     - Basel Open ✓ (already mapped)
     - Tokyo Open
   
   - Add WTA Premier tournaments (top 10-15):
     - Dubai Tennis Championships
     - Doha Open (Qatar Total Open)
     - Indian Wells ✓ (already mapped)
     - Miami ✓ (already mapped)
     - Madrid ✓ (already mapped)
     - Rome ✓ (already mapped)
     - Toronto/Montreal ✓ (already mapped)
     - Cincinnati ✓ (already mapped)
     - Wuhan Open
     - Beijing Open
     - Moscow Open
     - Stuttgart ✓ (already mapped)
     - Eastbourne ✓ (already mapped)

**Deliverables**:
- Expanded `GRAND_SLAM_MAPPINGS` dictionary (if needed)
- New `MASTERS_1000_MAPPINGS` dictionary
- New `ATP_500_MAPPINGS` dictionary
- New `WTA_PREMIER_MAPPINGS` dictionary
- Updated `COMBINED_TOURNAMENT_MAPPINGS` dictionary

**Estimated Effort**: 2-3 weeks  
**Risk**: Low - straightforward dictionary expansion

---

## Phase 2: Implement Fuzzy Matching (Priority: HIGH)

### 2.1 Add String Similarity Library
**Objective**: Enable partial and fuzzy matching for tournament names

**Tasks**:
1. **Choose Similarity Algorithm** (Week 1)
   - Evaluate options:
     - `difflib.SequenceMatcher` (built-in, no dependencies)
     - `fuzzywuzzy` / `rapidfuzz` (external, better performance)
     - `Levenshtein distance` (custom implementation)
   - **Recommendation**: Use `rapidfuzz` (fast, MIT licensed, maintained)

2. **Install Dependencies** (Week 1)
   - Add `rapidfuzz` to `requirements.txt`
   - Update documentation

3. **Implement Fuzzy Matching Function** (Week 2)
   - Create `_fuzzy_match_tournament()` helper function
   - Parameters:
     - Input tournament name
     - Similarity threshold (default: 0.85)
     - Max results (default: 3)
   - Return top matches with similarity scores

4. **Integrate with Mapping Function** (Week 2)
   - Update `_get_tournament_mapping()` to:
     1. Check explicit mappings first (current behavior)
     2. If not found, query database for all tournament names
     3. Use fuzzy matching to find best matches
     4. Return top match if similarity > threshold
     5. Return multiple candidates if user needs to disambiguate

**Deliverables**:
- New `fuzzy_matching.py` module
- Updated `_get_tournament_mapping()` function
- Unit tests for fuzzy matching
- Performance benchmarks

**Estimated Effort**: 2-3 weeks  
**Risk**: Medium - requires database queries, performance considerations

**Dependencies**: Phase 1 (can run in parallel)

---

## Phase 3: Historical Name Mapping (Priority: MEDIUM)

### 3.1 Research Historical Tournament Names
**Objective**: Map old tournament names to current names

**Tasks**:
1. **Compile Historical Name Changes** (Week 1)
   - Research major tournament name changes:
     - Pacific Life Open → BNP Paribas Open → Indian Wells Masters
     - NASDAQ-100 Open → Sony Ericsson Open → Miami Masters
     - Rogers Masters → Rogers Cup → Toronto/Montreal Masters
     - Other significant name changes
   
2. **Create Historical Mapping Dictionary** (Week 1)
   - New `HISTORICAL_TOURNAMENT_MAPPINGS` dictionary
   - Structure: `{"old_name": "current_name", ...}`
   - Include year ranges if applicable

3. **Update Mapping Function** (Week 2)
   - Add historical name check before fuzzy matching
   - Check historical mappings → resolve to current name → use current mapping

**Deliverables**:
- `HISTORICAL_TOURNAMENT_MAPPINGS` dictionary
- Updated mapping function with historical lookup
- Documentation of name changes

**Estimated Effort**: 1-2 weeks  
**Risk**: Low - straightforward dictionary addition

**Dependencies**: Phase 1

---

## Phase 4: Tournament Alias System (Priority: MEDIUM)

### 4.1 Design Alias Data Structure
**Objective**: Support multiple aliases per tournament

**Tasks**:
1. **Design Alias Structure** (Week 1)
   - Create `TOURNAMENT_ALIASES` dictionary
   - Structure: `{"canonical_name": ["alias1", "alias2", ...], ...}`
   - Include:
     - Common abbreviations (e.g., "US Open" → "USO")
     - Sponsor variations (e.g., "Dubai" → "Dubai Tennis Championships")
     - Location-based names (e.g., "Miami" → "Miami Masters")

2. **Populate Alias Dictionary** (Week 1-2)
   - Add aliases for all mapped tournaments
   - Research common user variations
   - Include multilingual names if applicable

3. **Update Mapping Function** (Week 2)
   - Check aliases before explicit mappings
   - Resolve alias → canonical name → use canonical mapping

**Deliverables**:
- `TOURNAMENT_ALIASES` dictionary
- Updated mapping function with alias resolution
- Documentation

**Estimated Effort**: 1-2 weeks  
**Risk**: Low

**Dependencies**: Phase 1

---

## Phase 5: Database-Driven Mapping (Priority: LOW)

### 5.1 Tournament Name Analysis
**Objective**: Build mappings from actual database patterns

**Tasks**:
1. **Analyze Database Patterns** (Week 1)
   - Query database for tournament name variations
   - Identify patterns (e.g., "Tournament Name" vs "Tournament Name Open")
   - Group similar names by `tourney_id` or location

2. **Generate Mapping Suggestions** (Week 1)
   - Create script to suggest mappings based on:
     - Same location + similar name
     - Same tournament level + similar name
     - Same time period + similar name

3. **Review and Curate** (Week 2)
   - Manual review of generated suggestions
   - Add high-confidence mappings to dictionaries

**Deliverables**:
- Analysis script
- Generated mapping suggestions
- Curated mappings added to dictionaries

**Estimated Effort**: 2 weeks  
**Risk**: Medium - requires manual curation

**Dependencies**: Phase 1, Phase 2

---

## Phase 6: Enhanced Fallback Strategy (Priority: HIGH)

### 6.1 Improve Unknown Tournament Handling
**Objective**: Better handling when explicit mapping fails

**Tasks**:
1. **Database Query Fallback** (Week 1)
   - When mapping returns "unknown":
     - Query database for similar tournament names using `LIKE`
     - Use fuzzy matching on database results
     - Return top 3-5 suggestions

2. **User Disambiguation** (Week 2)
   - If multiple matches found:
     - Return JSON with multiple candidates
     - Include similarity scores
     - Let LLM/agent handle disambiguation

3. **Partial Match Support** (Week 2)
   - Handle partial tournament names:
     - "Dubai" → matches "Dubai Tennis Championships"
     - "Miami" → matches "Miami Masters"
   - Use word-based matching (split by spaces)

**Deliverables**:
- Enhanced `_get_tournament_mapping()` function
- Database query helper functions
- Disambiguation logic
- Updated tool response format

**Estimated Effort**: 2-3 weeks  
**Risk**: Medium - requires database integration

**Dependencies**: Phase 2

---

## Phase 7: Integration & Testing (Priority: HIGH)

### 7.1 Integration Testing
**Objective**: Ensure all improvements work together

**Tasks**:
1. **Unit Tests** (Week 1)
   - Test each mapping function individually
   - Test fuzzy matching accuracy
   - Test historical name resolution
   - Test alias resolution

2. **Integration Tests** (Week 1)
   - Test end-to-end mapping flow
   - Test with real user queries
   - Test performance with large datasets

3. **Performance Optimization** (Week 2)
   - Profile mapping function performance
   - Optimize database queries
   - Cache frequently accessed mappings
   - Consider pre-computing fuzzy matches

**Deliverables**:
- Comprehensive test suite
- Performance benchmarks
- Optimization report

**Estimated Effort**: 2 weeks  
**Risk**: Low

**Dependencies**: All previous phases

---

## Phase 8: Documentation & Monitoring (Priority: MEDIUM)

### 8.1 Documentation
**Objective**: Document new features and usage

**Tasks**:
1. **Update Code Documentation** (Week 1)
   - Document new functions
   - Add docstrings
   - Update type hints

2. **User Documentation** (Week 1)
   - Update prompt documentation
   - Add examples of new features
   - Document fallback behavior

3. **Monitoring Setup** (Week 1)
   - Add logging for mapping failures
   - Track mapping success rates
   - Monitor performance metrics

**Deliverables**:
- Updated documentation
- Monitoring dashboard/metrics
- Usage examples

**Estimated Effort**: 1 week  
**Risk**: Low

**Dependencies**: Phase 7

---

## Implementation Timeline

### Recommended Sequence:
1. **Weeks 1-3**: Phase 1 (Expand Dictionary) + Phase 2 (Fuzzy Matching) - Parallel
2. **Weeks 4-5**: Phase 3 (Historical Names) + Phase 4 (Aliases) - Parallel
3. **Weeks 6-7**: Phase 6 (Enhanced Fallback)
4. **Week 8**: Phase 5 (Database-Driven) - Optional, can run in background
5. **Weeks 9-10**: Phase 7 (Integration & Testing)
6. **Week 11**: Phase 8 (Documentation)

**Total Estimated Time**: 11 weeks (~3 months)

### Quick Wins (Can Start Immediately):
- Phase 1.1: Expand mapping dictionary (2-3 weeks)
- Phase 3: Historical name mapping (1-2 weeks)
- Phase 4: Tournament aliases (1-2 weeks)

These can be done in parallel and provide immediate value.

---

## Success Metrics

### Quantitative:
- **Mapping Coverage**: Increase from 0.13% to 80%+ for top tournaments
- **Query Success Rate**: Increase from ~60% to 90%+ for tournament queries
- **Response Time**: Maintain <100ms for mapping lookups
- **False Positive Rate**: <5% for fuzzy matching

### Qualitative:
- User satisfaction with tournament query results
- Reduction in "unknown tournament" responses
- Better handling of tournament name variations

---

## Risk Assessment

### High Risk:
- **Phase 2 (Fuzzy Matching)**: Performance impact, false positives
  - Mitigation: Use efficient library (rapidfuzz), set appropriate thresholds

### Medium Risk:
- **Phase 6 (Enhanced Fallback)**: Database query overhead
  - Mitigation: Cache results, optimize queries, limit result sets

### Low Risk:
- **Phase 1, 3, 4**: Dictionary expansions
  - Mitigation: Thorough testing, incremental rollout

---

## Resource Requirements

### Development:
- 1 developer (full-time equivalent)
- Access to database for analysis
- Testing environment

### Data:
- Tournament name research (ATP/WTA websites)
- Historical tournament name changes
- User query logs (if available)

### Tools:
- Python libraries: `rapidfuzz` (or similar)
- Database query tools
- Testing framework

---

## Approval Checklist

Before starting implementation, please approve:

- [ ] Overall plan and timeline
- [ ] Phase priorities and sequence
- [ ] Success metrics
- [ ] Resource allocation
- [ ] Risk mitigation strategies
- [ ] Specific phases to start with

---

## Next Steps

1. **Review this plan**
2. **Approve phases to implement**
3. **Prioritize phases** (if not implementing all)
4. **Set timeline** (if different from recommended)
5. **Assign resources**
6. **Begin Phase 1** (Expand Dictionary) - can start immediately

---

## Questions for Discussion

1. Should we implement all phases or prioritize specific ones?
2. What's the target timeline? (Recommended: 3 months)
3. Do we have access to user query logs to prioritize tournaments?
4. Should fuzzy matching be enabled by default or opt-in?
5. What similarity threshold should we use for fuzzy matching? (Recommended: 0.85)
6. Should we cache database queries for performance?
7. How should we handle ambiguous tournament names (multiple matches)?

---

*Document Version: 1.0*  
*Last Updated: 2025-11-07*  
*Author: AI Assistant*

