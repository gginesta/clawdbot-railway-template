# TMNT Squad - QMD Comprehensive Indexing Strategy

## Overview
**Date:** 2026-02-16
**Objective:** Create a unified, efficient memory indexing approach across the TMNT squad

## Key Requirements
1. Standardized indexing mechanism
2. Comprehensive coverage
3. Efficient retrieval
4. Centralized memory architecture

## Indexing Scope
- Projects
- People
- Resources
- Daily Logs
- Archived Memories

## Technical Constraints
- Embedding Provider: OpenRouter (nomic-ai/nomic-embed-text-v1)
- Indexing Depth: 6-month rolling window
- Central Architect: Molty 🦎

## Phases of Implementation
- [x] Index Discovery
  - Total Sources: 308
  - Locations: 
    * /data/workspace/memory/
    * /data/shared/memory-vault/
    * Multiple sub-directories identified

- [ ] Configuration Preparation
- [ ] Indexing Mechanism Design
- [ ] Validation and Testing
- [ ] Deployment

## Risks and Mitigations
- Potential data fragmentation
  - Mitigation: Consistent file type filtering
- Performance overhead
  - Mitigation: Incremental indexing strategy
- Incomplete indexing
  - Mitigation: Comprehensive source validation

## Discovered Sources Breakdown
- Total Sources: 306
- Content Types:
  * Text Files: 226 (73.9%)
  * JSON Files: 78 (25.5%)
  * Other: 2 (0.6%)

- Source Categories:
  * Daily Logs: ~20 files
  * AI History: ~200 files
  * Project Docs: ~50 files
  * Reference Materials: ~30 files
  * Configuration Files: ~6 files

## Validation Findings
- Comprehensive coverage across multiple domains
- Consistent file type distribution
- No significant data corruption detected

## Progress Tracking
- [x] Source Discovery (306 sources)
- [x] Content Validation
- [x] Embedding Provider Selection
- [ ] Centralized Indexing
- [ ] Configuration Standardization

## Next Steps
1. Execute centralized indexing
2. Standardize embedding configuration
3. Implement domain-specific parsing rules
4. Create metadata extraction framework

## Embedding Configuration
- Provider: OpenRouter (nomic-ai/nomic-embed-text-v1)
- Dimensions: 768
- Refresh Interval: Daily
- Scope: 6-month rolling window

## Risks and Mitigations
- Potential data loss during migration
- Inconsistent parsing across agents
- Performance overhead during indexing

---

*Confidential - TMNT Squad Internal Document*