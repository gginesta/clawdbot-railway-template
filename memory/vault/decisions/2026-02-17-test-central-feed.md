<!-- agent: molty | type: decision | priority: P2 | date: 2026-02-17 -->
# Test: Central Feed Verification

This is a test file to verify the shared vault → Molty QMD indexing pipeline.

## Test Criteria
1. File appears in Syncthing sync on all agents
2. Molty's QMD indexes it within 5 minutes
3. `memory_search("central feed verification test")` returns this file
4. Clean up after verification

## Unique Search Term
CENTRAL_FEED_CANARY_2026_02_17
