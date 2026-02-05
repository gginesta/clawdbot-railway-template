#!/bin/bash
# Google Calendar API helper for Molty
# Usage: calendar.sh [command] [args]
#
# Commands:
#   list                          - List all calendars
#   events [calendar_id] [days]   - List events (default: primary, 7 days)
#   today [calendar_id]           - Today's events
#   week [calendar_id]            - This week's events
#   add <calendar_id> <summary> <start> <end> [description] [visibility]
#                                 - Add event (visibility: default|private)
#   busy <calendar_id> <start> <end> [summary]
#                                 - Add busy/private block
#   move <event_id> <calendar_id> <new_start> <new_end>
#                                 - Move/reschedule event
#   delete <event_id> <calendar_id>
#                                 - Delete event
#   freebusy <calendar_ids> <start> <end>
#                                 - Check free/busy across calendars
#   refresh                       - Refresh OAuth token

CREDS_FILE="/data/workspace/credentials/gmail-tokens.json"
OAUTH_FILE="/data/workspace/credentials/google-oauth.json"
CALENDAR_CONFIG="/data/workspace/credentials/calendar-config.json"

# Read tokens
ACCESS_TOKEN=$(grep -o '"access_token": "[^"]*"' "$CREDS_FILE" | cut -d'"' -f4)
REFRESH_TOKEN=$(grep -o '"refresh_token": "[^"]*"' "$CREDS_FILE" | cut -d'"' -f4)
CLIENT_ID=$(grep -o '"client_id": "[^"]*"' "$OAUTH_FILE" | head -1 | cut -d'"' -f4)
CLIENT_SECRET=$(grep -o '"client_secret": "[^"]*"' "$OAUTH_FILE" | head -1 | cut -d'"' -f4)

CALENDAR_API="https://www.googleapis.com/calendar/v3"

# Refresh access token
refresh_token() {
    RESPONSE=$(curl -s -X POST https://oauth2.googleapis.com/token \
        -d "client_id=$CLIENT_ID" \
        -d "client_secret=$CLIENT_SECRET" \
        -d "refresh_token=$REFRESH_TOKEN" \
        -d "grant_type=refresh_token")
    
    NEW_TOKEN=$(echo "$RESPONSE" | grep -o '"access_token": "[^"]*"' | cut -d'"' -f4)
    
    if [ -n "$NEW_TOKEN" ]; then
        sed -i "s|\"access_token\": \"[^\"]*\"|\"access_token\": \"$NEW_TOKEN\"|" "$CREDS_FILE"
        ACCESS_TOKEN="$NEW_TOKEN"
        echo "Token refreshed" >&2
    else
        echo "Failed to refresh token: $RESPONSE" >&2
        return 1
    fi
}

# API call with auto-refresh
api_call() {
    local METHOD="$1"
    local URL="$2"
    local DATA="$3"
    
    if [ "$METHOD" = "GET" ]; then
        RESPONSE=$(curl -s -w "\n%{http_code}" "$URL" \
            -H "Authorization: Bearer $ACCESS_TOKEN")
    elif [ "$METHOD" = "DELETE" ]; then
        RESPONSE=$(curl -s -w "\n%{http_code}" -X DELETE "$URL" \
            -H "Authorization: Bearer $ACCESS_TOKEN")
    else
        RESPONSE=$(curl -s -w "\n%{http_code}" -X "$METHOD" "$URL" \
            -H "Authorization: Bearer $ACCESS_TOKEN" \
            -H "Content-Type: application/json" \
            -d "$DATA")
    fi
    
    HTTP_CODE=$(echo "$RESPONSE" | tail -1)
    BODY=$(echo "$RESPONSE" | sed '$d')
    
    if [ "$HTTP_CODE" = "401" ]; then
        refresh_token
        if [ "$METHOD" = "GET" ]; then
            RESPONSE=$(curl -s -w "\n%{http_code}" "$URL" \
                -H "Authorization: Bearer $ACCESS_TOKEN")
        elif [ "$METHOD" = "DELETE" ]; then
            RESPONSE=$(curl -s -w "\n%{http_code}" -X DELETE "$URL" \
                -H "Authorization: Bearer $ACCESS_TOKEN")
        else
            RESPONSE=$(curl -s -w "\n%{http_code}" -X "$METHOD" "$URL" \
                -H "Authorization: Bearer $ACCESS_TOKEN" \
                -H "Content-Type: application/json" \
                -d "$DATA")
        fi
        HTTP_CODE=$(echo "$RESPONSE" | tail -1)
        BODY=$(echo "$RESPONSE" | sed '$d')
    fi
    
    echo "$BODY"
}

