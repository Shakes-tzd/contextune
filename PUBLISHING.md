# Publishing Contextune to Claude Code Marketplace

This guide explains how Contextune is published and how users receive updates.

---

## 📦 Publishing Model

Claude Code uses a **decentralized marketplace system**. Unlike centralized app stores, there's no single approval process. Instead:

1. **You host the plugin** on GitHub (or any git service)
2. **You create a marketplace** (a `marketplace.json` file in your repo)
3. **Users add your marketplace** with a single command
4. **Updates are pulled** directly from your repo

---

## 🚀 Initial Publishing Steps

### Step 1: Prepare the Plugin

✅ **Already Done:**
- Created `.claude-plugin/plugin.json` with version `0.1.0`
- Created `.claude-plugin/marketplace.json`
- Added MIT LICENSE
- Created comprehensive README.md
- Documented all commands
- Added all 26 command mappings

### Step 2: Tag a Release

```bash
# Update version in both files
# plugin.json: "version": "0.1.0"
# marketplace.json: "version": "0.1.0"

# Commit all changes
git add .
git commit -m "release: v0.1.0 - initial beta release"

# Create git tag
git tag -a v0.1.0 -m "v0.1.0: Initial beta release with parallel workflow support"

# Push to GitHub
git push origin master
git push origin v0.1.0
```

### Step 3: Verify on GitHub

Go to: https://github.com/Shakes-tzd/contextune

Ensure these files are present:
- `.claude-plugin/plugin.json` ✓
- `.claude-plugin/marketplace.json` ✓
- `LICENSE` ✓
- `README.md` ✓
- All command files in `commands/` ✓

### Step 4: Test Installation

```bash
# Test direct installation
/plugin install Shakes-tzd/contextune

# Test marketplace installation
/plugin marketplace add Shakes-tzd/contextune
/plugin install contextune
```

---

## 🌐 Submit to Community Marketplace

The community maintains an aggregator at **claudecodemarketplace.com** (115+ marketplaces).

### Submit Your Marketplace

1. **Fork the community repo:**
   ```bash
   # Go to: https://github.com/joesaunderson/claude-code-marketplace
   # Click "Fork"
   ```

2. **Add your marketplace to the list:**
   ```bash
   # Clone your fork
   git clone https://github.com/Shakes-tzd/claude-code-marketplace
   cd claude-code-marketplace

   # Add your marketplace (follow their format)
   # Edit the appropriate file
   ```

3. **Submit Pull Request:**
   - Title: "Add Contextune marketplace"
   - Description: Brief overview of plugin features
   - Link to your repo

4. **Wait for approval:**
   - Community maintainers review
   - Usually approved within 1-2 days
   - Once merged, your marketplace appears on claudecodemarketplace.com

---

## 🔄 Releasing Updates

### Semantic Versioning

