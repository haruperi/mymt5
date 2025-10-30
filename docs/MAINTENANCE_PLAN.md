# Maintenance Plan

Guidelines for ongoing maintenance of MyMT5 in production.

## Routine Tasks (Weekly)

- Review logs for errors/warnings
- Update dependencies (patch versions)
- Verify connection stability and latency
- Sanity-check risk limits and account health

## Routine Tasks (Monthly)

- Full dependency audit and updates
- Rotate credentials (where policy requires)
- Backup review and restoration drill
- Review performance and optimize hotspots

## Incident Response

- Triage: identify scope and impact
- Collect logs and recent changes
- Mitigate by stopping strategy if needed
- Recover: rollback package/version if necessary
- Postmortem: document cause and action items

## Versioning & Releases

- Semantic versioning (MAJOR.MINOR.PATCH)
- Update `mymt5/__version__.py` and CHANGELOG.md
- Tag releases in Git
- Use Test PyPI before production PyPI

## Monitoring & Alerts (Optional)

- Error rate thresholds
- Consecutive reconnection failures
- Heartbeat missing for N minutes
- Equity drawdown beyond threshold

