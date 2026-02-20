#!/bin/bash
# Gmail API helper for Molty
# Usage: gmail.sh [command] [args]

CREDS_FILE="/data/workspace/credentials/gmail-tokens.json"
OAUTH_FILE="/data/workspace/credentials/google-oauth.json"

# Read tokens — prefer client_id/secret from tokens file (matches refresh token),
# fall back to oauth file if not present in tokens
ACCESS_TOKEN=$(grep -o '"access_token": "[^"]*"' "$CREDS_FILE" | cut -d'"' -f4)
REFRESH_TOKEN=$(grep -o '"refresh_token": "[^"]*"' "$CREDS_FILE" | cut -d'"' -f4)
CLIENT_ID=$(grep -o '"client_id": "[^"]*"' "$CREDS_FILE" | cut -d'"' -f4)
CLIENT_SECRET=$(grep -o '"client_secret": "[^"]*"' "$CREDS_FILE" | cut -d'"' -f4)
# Fallback to oauth file if tokens file doesn't have client creds
if [ -z "$CLIENT_ID" ]; then
    CLIENT_ID=$(grep -o '"client_id": "[^"]*"' "$OAUTH_FILE" | cut -d'"' -f4)
fi
if [ -z "$CLIENT_SECRET" ]; then
    CLIENT_SECRET=$(grep -o '"client_secret": "[^"]*"' "$OAUTH_FILE" | cut -d'"' -f4)
fi

# Function to refresh access token
refresh_token() {
    RESPONSE=$(curl -s -X POST https://oauth2.googleapis.com/token \
        -d "client_id=$CLIENT_ID" \
        -d "client_secret=$CLIENT_SECRET" \
        -d "refresh_token=$REFRESH_TOKEN" \
        -d "grant_type=refresh_token")
    
    NEW_TOKEN=$(echo "$RESPONSE" | grep -o '"access_token": "[^"]*"' | cut -d'"' -f4)
    
    if [ -n "$NEW_TOKEN" ]; then
        # Update the tokens file
        sed -i "s|\"access_token\": \"[^\"]*\"|\"access_token\": \"$NEW_TOKEN\"|" "$CREDS_FILE"
        ACCESS_TOKEN="$NEW_TOKEN"
        echo "Token refreshed" >&2
    else
        echo "Failed to refresh token: $RESPONSE" >&2
        exit 1
    fi
}

# Function to make API call (with auto-refresh on 401)
api_call() {
    RESPONSE=$(curl -s -w "\n%{http_code}" "$@" -H "Authorization: Bearer $ACCESS_TOKEN")
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | sed '$d')
    
    if [ "$HTTP_CODE" = "401" ]; then
        refresh_token
        RESPONSE=$(curl -s -w "\n%{http_code}" "$@" -H "Authorization: Bearer $ACCESS_TOKEN")
        HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
        BODY=$(echo "$RESPONSE" | sed '$d')
    fi
    
    echo "$BODY"
}

case "$1" in
    profile)
        api_call "https://gmail.googleapis.com/gmail/v1/users/me/profile"
        ;;
    
    list)
        # List recent messages (default 10, or specify count)
        COUNT=${2:-10}
        api_call "https://gmail.googleapis.com/gmail/v1/users/me/messages?maxResults=$COUNT"
        ;;
    
    unread)
        # List unread messages
        COUNT=${2:-10}
        api_call "https://gmail.googleapis.com/gmail/v1/users/me/messages?q=is:unread&maxResults=$COUNT"
        ;;
    
    read)
        # Read a specific message by ID
        if [ -z "$2" ]; then
            echo "Usage: gmail.sh read <message_id>"
            exit 1
        fi
        api_call "https://gmail.googleapis.com/gmail/v1/users/me/messages/$2"
        ;;
    
    search)
        # Search messages
        if [ -z "$2" ]; then
            echo "Usage: gmail.sh search <query>"
            exit 1
        fi
        QUERY=$(echo "$2" | sed 's/ /%20/g')
        api_call "https://gmail.googleapis.com/gmail/v1/users/me/messages?q=$QUERY"
        ;;
    
    send)
        # Send email: gmail.sh send "to@email.com" "Subject" "Body"
        if [ -z "$2" ] || [ -z "$3" ] || [ -z "$4" ]; then
            echo "Usage: gmail.sh send <to> <subject> <body>"
            exit 1
        fi
        TO="$2"
        SUBJECT="$3"
        BODY="$4"
        
        # Encode subject for UTF-8 (RFC 2047)
        ENCODED_SUBJECT="=?UTF-8?B?$(echo -n "$SUBJECT" | base64 -w 0)?="
        
        # Create raw email with proper MIME headers
        RAW=$(printf "MIME-Version: 1.0\nContent-Type: text/plain; charset=utf-8\nContent-Transfer-Encoding: 8bit\nTo: %s\nSubject: %s\n\n%s" "$TO" "$ENCODED_SUBJECT" "$BODY" | base64 -w 0 | tr '+/' '-_' | tr -d '=')
        
        curl -s -X POST "https://gmail.googleapis.com/gmail/v1/users/me/messages/send" \
            -H "Authorization: Bearer $ACCESS_TOKEN" \
            -H "Content-Type: application/json" \
            -d "{\"raw\": \"$RAW\"}"
        ;;
    
    refresh)
        refresh_token
        echo "Token refreshed successfully"
        ;;
    
    *)
        echo "Gmail CLI for Molty"
        echo ""
        echo "Commands:"
        echo "  profile          - Show account info"
        echo "  list [n]         - List recent messages (default 10)"
        echo "  unread [n]       - List unread messages"
        echo "  read <id>        - Read a specific message"
        echo "  search <query>   - Search messages"
        echo "  send <to> <subj> <body> - Send email"
        echo "  refresh          - Refresh access token"
        ;;
esac
