#!/bin/bash
# deploy-agency.sh - Deploy the full Hermes-Ecom Drop Shipping Agency

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENCY_DIR="$(dirname "$SCRIPT_DIR")"
DEPARTMENTS=("market-intelligence" "product-validation" "creative-production" "campaign-operations" "supply-chain" "financial-analytics" "learning-optimization")

echo "🚀 Deploying Hermes-Ecom Drop Shipping Agency..."
echo "=============================================="

# Create department directories
echo "📁 Creating department structure..."
for dept in "${DEPARTMENTS[@]}"; do
    dept_path="$AGENCY_DIR/departments/$dept"
    mkdir -p "$dept_path"/{agents,output,configs,scripts}
    echo "  ✅ $dept"
done

# Copy configurations
echo "⚙️  Copying configurations..."
for dept in "${DEPARTMENTS[@]}"; do
    if [ -f "$AGENCY_DIR/configs/department-configs/$dept/config.yaml" ]; then
        cp "$AGENCY_DIR/configs/department-configs/$dept/config.yaml" "$AGENCY_DIR/departments/$dept/configs/config.yaml"
        echo "  ✅ Copied config for $dept"
    fi
done

# Setup profiles
echo "👤 Setting up Hermes profiles..."
for dept in "${DEPARTMENTS[@]}"; do
    profile_name="agency-$(echo $dept | tr '-' '-')"
    hermes profile create "$profile_name" --clone default 2>/dev/null || true
    echo "  ✅ Profile: $profile_name"
done

# Setup cron jobs
echo "⏰ Setting up cron jobs..."
hermes cron create "0 9 * * *" -p agency-campaign-operations "Daily campaign performance review" 2>/dev/null || true
hermes cron create "0 18 * * 1" -p agency-learning "Weekly heuristic update from campaigns" 2>/dev/null || true
hermes cron create "0 20 1 * *" -p agency-financial "Monthly financial report generation" 2>/dev/null || true

# Validate deployment
echo "✅ Validating deployment..."
missing=()
for dept in "${DEPARTMENTS[@]}"; do
    if [ ! -f "$AGENCY_DIR/departments/$dept/README.md" ]; then
        missing+=("$dept")
    fi
done

if [ ${#missing[@]} -eq 0 ]; then
    echo "🎉 Agency deployment complete!"
    echo "=================================="
    echo "Departments deployed:"
    printf '  - %s\n' "${DEPARTMENTS[@]}"
    echo ""
    echo "Next steps:"
    echo "  1. Review department README.md files"
    echo "  2. Configure department-specific scripts"
    echo "  3. Test cross-department handoffs"
    echo "  4. Run initial validation: ./scripts/validate-agency.sh"
else
    echo "❌ Missing documentation for: ${missing[*]}"
    exit 1
fi