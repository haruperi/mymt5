# Security Guide

This guide outlines best practices for running MyMT5 securely in production.

## Credentials and Secrets

- Store secrets in environment variables or a secrets manager.
- Never commit secrets to git. Ensure `config.ini` is gitignored.
- Prefer `.env` for local development and a secret store in production.

### Recommended secret keys

- MT5 login, password, server
- Notification tokens (email SMTP password, Telegram bot token)

## Configuration Loading

- Use environment variables to override file-based config at runtime.
- Validate presence of required settings on startup and fail fast.

## Logging Hygiene

- Never log passwords, tokens, magic numbers, or full account numbers.
- Use redaction filters for sensitive fields (e.g., `password`, `token`, `api_key`).
- Enable log rotation and limit retention.

## Least Privilege

- Run as a non-admin user.
- Limit filesystem write access to `logs/` and `data/` only.
- Restrict outbound network to broker endpoints where possible.

## Dependencies

- Pin core runtime dependencies in `requirements.txt`.
- Regularly update security patches.
- Use `pip install --upgrade --require-hashes` (optional).

## Operational Hardening

- Enable watchdog/auto-restart (systemd, PM2, Supervisor, Windows Task Scheduler).
- Health checks: connection state, last successful ping, error rate.
- Implement exponential backoff on reconnect.

## Data Protection

- Avoid storing raw credentials in `data/` or logs.
- If exporting reports, avoid including PII or mask account identifiers.

## Incident Response

- Capture contextual error logs with correlation IDs.
- Keep a minimal crash report (timestamp, version, last action, error).
- Provide a procedure to rotate credentials quickly.

## Checklist

- [ ] Secrets in env/secret store
- [ ] Config validated on startup
- [ ] PII redaction in logs
- [ ] Log rotation enabled
- [ ] Non-admin runtime user
- [ ] Health checks enabled
- [ ] Dependencies up-to-date

---

## .env Template (Optional)

Create a `.env` file next to `config.ini` for local use:

```
MT5_LOGIN=12345678
MT5_PASSWORD=your_password
MT5_SERVER=YourBroker-Demo
# Optional overrides
LOG_LEVEL=INFO
RISK_MAX_PER_TRADE=2.0
```

Load them in your runner (example PowerShell):

```powershell
# Windows PowerShell
$env:MT5_LOGIN=(Get-Content .env | Select-String -Pattern '^MT5_LOGIN=').ToString().Split('=')[1]
```


