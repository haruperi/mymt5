# Deployment Guide

This document provides a practical reference to deploy MyMT5 to a production host.

## Environments

- Windows 10/11 (recommended for MT5 terminal)
- Optionally Linux/macOS via VM/Wine (requires extra care)

## Files to Prepare

- `config.ini` (from `config.ini.example`)
- `.env` (optional, for overrides)
- `logs/` directory (writable)
- `data/` directory (if storing exports/cache)

## Process Supervisor Options

- Windows Task Scheduler (simple scheduling)
- NSSM (Non-Sucking Service Manager) to run as a service
- Python `pywin32` service (advanced)

### Example: Run on reboot and keep alive (Task Scheduler)

1. Create venv and install package
2. Create a scheduled task:
   - Trigger: At startup
   - Action: `python path\\to\\starter_template.py`
   - Run whether user is logged on or not
   - Retry on failure

## Logging

- Use rotation (daily/size-based)
- Separate `app.log` and `errors.log`
- Do not log secrets

## Monitoring (Lightweight)

- Emit periodic heartbeat lines to logs
- Track connection state (`client.is_connected()`)
- Measure latency for `ping()`
- Optionally push metrics to a timeseries DB/CSV

## Backups

- Backup `config.ini` and logs daily
- Keep last N days (e.g., 7)

## Updates/Rollbacks

- Keep previous wheel in `dist/`
- Version with `mymt5/__version__.py`
- To roll back: reinstall previous wheel

## Minimal Deployment Steps

```powershell
# Windows PowerShell
python -m venv venv
./venv/Scripts/Activate.ps1
pip install -r requirements.txt
pip install dist/mymt5-1.0.0-py3-none-any.whl

# Prepare config
copy config.ini.example config.ini
# Edit config.ini

# Run bot (or your app entrypoint)
python starter_template.py
```

## Production Checklist (Quick)

- [ ] MT5 installed and accessible
- [ ] Valid credentials configured
- [ ] venv created and locked down
- [ ] Logs and data directories writable
- [ ] Rotation configured
- [ ] Supervisor/Task in place
- [ ] Health checks tested
- [ ] Backups scheduled
