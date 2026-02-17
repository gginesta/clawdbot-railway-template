# TMNT Delivery Architecture Specification

## Purpose
Define precise rules for message routing, model selection, and delivery across different surfaces.

## Surface Definitions
1. **Telegram**: Text-only surface
   - No image support
   - Strict text message routing
   - Maximum message length: 4096 characters

2. **Webchat**: Mixed-mode surface
   - Supports text and limited media
   - Flexible routing
   - Requires strict error handling

3. **Discord**: Team communication surface
   - Full media support
   - Used for internal notifications
   - Supports rich formatting

## Model Routing Rules
- **Primary Model**: Claude Opus 4.6
- **Fallback Chain**:
  1. Anthropic Sonnet 4
  2. Google Gemini Flash
  3. GLM-5 (text-only)

### Surface-Specific Routing Constraints
- Telegram: Text models only
- Webchat: Mixed-mode models
- Discord: Any model

## Delivery Context Validation
- Mandatory `channel:` prefix for all routing
- Explicit surface type in delivery configuration
- Pre-flight compatibility checks required

## Error Handling
- 3 consecutive errors → auto-isolate surface
- Require manual intervention for re-enablement
- Detailed logging of routing attempts