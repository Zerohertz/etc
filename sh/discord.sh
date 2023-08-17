# ~/.bashrc
# ~/.zshrc

DISCORD="YOUR_WEBHOOK_URL"
to_discord() {
    local content=$1
    curl -H "Content-Type: application/json" \
         -X POST \
         -d "{\"content\":\"$content\"}" \
         $DISCORD
}