# Format datetime for display (expects ISO format)
format_time() {
    echo "$1" | sed 's/T/ /; s/:00+.*//; s/:00Z//'
}

case "${1:-help}" in
    list)
        api_call GET "$CALENDAR_API/users/me/calendarList" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for cal in data.get('items', []):
    role = cal.get('accessRole', '?')
    primary = ' ⭐' if cal.get('primary') else ''
    print(f\"{cal['id']:50s} | {cal.get('summary','?'):30s} | {role}{primary}\")
" 2>/dev/null || echo "Error listing calendars"
        ;;
    
    events)
        CAL_ID="${2:-primary}"
        DAYS="${3:-7}"
        NOW=$(date -u +%Y-%m-%dT%H:%M:%SZ)
        END=$(date -u -d "+${DAYS} days" +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u -v+${DAYS}d +%Y-%m-%dT%H:%M:%SZ)
        
        api_call GET "$CALENDAR_API/calendars/$(python3 -c "import urllib.parse; print(urllib.parse.quote('$CAL_ID', safe=''))")/events?timeMin=$NOW&timeMax=$END&singleEvents=true&orderBy=startTime&maxResults=50" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for ev in data.get('items', []):
    start = ev.get('start', {}).get('dateTime', ev.get('start', {}).get('date', '?'))
    end = ev.get('end', {}).get('dateTime', ev.get('end', {}).get('date', '?'))
    summary = ev.get('summary', '(no title)')
    status = ev.get('status', '?')
    eid = ev.get('id', '?')
    print(f'{start:25s} → {end:25s} | {summary:40s} | {eid}')
" 2>/dev/null || echo "Error listing events"
        ;;
    
    today)
        CAL_ID="${2:-primary}"
        TODAY=$(date -u +%Y-%m-%dT00:00:00Z)
        TOMORROW=$(date -u -d "+1 day" +%Y-%m-%dT00:00:00Z 2>/dev/null || date -u -v+1d +%Y-%m-%dT00:00:00Z)
        
        api_call GET "$CALENDAR_API/calendars/$(python3 -c "import urllib.parse; print(urllib.parse.quote('$CAL_ID', safe=''))")/events?timeMin=$TODAY&timeMax=$TOMORROW&singleEvents=true&orderBy=startTime" | python3 -c "
import sys, json
data = json.load(sys.stdin)
events = data.get('items', [])
if not events:
    print('No events today')
else:
    for ev in events:
        start = ev.get('start', {}).get('dateTime', ev.get('start', {}).get('date', '?'))
        summary = ev.get('summary', '(no title)')
        print(f'  {start[11:16] if \"T\" in start else \"all-day\":>6s}  {summary}')
