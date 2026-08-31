# Agency Infrastructure

## Overview
Core infrastructure files for the Hermes-Ecom drop shipping agency including agent configurations, deployment scripts, and shared utilities.

## Markets
- **EU/UK** — automated (Meta Ad Library API, EU warehouse, IOSS/OSS, EUR €62-93 target band)
- **US** — manual (web-UI competitor count, US 3PL bulk import, state sales tax, USD $68-105 target band)

US entry point: `agency/US-MARKET.md`. Per-department US playbooks: `agency/departments/*/us-market/`.

## Structure

### configs/ - Agent configurations
- **config.yaml** - Base configuration template for all agents
- **department-configs/** - Department-specific configurations

### agents/ - Agent definitions
- **lead-agents/** - Primary agent definitions per department
- **specialist-agents/** - Specialized agent configurations
- **shared-agents/** - Cross-department shared capabilities

### scripts/ - Automation scripts
- **deploy-agency.sh** - Deploy the full agency structure
- **spawn-agents.sh** - Spawn Hermes agents for each department
- **validate-agency.sh** - Validate agency structure and configuration
- **setup-cron.sh** - Setup cron jobs for automated operations

## Deployment

### Quick Start
```bash
# Deploy full agency
./scripts/deploy-agency.sh

# Spawn all department agents
./scripts/spawn-agents.sh

# Validate agency structure
./scripts/validate-agency.sh
```

### Individual Deployment
```bash
# Deploy specific department
./scripts/deploy-agency.sh --department market-intelligence

# Spawn specific agents
./scripts/spawn-agents.sh --department product-validation
```

## Agent Spawning

### Spawning Commands
Each department agent can be spawned using:

```bash
# Market Intelligence Lead
hermes chat -q "Execute market intelligence protocol" --profile agency-market-intelligence

# Product Validation Lead
hermes chat -q "Execute product validation protocol" --profile agency-product-validation
```

### Profile Configuration
Create separate profiles for each department:

```bash
hermes profile create agency-market-intelligence --clone default
hermes profile create agency-product-validation --clone default
# etc...
```

## Cron Jobs for Automation

### Scheduled Operations
```bash
# Daily campaign review
hermes cron create "0 9 * * *" -p agency-campaign-operations "Review daily campaign performance"

# Weekly learning update
hermes cron create "0 18 * * 1" -p agency-learning "Update heuristics from last week's campaigns"

# Monthly financial report
hermes cron create "0 20 1 * *" -p agency-financial "Generate monthly financial report"
```

## Cross-Department Communication

### Handoff Protocols
1. **Market Intelligence → Product Validation**: Qualified candidates
2. **Product Validation → Creative Production**: Validated products
3. **Creative Production → Campaign Operations**: Creative assets
4. **Campaign Operations → Financial Analytics**: Performance data
5. **All → Learning & Optimization**: Campaign outcomes

### Integration Points
- **Shared Memory**: Cross-department knowledge sharing
- **Campaign Directory**: Centralized campaign tracking
- **Products Directory**: Product information repository
- **Reports Directory**: Cross-department reporting

## Quality Assurance

### Validation Checks
- All department directories created
- Agent configurations properly set up
- Cron jobs configured correctly
- Cross-department handoffs documented
- Integration points validated

### Performance Monitoring
- Agent response times
- Cross-department communication latency
- Campaign performance metrics
- Learning loop effectiveness

## Scaling Strategy

### Phase 1: Foundation
- Deploy all departments
- Establish basic handoffs
- Set up cron jobs for automation

### Phase 2: Optimization
- Implement parallel processing
- Add advanced analytics
- Optimize cross-department workflows

### Phase 3: Maturity
- Full automation with minimal oversight
- Advanced predictive capabilities
- Self-improving agency structure