---
name: ss:intents
description: Configure SlashSense intent detection settings
executable: commands/slashsense-config.py
---

# SlashSense Intent Detection Settings

Configure intent detection settings and custom command mappings.

## Usage
`/ss:intents`

This opens `~/.claude/plugins/slashsense/data/user_patterns.json` where you can:

- Add custom command mappings
- Adjust confidence thresholds
- Enable/disable detection tiers
- View detection statistics

## Configuration Options
```json
{
  "enabled": true,
  "confidence_threshold": 0.7,
  "tiers": {
    "keyword": true,
    "model2vec": true,
    "semantic_router": true
  },
  "custom_mappings": {
    "make it pretty": "/sc:improve",
    "ship it": "/sc:git"
  }
}
```