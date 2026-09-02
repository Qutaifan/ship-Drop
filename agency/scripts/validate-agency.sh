#!/bin/bash
# validate-agency.sh - Validate agency structure and configuration

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENCY_DIR="$(dirname "$SCRIPT_DIR")"
DEPARTMENTS=("market-intelligence" "product-validation" "creative-production" "campaign-operations" "supply-chain" "financial-analytics" "learning-optimization")

echo "🔍 Validating Hermes-Ecom Drop Shipping Agency..."
echo "=============================================="

errors=()
warnings=()

# Check department directories
echo "📁 Checking department structure..."
for dept in "${DEPARTMENTS[@]}"; do
    dept_path="$AGENCY_DIR/departments/$dept"
    
    # Check main directory exists
    if [ ! -d "$dept_path" ]; then
        errors+=("Missing department directory: $dept")
        continue
    fi
    
    # Check subdirectories
    for subdir in agents output configs scripts; do
        if [ ! -d "$dept_path/$subdir" ]; then
            warnings+=("Missing subdirectory: $dept_path/$subdir")
        fi
    done
    
    # Check README exists
    if [ ! -f "$dept_path/README.md" ]; then
        warnings+=("Missing README.md for: $dept")
    fi
    
    echo "  ✅ $dept"
done

# Check configurations
echo "⚙️  Checking configurations..."
for dept in "${DEPARTMENTS[@]}"; do
    config_path="$AGENCY_DIR/departments/$dept/configs/config.yaml"
    if [ -f "$config_path" ]; then
        echo "  ✅ Config for $dept"
    else
        warnings+=("Missing config for: $dept")
    fi
done

# Check scripts
echo "🔧 Checking scripts..."
if [ ! -f "$AGENCY_DIR/scripts/deploy-agency.sh" ]; then
    errors+=("Missing deploy-agency.sh script")
fi
if [ ! -f "$AGENCY_DIR/scripts/spawn-agents.sh" ]; then
    errors+=("Missing spawn-agents.sh script")
fi

# Check profiles
echo "👤 Checking Hermes profiles..."
for dept in "${DEPARTMENTS[@]}"; do
    profile_name="agency-$(echo $dept | tr '-' '-')"
    if hermes profile list 2>/dev/null | grep -q "$profile_name"; then
        echo "  ✅ Profile: $profile_name"
    else
        warnings+=("Missing profile: $profile_name")
    fi
done

# Summary
echo ""
echo "=============================================="
if [ ${#errors[@]} -eq 0 ]; then
    echo "✅ Agency validation passed!"
    if [ ${#warnings[@]} -gt 0 ]; then
        echo ""
        echo "⚠️  Warnings (${#warnings[@]}):"
        printf '  - %s\n' "${warnings[@]}"
    fi
    echo ""
    echo "Agency is ready to deploy."
else
    echo "❌ Agency validation failed!"
    echo ""
    echo "Errors (${#errors[@]}):"
    printf '  - %s\n' "${errors[@]}"
    exit 1
fi