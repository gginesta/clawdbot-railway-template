# HEARTBEAT.md

## Heartbeat Check
Run the script: `bash /data/workspace/scripts/heartbeat-check.sh`

The script handles:
1. Usage report
2. Agent-link health update
3. April health check
4. MC inbox task count

## Response Rules (REG-034)
- Script outputs `HEARTBEAT_OK` → reply ONLY: `HEARTBEAT_OK`
- Script outputs alerts → send alerts to Guillermo, then reply `HEARTBEAT_OK`
- **DO NOT** add briefings, status cards, calendar, weather, or any other content
- **DO NOT** fabricate data you didn't query
- Adding anything after `HEARTBEAT_OK` = regression failure
