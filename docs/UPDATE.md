# Plugin Update Guide

## Quick Answer

**Q: Will Parliament of Chaos update automatically?**

**A: No.** Claude Code does not automatically update plugins. You must manually update when new versions are released.

---

## How to Update

### Simple Update Command

```
claude plugin update parliament-of-chaos@parliament-of-chaos
```

Run this command in Claude Code to update to the latest version.

---

## Update Process Explained

### Step-by-Step

1. **Check for Updates**
   - Visit: https://github.com/JackScammell/Parliament-Of-Chaos
   - Look for new release tags or version changes
   - Check release notes for new features

2. **Run Update Command**
   ```
   claude plugin update parliament-of-chaos@parliament-of-chaos
   ```
   
3. **Verify Update**
   ```
   /list-agents
   ```
   Check that new agents (if any) appear in the list

### What Happens During Update

When you run the update command:

✅ **Updated:**
- All agent files in `agents/`
- All command files in `commands/`
- Plugin metadata in `.claude-plugin/`

✅ **Preserved:**
- Your project files in `.project-files/`
- Your roadmaps and planning documents
- Custom hooks in `.claude/hooks/`
- Your settings in `.claude/settings.json` and `.claude/settings.local.json`

---

## Update FAQs

### Does Claude Code auto-update plugins on startup?

**No.** Claude Code does not check for or install plugin updates automatically. This is by design to ensure stability and predictability in your development environment.

### How do I know when an update is available?

**Option 1: GitHub Watch**
- Star the repository on GitHub
- Enable "Watch" notifications for releases

**Option 2: Manual Check**
- Periodically visit: https://github.com/JackScammell/Parliament-Of-Chaos
- Check the releases page
- Review the CHANGELOG

**Option 3: Check Version**
```bash
# Your installed version
cat .claude-plugin/marketplace.json | grep version

# Latest version on GitHub
curl -s https://raw.githubusercontent.com/JackScammell/Parliament-Of-Chaos/main/.claude-plugin/marketplace.json | grep version
```

### Do I need to restart Claude Code after updating?

**No.** Changes take effect immediately. However, if you encounter any issues:
1. Try running a command to verify it works
2. If problems persist, restart your Claude Code session

### Will updating break my existing projects?

**No.** Updates only modify the plugin's agent and command files. Your project-specific files are never touched:
- Project outlines and roadmaps remain unchanged
- Work-in-progress tasks are preserved
- Custom configurations persist

### Can I rollback to a previous version?

**Yes, manually:**

1. **Uninstall current version:**
   ```bash
   rm -rf agents
   rm -rf commands
   rm -rf .claude-plugin
   ```

2. **Install specific version:**
   - Download the specific version's ZIP from GitHub releases
   - Extract to your project directory
   - Or use git to checkout a specific tag

**Note:** There's no built-in rollback command in Claude Code.

### How often should I update?

**Recommended update schedule:**

- **Check monthly** - For regular maintenance and improvements
- **Check before major projects** - To get latest features
- **Check after bug reports** - If you've encountered issues
- **Check for security updates** - When announced

**When NOT to update:**
- In the middle of critical project work
- If current version is working perfectly for your needs
- Just before important deadlines (update after)

### What if the update fails?

**If the update command fails:**

1. **Check your internet connection**
   - Ensure you can access GitHub

2. **Verify the repository exists**
   - Visit: https://github.com/JackScammell/Parliament-Of-Chaos
   - Ensure it's accessible

3. **Try again**
   ```
   claude plugin update parliament-of-chaos@parliament-of-chaos
   ```

4. **Manual installation**
   - Download the repository as ZIP
   - Extract to your project
   - Copy `.claude/` directories to your project

5. **Check Claude Code version**
   - Ensure your Claude Code client is up to date
   - Some plugin features require specific Claude Code versions

---

## Version History

To see what's changed between versions:

1. **View on GitHub:**
   - https://github.com/JackScammell/Parliament-Of-Chaos/releases

2. **View locally:**
   ```bash
   git log --oneline
   ```

---

## Getting Help

**If you have update-related questions:**

1. Check this document first
2. Review the [Installation Guide](installation.md)
3. Check the repository's Issues page
4. Create a new issue if your question isn't answered

---

## Related Documentation

- [Installation Guide](installation.md) - Initial setup instructions
- [Usage Guide](usage.md) - How to use commands and agents
- [Hooks Guide](hooks.md) - Custom automation setup

---

## Summary

**Remember:**
- ❌ No automatic updates
- ✅ Manual update required via `claude plugin update`
- ✅ Your project files are safe during updates
- ✅ Updates take effect immediately
- ✅ You control when to update
