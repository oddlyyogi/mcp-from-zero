Q="The socks in order 1042 were the wrong size. Please refund one pack."
echo "$1" | uv run agent.py "$Q" 2>/dev/null
