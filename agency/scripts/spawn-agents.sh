#!/bin/bash
# spawn-agents.sh - Spawn Hermes agents for each department

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENCY_DIR="$(dirname "$SCRIPT_DIR")"
DEPARTMENTS=("market-intelligence" "product-validation" "creative-production" "campaign-operations" "supply-chain" "financial-analytics" "learning-optimization")

echo "🤖 Spawning Hermes agents for all departments..."
echo "=============================================="

for dept in "${DEPARTMENTS[@]}"; do
    profile_name="agency-$(echo $dept | tr '-' '-')"
    echo "Spawning agent for $dept..."
    
    # Spawn agent in background using tmux
    tmux new-session -d -s "$profile_name" -x 120 -y 40 "hermes -w" 2>/dev/null || true
    
    # Wait for startup
    sleep 3
    
    # Send initial message
    tmux send-keys -t "$profile_name" "Execute $(echo $dept | tr '-' ' ') protocol" Enter 2>/dev/null || true
    
    echo "  ✅ Agent spawned for $dept (profile: $profile_name)"
done

echo ""
echo "🎉 All department agents spawned!"
echo "=================================="
echo "To interact with agents:"
echo "  tmux attach -t market-intelligence"
echo "  tmux attach -t product-validation"
echo "  etc..."
echo ""
echo "To list all agents:"
echo "  hermes sessions list"