Follow [SemVer](https://semver.org/):

**Pre-1.0 (Beta Phase):**
- `0.1.0` → `0.1.1`: Patch (bug fixes)
- `0.1.0` → `0.2.0`: Minor (new features, may have breaking changes)
- `0.x.x` → `1.0.0`: Major (first stable release)

**Post-1.0 (Stable):**
- `1.0.0` → `1.0.1`: Patch (bug fixes)
- `1.0.0` → `1.1.0`: Minor (new features, backward compatible)
- `1.0.0` → `2.0.0`: Major (breaking changes)

**Note:** In pre-1.0 versions (0.x.x), breaking changes are allowed without major version bump. This is the **beta period** where we gather user feedback and stabilize the API.

### When to Release v1.0.0

Only release v1.0.0 when:
- ✅ Plugin has been tested by multiple users
- ✅ No major bugs reported for 2+ weeks
- ✅ API/hook interface is stable (no breaking changes planned)
- ✅ Performance validated at scale
- ✅ Command mappings proven accurate
- ✅ Documentation complete and accurate
- ✅ Confidence threshold is well-calibrated

**Estimated timeline:** 1-3 months of beta testing

### Roadmap to v1.0.0

```
v0.1.0 → Initial beta release (current)
v0.2.0 → Bug fixes + user feedback incorporated
v0.3.0 → Performance optimizations
v0.4.0 → Additional command mappings
v0.9.0 → Release candidate (feature freeze)
v1.0.0 → Stable release (API locked)
```

### Update Process

**1. Make your changes**
```bash
# Develop new feature
# Update tests
# Update documentation
```

**2. Update version numbers**
```bash
# Edit .claude-plugin/plugin.json
{
  "version": "1.1.0"
}

# Edit .claude-plugin/marketplace.json
{
  "version": "1.1.0",
  "plugins": [
    {
      "name": "contextune",
      "version": "1.1.0"
    }
  ]
}
```

**3. Update CHANGELOG**
```bash
# Create/update CHANGELOG.md
## [1.1.0] - 2025-10-15

### Added
- New feature X
- New command Y

### Fixed
- Bug Z

### Changed
- Improved performance of A
```

**4. Commit and tag**
```bash
git add .
git commit -m "release: v1.1.0 - add feature X"
git tag -a v1.1.0 -m "v1.1.0: Add feature X"
git push origin main
git push origin v1.1.0
```

**5. Create GitHub Release**
```bash
# Via GitHub CLI
gh release create v1.1.0 \
  --title "v1.1.0: Add feature X" \
  --notes "See CHANGELOG.md for details"

# Or via GitHub web UI:
# https://github.com/Shakes-tzd/contextune/releases/new
```

---

## 🔔 How Users Get Updates

### Automatic Update Checking

Claude Code automatically checks for plugin updates:
- Checks when user runs `/plugin list`
- Checks when user runs `/plugin update`
- Checks periodically (implementation dependent)

### Manual Update

Users can update with:
```bash
# Update specific plugin
/plugin update contextune

# Update all plugins
/plugin update --all
```

### Version Pinning

Users can pin to specific versions:
```bash
# Install specific version
/plugin install Shakes-tzd/contextune@1.0.0

# Upgrade to new version
/plugin install Shakes-tzd/contextune@1.1.0
```

---

## 📊 Monitoring Adoption

### GitHub Insights

Track plugin adoption via GitHub:
- **Stars**: Popularity indicator
- **Forks**: Developers extending your work
- **Clone Count**: Installation attempts
- **Traffic**: Views and clones over time

Access at: https://github.com/Shakes-tzd/contextune/graphs/traffic

### Community Feedback

Monitor these channels:
- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: User questions and showcase
- **claudecodemarketplace.com**: Ranking and visibility

---

## 🎯 Best Practices

### Documentation

- ✅ Maintain comprehensive README
- ✅ Document all commands
- ✅ Include usage examples
- ✅ Provide troubleshooting guide
- ✅ Keep CHANGELOG updated

### Communication

- Announce releases in GitHub Releases
- Tag breaking changes clearly
- Provide migration guides for major versions
- Respond to issues promptly

### Testing

Before each release:
```bash
# Run tests
uv run pytest

# Lint code
uv run ruff check .

# Type check
uv run mypy lib/

# Test installation
/plugin uninstall contextune
/plugin install @local
```

### Versioning Strategy

- **Patch (1.0.x)**: Bug fixes, every 1-2 weeks
- **Minor (1.x.0)**: New features, every 1-2 months
- **Major (x.0.0)**: Breaking changes, rarely (6+ months)

---

## 🚨 Breaking Changes

If you need to make breaking changes:

1. **Announce in advance** (GitHub Discussions)
2. **Document migration path** (MIGRATION.md)
3. **Bump major version** (1.x.x → 2.0.0)
4. **Provide deprecation warnings** (in v1.x)
5. **Support old version** (for transition period)

Example deprecation:
```javascript
// In v1.9.0 (before breaking change)
console.warn("⚠️  /old-command is deprecated. Use /new-command instead. Support will be removed in v2.0.0")
```

---

## 📝 Release Checklist

Before each release:

- [ ] Update version in `plugin.json`
- [ ] Update version in `marketplace.json`
- [ ] Update `CHANGELOG.md`
- [ ] Run full test suite
- [ ] Update documentation
- [ ] Test local installation
- [ ] Commit changes
- [ ] Create git tag
- [ ] Push to GitHub
- [ ] Create GitHub Release
- [ ] Test marketplace installation
- [ ] Announce on relevant channels

---

## 🔗 Useful Links

- **Contextune Repository**: https://github.com/Shakes-tzd/contextune
- **Community Marketplace**: https://claudecodemarketplace.com/
- **Submit Marketplace**: https://github.com/joesaunderson/claude-code-marketplace
- **Claude Code Docs**: https://docs.claude.com/en/docs/claude-code/plugin-marketplaces
- **SemVer**: https://semver.org/

---

## 🆘 Troubleshooting

### "Plugin not found"

- Ensure `plugin.json` exists in `.claude-plugin/`
- Check GitHub repo is public
- Verify tag exists: `git tag -l`

### "Version mismatch"

- Ensure versions match in both JSON files
- Push tags: `git push --tags`

### "Update not appearing"

- Users need to run `/plugin update contextune`
- Check git tag created and pushed
- Clear plugin cache (implementation dependent)

---

## 🎉 You're Ready!

Your plugin is now ready for the marketplace. Users can install it with:

```bash
/plugin marketplace add Shakes-tzd/contextune
/plugin install contextune
```

Or directly:

```bash
/plugin install Shakes-tzd/contextune
```

Updates will be pulled automatically from your GitHub repo when you push new tagged versions!
