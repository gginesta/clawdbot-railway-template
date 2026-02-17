# TMNT Squad QMD Memory Standardization Plan

## Overview
**Objective:** Standardize Memory Search Infrastructure Across TMNT Squad

### Current State Audit
- **Molty (🦎):** Default QMD implementation
- **Leonardo (🔵):** Custom QMD implementation
- **Raphael (🔴):** SQLite-based partial QMD

### Target State
- Unified QMD implementation
- Consistent embedding provider
- Centralized memory architecture
- Efficient indexing and cleanup mechanism

## Standardization Phases

### Phase 1: Preparation and Backup
1. Create comprehensive memory backups
2. Validate existing memory stores
3. Document pre-migration state

### Phase 2: Embedding Provider Configuration
- **Provider:** nomic-ai/nomic-embed-text-v1 (via OpenRouter)
- **Embedding Characteristics:**
  * Dimension: 768
  * Cost: $0.0001 per 1K tokens
  * Open-source
  * Semantic search optimized

### Phase 3: Implementation Standardization
- Develop unified QMD configuration template
- Create migration scripts
- Implement consistent indexing rules

### Phase 4: Central Memory Architecture
- Establish `/data/shared/memory-vault/` as primary shared memory location
- Create standardized metadata tagging system
- Implement version-controlled embedding schema

### Phase 5: Re-Indexing Process
- Staged re-indexing approach
- Parallel processing
- Comprehensive validation checks

### Phase 6: Memory Cleanup and Optimization
- Remove stale memory collections
- Implement retention policy
- Automated cleanup mechanisms

## Risks and Mitigations
1. **Data Loss Risk**
   - Full backups before migration
   - Staged rollout
   - Comprehensive logging

2. **Performance Risks**
   - Monitored re-indexing
   - Fallback mechanisms
   - Performance benchmarking

## Documentation Requirements
- Detailed migration logs
- Configuration snapshots
- Performance metrics
- Rollback procedures

## Open Questions
- Exact embedding dimension preferences
- Specific exclusion rules for sensitive content
- Retention period for historical memories

---

**Prepared by: Molty 🦎 (Fleet Coordinator)**
**Date:** 2026-02-16
**Version:** 0.1-DRAFT