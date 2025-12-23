#!/usr/bin/env python3
"""Configuration loader for unified Contextune-HtmlGraph config."""

import sys
from pathlib import Path
from typing import Optional

import yaml
from pydantic import ValidationError

from .config import UnifiedConfig


class ConfigLoader:
    """Load and validate unified configuration."""

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize config loader.

        Args:
            config_path: Path to config file. If None, uses default (~/.contextune-config.yaml)
        """
        self.config_path = config_path or UnifiedConfig.get_default_path()
        self._config: Optional[UnifiedConfig] = None

    def load(self, create_if_missing: bool = False) -> UnifiedConfig:
        """Load configuration from file.

        Args:
            create_if_missing: Create default config if file doesn't exist

        Returns:
            Loaded UnifiedConfig

        Raises:
            FileNotFoundError: If config file doesn't exist and create_if_missing=False
            ValidationError: If config file is invalid
        """
        if not self.config_path.exists():
            if create_if_missing:
                return self.create_default()
            raise FileNotFoundError(
                f"Config file not found: {self.config_path}\n"
                f"Run 'contextune config init' to create default config"
            )

        try:
            with open(self.config_path) as f:
                data = yaml.safe_load(f)

            if data is None:
                # Empty file - use defaults
                self._config = UnifiedConfig()
            else:
                self._config = UnifiedConfig(**data)

            return self._config

        except yaml.YAMLError as e:
            print(f"❌ Invalid YAML in {self.config_path}:", file=sys.stderr)
            print(f"   {e}", file=sys.stderr)
            raise
        except ValidationError as e:
            print(f"❌ Invalid config in {self.config_path}:", file=sys.stderr)
            print(f"   {e}", file=sys.stderr)
            raise

    def create_default(self) -> UnifiedConfig:
        """Create default config file.

        Returns:
            Default UnifiedConfig
        """
        # Ensure parent directory exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        # Create default config
        config = UnifiedConfig()

        # Write to file
        self.save(config)

        print(f"✅ Created default config: {self.config_path}", file=sys.stderr)
        return config

    def save(self, config: UnifiedConfig) -> None:
        """Save configuration to file.

        Args:
            config: UnifiedConfig to save
        """
        # Convert to dict, converting Path objects to strings
        data = config.model_dump(mode='json')  # Use 'json' mode to convert Path to str

        with open(self.config_path, 'w') as f:
            # Write with comments
            f.write("# Unified Contextune-HtmlGraph Configuration\n")
            f.write("# Auto-generated - edit as needed\n\n")
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)

        self._config = config

    def validate(self) -> tuple[bool, list[str]]:
        """Validate config file.

        Returns:
            Tuple of (is_valid, errors)
        """
        errors = []

        if not self.config_path.exists():
            errors.append(f"Config file not found: {self.config_path}")
            return False, errors

        try:
            self.load()
            return True, []
        except yaml.YAMLError as e:
            errors.append(f"Invalid YAML: {e}")
            return False, errors
        except ValidationError as e:
            for error in e.errors():
                loc = " -> ".join(str(x) for x in error['loc'])
                msg = error['msg']
                errors.append(f"{loc}: {msg}")
            return False, errors

    @property
    def config(self) -> UnifiedConfig:
        """Get loaded config, loading if necessary."""
        if self._config is None:
            self._config = self.load(create_if_missing=True)
        return self._config


# Global config instance
_global_config: Optional[ConfigLoader] = None


def get_config(config_path: Optional[Path] = None) -> UnifiedConfig:
    """Get global config instance.

    Args:
        config_path: Optional path to config file

    Returns:
        UnifiedConfig instance
    """
    global _global_config

    if _global_config is None or (config_path and config_path != _global_config.config_path):
        _global_config = ConfigLoader(config_path)

    return _global_config.config


def reload_config() -> UnifiedConfig:
    """Reload config from disk.

    Returns:
        Reloaded UnifiedConfig
    """
    global _global_config

    if _global_config is None:
        _global_config = ConfigLoader()

    _global_config._config = None  # Clear cached config
    return _global_config.load(create_if_missing=True)


if __name__ == "__main__":
    # Self-test
    import tempfile

    print("Testing ConfigLoader...")

    with tempfile.TemporaryDirectory() as tmpdir:
        test_path = Path(tmpdir) / "test-config.yaml"

        # Test 1: Create default config
        loader = ConfigLoader(test_path)
        config = loader.create_default()
        assert test_path.exists()
        print("✅ Default config creation works")

        # Test 2: Load config
        loaded = loader.load()
        assert loaded.integration.enabled == True
        print("✅ Config loading works")

        # Test 3: Validation
        is_valid, errors = loader.validate()
        assert is_valid
        assert len(errors) == 0
        print("✅ Config validation works")

        # Test 4: Modify and save
        config.htmlgraph.dashboard.port = 9090
        loader.save(config)
        reloaded = ConfigLoader(test_path).load()
        assert reloaded.htmlgraph.dashboard.port == 9090
        print("✅ Config modification and reload works")

        # Test 5: Invalid config
        with open(test_path, 'w') as f:
            f.write("invalid: yaml: content:")
        is_valid, errors = loader.validate()
        assert not is_valid
        assert len(errors) > 0
        print("✅ Invalid YAML detection works")

    print("\n✅ All ConfigLoader tests passed!")
