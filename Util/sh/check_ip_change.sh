#!/bin/bash

to_slack() {
	local content=$1
	curl -X POST https://slack.com/api/chat.postMessage \
		-H "Authorization: Bearer $SLACK_BOT_TOKEN" \
		-H "Content-type: application/json" \
		-d '{
                "channel": "zerohertz",
                "text": "'"$content"'",
                "username": "IP",
                "icon_emoji": ":computer:",
            }'
}

IP_FILE="/tmp/last_known_ip"
current_ip=$(curl -s ipecho.net/plain)
if [[ "$current_ip" != "$(cat $IP_FILE 2>/dev/null)" ]]; then
	to_slack "IP changed to $current_ip"
	echo "$current_ip" >$IP_FILE
fi
