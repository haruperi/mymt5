# Production Checklist

A concise checklist to validate MyMT5 is production-ready on a host.

## Pre-Deployment

- [ ] MT5 terminal installed and updated
- [ ] Demo/live account credentials verified in MT5 GUI
- [ ] Python 3.8+ installed
- [ ] Virtual environment created

## Configuration

- [ ] `config.ini` created from `config.ini.example`
- [ ] Secrets not committed to Git
- [ ] Environment overrides (.env or secret store) configured (optional)
- [ ] Risk limits set (RISK section)

## Logging & Monitoring

- [ ] Log rotation in place
- [ ] PII redaction filter applied
- [ ] Heartbeat logs enabled
- [ ] Connection health checks validated

## Security

- [ ] Non-admin runtime user
- [ ] Least filesystem privileges
- [ ] Firewall/network rules reviewed
- [ ] Dependencies scanned/updated

## Operations

- [ ] Supervisor/Task configured (auto-restart)
- [ ] Crash handling emits context
- [ ] Daily backups of logs and config
- [ ] Rollback plan documented

## Validation

- [ ] Dry run with demo account completed
- [ ] Error handling paths exercised
- [ ] Recovery from forced disconnect tested
- [ ] Stop/Start procedures documented

