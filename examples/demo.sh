#!/bin/bash

# Example script demonstrating A2A Registry API usage

API_BASE="http://localhost:3000/api/v1"

echo "=== A2A Registry API Demo ==="
echo

# 1. Health Check
echo "1. Checking registry health..."
curl -s -X GET $API_BASE/../health | jq
echo
sleep 1

# 2. Register an agent
echo "2. Registering translation agent..."
AGENT_RESPONSE=$(curl -s -X POST $API_BASE/agents \
  -H "Content-Type: application/json" \
  -d @sample-agent.json)

echo $AGENT_RESPONSE | jq
AGENT_ID=$(echo $AGENT_RESPONSE | jq -r '.agentId')
echo "Agent ID: $AGENT_ID"
echo
sleep 1

# 3. Get agent details
echo "3. Retrieving agent details..."
curl -s -X GET $API_BASE/agents/$AGENT_ID | jq
echo
sleep 1

# 4. Send heartbeat
echo "4. Sending heartbeat..."
curl -s -X POST $API_BASE/agents/$AGENT_ID/heartbeat | jq
echo
sleep 1

# 5. List all agents
echo "5. Listing all agents..."
curl -s -X GET "$API_BASE/agents?limit=10" | jq
echo
sleep 1

# 6. Search by tag
echo "6. Searching agents by tag 'translation'..."
curl -s -X GET "$API_BASE/agents?tags=translation" | jq
echo
sleep 1

# 7. Search by skill
echo "7. Searching agents with 'translate' skill..."
curl -s -X GET "$API_BASE/agents?skill=translate" | jq
echo
sleep 1

# 8. Update agent
echo "8. Updating agent metadata..."
curl -s -X PUT $API_BASE/agents/$AGENT_ID \
  -H "Content-Type: application/json" \
  -d '{
    "agentCard": {
      "name": "translation-agent",
      "description": "Enhanced multilingual translation agent",
      "endpoint": "https://translation-agent.example.com",
      "protocolVersion": "0.3"
    },
    "tags": ["translation", "nlp", "language", "enhanced"],
    "metadata": {
      "region": "us-east-1",
      "version": "1.1.0"
    }
  }' | jq
echo
sleep 1

# 9. Delete agent (cleanup)
echo "9. Cleaning up - deleting agent..."
curl -s -X DELETE $API_BASE/agents/$AGENT_ID
echo "Agent deleted."
echo

echo "=== Demo Complete ==="
