## Description

<!-- What does this PR change and why? Link the related issue: Fixes #123 -->

## Type of change

- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Refactor (no behavior change)
- [ ] Documentation only

## How was this tested?

<!-- Describe what you ran. Example: opened the GUI, saved settings, verified
%APPDATA%\StockbitDiscordPresence\config.json; ran stockbit_rpc.pyw with the
console while Stockbit Desktop was open/closed. -->

## Checklist

- [ ] `CLIENT_ID` in `backend/presence.py` is unchanged
- [ ] The unaffiliated disclaimer (GUI footer / README) is preserved
- [ ] The GUI still does not open a second Discord IPC connection
- [ ] Error messages name the real dependency (no vague failures)
- [ ] README updated if user-facing behavior or structure changed
- [ ] Tested on Windows with the Discord desktop app installed
