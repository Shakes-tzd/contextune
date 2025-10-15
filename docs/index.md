# SlashSense

Natural language to slash command mapping for Claude Code.

## Overview

SlashSense is a Claude Code plugin that intelligently detects user intent from natural language and suggests appropriate slash commands. It uses a 3-tier detection cascade for optimal performance:

1. **Keyword Matching** (Tier 1) - Fast regex-based detection (<0.1ms)
2. **Model2Vec Embeddings** (Tier 2) - Semantic similarity matching (<1ms)
3. **Semantic Router** (Tier 3) - LLM-based intent detection (<100ms)

## Quick Start

```bash
# Install the plugin
/plugin install slashsense

# Try it out with natural language
"can you analyze my code"
# SlashSense detects intent and suggests: /sc:analyze
```

## Features

- **Fast Detection**: Most queries match in <2ms using keyword patterns
- **Smart Fallback**: Cascades to ML models when keywords don't match
- **Customizable**: Add your own patterns and commands
- **Zero Config**: Works out of the box with sensible defaults

## Documentation

- [Installation](getting-started/installation.md) - Get started with SlashSense
- [Usage Guide](user-guide/usage.md) - Learn how to use SlashSense
- [Architecture](architecture/overview.md) - Understand how it works
- [API Reference](api/index.md) - Explore the codebase

## License

MIT License - See [LICENSE](about/license.md) for details.
