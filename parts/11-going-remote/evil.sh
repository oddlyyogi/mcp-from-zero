curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8000/mcp \
  -H "Origin: https://evil.example" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "MCP-Protocol-Version: 2026-07-28" \
  -H "Mcp-Method: tools/call" -H "Mcp-Name: get_order" \
  -d @call.json