" 2>/dev/null || echo "Error"
        ;;
    
    week)
        "$0" events "${2:-primary}" 7
        ;;
    
    add)
        CAL_ID="$2"
        SUMMARY="$3"
        START="$4"
        END="$5"
        DESC="${6:-}"
        VISIBILITY="${7:-default}"
        
        if [ -z "$CAL_ID" ] || [ -z "$SUMMARY" ] || [ -z "$START" ] || [ -z "$END" ]; then
            echo "Usage: calendar.sh add <calendar_id> <summary> <start_datetime> <end_datetime> [description] [visibility]"
            echo "  datetime format: 2026-02-05T10:00:00+08:00"
            echo "  visibility: default | private"
            exit 1
        fi
        
        JSON=$(python3 -c "
import json
event = {
    'summary': '$SUMMARY',
    'start': {'dateTime': '$START', 'timeZone': 'Asia/Hong_Kong'},
    'end': {'dateTime': '$END', 'timeZone': 'Asia/Hong_Kong'},
    'visibility': '$VISIBILITY',
    'reminders': {'useDefault': True}
}
desc = '''$DESC'''
if desc:
    event['description'] = desc
print(json.dumps(event))
")
        
        api_call POST "$CALENDAR_API/calendars/$(python3 -c "import urllib.parse; print(urllib.parse.quote('$CAL_ID', safe=''))")/events" "$JSON" | python3 -c "
import sys, json
data = json.load(sys.stdin)
if 'id' in data:
    print(f\"✅ Created: {data.get('summary')} ({data['start'].get('dateTime','?')})\")
    print(f\"   ID: {data['id']}\")
    print(f\"   Link: {data.get('htmlLink','')}\")
else:
    print(f\"❌ Error: {data.get('error',{}).get('message', json.dumps(data))}\")
" 2>/dev/null
        ;;
    
    busy)
        CAL_ID="$2"
        START="$3"
        END="$4"
        SUMMARY="${5:-Busy}"
        
        if [ -z "$CAL_ID" ] || [ -z "$START" ] || [ -z "$END" ]; then
            echo "Usage: calendar.sh busy <calendar_id> <start> <end> [summary]"
            exit 1
        fi
        
        "$0" add "$CAL_ID" "$SUMMARY" "$START" "$END" "" "private"
        ;;
    
    move)
        EVENT_ID="$2"
        CAL_ID="$3"
        NEW_START="$4"
        NEW_END="$5"
        
        if [ -z "$EVENT_ID" ] || [ -z "$CAL_ID" ] || [ -z "$NEW_START" ] || [ -z "$NEW_END" ]; then
            echo "Usage: calendar.sh move <event_id> <calendar_id> <new_start> <new_end>"
            exit 1
        fi
        
        JSON="{\"start\": {\"dateTime\": \"$NEW_START\", \"timeZone\": \"Asia/Hong_Kong\"}, \"end\": {\"dateTime\": \"$NEW_END\", \"timeZone\": \"Asia/Hong_Kong\"}}"
        
        api_call PATCH "$CALENDAR_API/calendars/$(python3 -c "import urllib.parse; print(urllib.parse.quote('$CAL_ID', safe=''))")/events/$EVENT_ID" "$JSON" | python3 -c "
import sys, json
data = json.load(sys.stdin)
if 'id' in data:
    print(f\"✅ Moved: {data.get('summary')} → {data['start'].get('dateTime','?')}\")
else:
    print(f\"❌ Error: {data.get('error',{}).get('message', json.dumps(data))}\")
" 2>/dev/null
        ;;
    
    delete)
        EVENT_ID="$2"
        CAL_ID="$3"
        
        if [ -z "$EVENT_ID" ] || [ -z "$CAL_ID" ]; then
            echo "Usage: calendar.sh delete <event_id> <calendar_id>"
            exit 1
        fi
        
        RESULT=$(api_call DELETE "$CALENDAR_API/calendars/$(python3 -c "import urllib.parse; print(urllib.parse.quote('$CAL_ID', safe=''))")/events/$EVENT_ID")
        if [ -z "$RESULT" ]; then
            echo "✅ Event deleted"
        else
            echo "❌ $RESULT"
        fi
        ;;
    
    freebusy)
        CAL_IDS="$2"  # comma-separated
        START="$3"
        END="$4"
        
        if [ -z "$CAL_IDS" ] || [ -z "$START" ] || [ -z "$END" ]; then
            echo "Usage: calendar.sh freebusy <cal1,cal2,...> <start> <end>"
            exit 1
        fi
        
        ITEMS=$(echo "$CAL_IDS" | tr ',' '\n' | while read cid; do
            echo "{\"id\": \"$cid\"}"
        done | paste -sd,)
        
        JSON="{\"timeMin\": \"$START\", \"timeMax\": \"$END\", \"items\": [$ITEMS]}"
        
        api_call POST "$CALENDAR_API/freeBusy" "$JSON" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for cal_id, info in data.get('calendars', {}).items():
    busy = info.get('busy', [])
    print(f'\n📅 {cal_id}:')
    if not busy:
        print('  ✅ All free')
    for slot in busy:
        print(f\"  🔴 {slot['start'][:16]} → {slot['end'][:16]}\")
" 2>/dev/null
        ;;
    
    refresh)
        refresh_token && echo "✅ Token refreshed successfully"
        ;;
    
    help|*)
        echo "Google Calendar CLI for Molty 🦎"
        echo ""
        echo "Commands:"
        echo "  list                              List all calendars"
        echo "  events [cal_id] [days]            List events (default: primary, 7 days)"
        echo "  today [cal_id]                    Today's events"
        echo "  week [cal_id]                     This week's events"  
        echo "  add <cal> <summary> <start> <end> [desc] [visibility]  Add event"
        echo "  busy <cal> <start> <end> [title]  Add busy/private block"
        echo "  move <event_id> <cal> <start> <end>  Reschedule event"
        echo "  delete <event_id> <cal>           Delete event"
        echo "  freebusy <cal1,cal2> <start> <end>  Check free/busy"
        echo "  refresh                           Refresh OAuth token"
        echo ""
        echo "Datetime format: 2026-02-05T10:00:00+08:00"
        ;;
esac
