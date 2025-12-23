---
name: contextune:config
description: Manage unified Contextune-HtmlGraph configuration
---

# Contextune Configuration Management

Manage the unified `.contextune-config.yaml` configuration file for both Contextune and HtmlGraph.

## Commands

### Initialize Configuration

Create a new default configuration file:

```bash
uv run python -c "
from lib.contextune_integration.config_loader import ConfigLoader
from pathlib import Path

loader = ConfigLoader()
config = loader.create_default()

print(f'✅ Created config: {loader.config_path}')
print(f'   Edit the file to customize settings')
"
```

Creates `~/.contextune-config.yaml` with default values.

### Show Current Configuration

Display the current configuration:

```bash
uv run python -c "
from lib.contextune_integration.config_loader import get_config
import yaml

config = get_config()
data = config.model_dump(mode='json')

print('Current Configuration:')
print('=' * 50)
print(yaml.dump(data, default_flow_style=False, sort_keys=False))
print('=' * 50)
print(f'Config file: {config.get_default_path()}')
"
```

### Validate Configuration

Check if your configuration file is valid:

```bash
uv run python -c "
from lib.contextune_integration.config_loader import ConfigLoader

loader = ConfigLoader()
is_valid, errors = loader.validate()

if is_valid:
    print('✅ Configuration is valid')
else:
    print('❌ Configuration has errors:')
    for error in errors:
        print(f'   - {error}')
"
```

### Reload Configuration

Reload configuration from disk (useful after manual edits):

```bash
uv run python -c "
from lib.contextune_integration.config_loader import reload_config

config = reload_config()
print('✅ Configuration reloaded')
print(f'   Integration enabled: {config.integration.enabled}')
print(f'   Auto-create tracks: {config.htmlgraph.tracking.auto_create_tracks}')
"
```

## Configuration Structure

### Contextune Section

```yaml
contextune:
  intent_detection:
    keyword_threshold: 1.0        # Exact match for keywords
    model2vec_threshold: 0.85     # Model2Vec similarity
    semantic_threshold: 0.7       # Semantic Router confidence
    enable_haiku_analysis: true   # Enable Haiku interactive analysis

  parallel_execution:
    max_agents: 5                 # Maximum parallel agents
    default_model: haiku          # Default model (haiku|sonnet|opus)
    timeout_minutes: 30           # Execution timeout

  data_dir: ~/.claude/plugins/contextune/data  # Contextune data directory
```

### HtmlGraph Section

```yaml
htmlgraph:
  tracking:
    auto_create_tracks: true      # Create tracks from /ctx:plan
    auto_link_features: true      # Link features to tracks
    auto_start_features: true     # Start features on /ctx:execute
    track_all_sessions: true      # Track all Claude sessions

  dashboard:
    port: 8080                    # Dashboard port
    host: localhost               # Dashboard host
    show_contextune_metrics: true # Show Contextune data
    auto_reload: true             # Auto-reload on changes

  data_dir: .htmlgraph            # HtmlGraph data directory
```

### Integration Section

```yaml
integration:
  enabled: true                   # Enable integration
  shared_data_dir: ~/.contextune-htmlgraph  # Shared data
  log_level: INFO                 # Logging level (DEBUG|INFO|WARNING|ERROR)
  sync_interval_seconds: 60       # Sync interval
```

## Common Use Cases

### Disable Integration

To temporarily disable integration:

```yaml
integration:
  enabled: false
```

### Change Dashboard Port

If port 8080 is in use:

```yaml
htmlgraph:
  dashboard:
    port: 8081  # Or any available port
```

### Increase Parallel Agents

For faster execution with more resources:

```yaml
contextune:
  parallel_execution:
    max_agents: 10  # Up to 10 parallel agents
```

### Change Detection Thresholds

To make intent detection more/less strict:

```yaml
contextune:
  intent_detection:
    model2vec_threshold: 0.9  # More strict (fewer false positives)
    # OR
    model2vec_threshold: 0.75 # Less strict (more detections)
```

## Troubleshooting

### Config Not Found

If you get "Config file not found":

1. Run initialization command to create default config
2. Or specify custom path in your code

### Invalid YAML

If validation fails with "Invalid YAML":

1. Check for correct indentation (use spaces, not tabs)
2. Ensure all strings are properly quoted if they contain special characters
3. Run validation command to see specific errors

### Integration Not Working

If integration isn't working despite `enabled: true`:

1. Check that both Contextune and HtmlGraph plugins are installed
2. Verify data directories exist and are writable
3. Check log output for errors
4. Try reloading configuration

## Configuration Priority

Configuration is loaded in this order (first found wins):

1. Custom path (if specified in code)
2. `~/.contextune-config.yaml` (unified config)
3. Project-specific configs (fallback)
4. Default values (hardcoded)

## Example: Programmatic Access

Use configuration in your Python code:

```python
from lib.contextune_integration.config_loader import get_config

# Get config
config = get_config()

# Access settings
if config.integration.enabled:
    if config.htmlgraph.tracking.auto_create_tracks:
        # Auto-create HtmlGraph track
        pass

# Get specific values
port = config.htmlgraph.dashboard.port
max_agents = config.contextune.parallel_execution.max_agents
```

## See Also

- `/ctx:plan` - Parallel planning (uses config settings)
- `/ctx:execute` - Parallel execution (uses config settings)
- `htmlgraph serve` - Dashboard (uses port from config)
