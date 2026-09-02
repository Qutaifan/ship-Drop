# Dropshipping Agency Structure

## Overview
This agency follows the Hermes-Ecom framework from AGENTS.md, organizing specialized departments that each contain autonomous agents utilizing the best available skills and tools from the eCommerce-Skills library and project resources.

## Department Structure

**Markets**: EU/UK (automated) and US (manual). See `agency/US-MARKET.md` for US specifics.

### 1. Market Intelligence Department
**Focus**: Market research, trend analysis, competitor intelligence, demand validation (EU + US)
**Core Skills**:
- market-gap-analysis
- trend-scan (from scripts/reports)
- competitor-price-analysis
- competitor-price-tracker
- ecommerce-competitor-analysis
- product-research (dropshipping-product-research, ebay-product-research, tiktok-shop-product-research)
- Agent-Reach (for YouTube/web demand analysis)
- Firecrawl MCP (for merchant site intelligence)
**Key Tools**: web_search, web_extract, browser, session_search, Agent-Reach CLI
**Primary Output**: Validated product opportunities with market sizing, competition analysis, demand validation

### 2. Product Validation Department  
**Focus**: Rigorous product validation using PROTOCOL-01 gates and margin mathematics
**Core Skills**:
- profitability-validation (scripts/profitability.py)
- margin-solver (scripts/margin_solver.py)
- demand-screen (scripts/demand_screen.py)
- ad-library-validation (scripts/ad_library.py)
- zero-budget-model (reports/2026-08-30-zero-budget-model.md)
- HEURISTICS.md (learning system)
- ecommerce-validator (existing skill)
**Key Tools**: margin_solver.py, profitability.py, ad_library.py, demand_screen.py, terminal (for calculations)
**Primary Output**: VALIDATED products that pass all 6-criteria + CAC gate + True Margin Matrix

### 3. Creative Production Department
**Focus**: AI-generated and human-quality ad creative for winning products
**Core Skills**:
- comfyui-product-staging (existing .agents/skill)
- remotion-video-ads (existing .agents/skill)
- tiktok-shop-ads
- tiktok-shop-content-strategy
- ecommerce-video-marketing
- ecommerce-landing-page
- ecommerce-feed-management
- product-description-generator
- ecommerce-personalization
**Key Tools**: ComfyUI (local RTX 4060), Remotion, Veo (for winners only), image_gen, video analysis
**Primary Output**: 3+1 creative briefs per product (3 video hooks + 1 landing page scaffold)

### 4. Campaign Operations Department
**Focus**: Launch, monitor, optimize, and scale validated campaigns
**Core Skills**:
- ecommerce-marketing-strategy-builder
- ecommerce-ppc-strategy-planner
- ecommerce-social-media-marketing
- ecommerce-feed-management
- conversion-rate-optimization
- ecommerce-ab-testing
- ecommerce-checkout-optimization
- ecommerce-customer-retention
- dynamic-pricing-ecommerce
- inventory-tracking-software
**Key Tools**: cronjob (for scheduling/optimization), delegation (subagents), terminal (ad platform APIs), memory
**Primary Output**: Live campaigns with performance tracking, optimization recommendations, scale/kill/iterate decisions

### 5. Supply Chain & Logistics Department
**Focus**: Supplier management, fulfilment optimization, anti-de-minimis compliance
**Core Skills**:
- supply-chain-optimization (amazon, shopify, tiktok, walmart variants)
- warehouse-optimization
- restock-alert
- ecommerce-shipping-rates
- dropshipping-product-research
- supplier management (cjdropshipping.md, ebay.md, temu.md)
- cross-border-ecommerce
- omnichannel-ecommerce
**Key Tools**: supplier APIs, FILE tool (supplier docs), terminal (for API calls)
**Primary Output**: Optimized supplier network with EU warehouse utilization, cost tracking, lead time management

### 6. Financial Analytics Department
**Focus**: Profit tracking, ROI analysis, financial modeling, budget allocation
**Core Skills**:
- profit-margin-calculator (amazon, shopify, tiktok, walmart variants)
- price-optimization-tool
- minimum-advertised-price
- online-reputation-management
- public-status-page
- sales-tracking-tool
- share-of-shelf
- synthetic-monitoring
**Key Tools**: DuckDB + Python (margin_solver.py), Metabase OSS, terminal (financial calculations)
**Primary Output**: Real-time P&L, ROAS tracking, budget optimization, scale recommendations

### 7. Learning & Optimization Department
**Focus**: Continuous improvement through PROTOCOL-03 learning loop
**Core Skills**:
- learning-loop (scripts/learning_loop.py)
- HEURISTICS.md maintenance
- ecommerce-returns-management
- review-checker (amazon, ebay, walmart variants)
- review-monitoring
- customer-feedback-analysis
- brand-monitoring
- brand-protection
- file-integrity-monitoring
**Key Tools**: memory, session_search, learnings/ directory, fact_store
**Primary Output**: Updated heuristics, retired false hypotheses, improved scoring model, knowledge base growth

## Agent Deployment Model

Each department deploys specialized Hermes agents with:

### Agent Configuration
- **Model**: Optimized for task type (reasoning for analysis, fast for execution)
- **Toolsets**: Department-specific enabled tools
- **Skills**: Pre-loaded department skills
- **Memory**: Department-specific context retention
- **Delegation**: Ability to spawn subagents for parallel tasks

### Communication Protocol
- **Inter-department**: Structured handoffs via documented deliverables
- **Intra-department**: Agent collaboration through shared goals and context
- **Reporting**: Standardized metrics and KPI tracking
- **Escalation**: Clear paths for decisions requiring human oversight

## Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)
1. Set up department directory structure
2. Deploy core validation pipeline (Products → Market Intelligence → Product Validation)
3. Establish learning loop infrastructure
4. Configure basic agent spawning capabilities

### Phase 2: Operational (Weeks 3-4)
1. Deploy creative production pipeline
2. Launch first test campaigns
3. Implement supply chain optimization
4. Establish financial tracking

### Phase 3: Scale (Weeks 5-6)
1. Full department activation
2. Automated optimization loops
3. Multi-product portfolio management
4. Advanced learning system maturity

## Success Metrics
- Product validation rate (target: 15-20% of analyzed products)
- Campaign ROAS (target: ≥3.0x)
- Net margin per sale (target: €15-30)
- Learning velocity (heuristics improved per week)
- Departmental efficiency (time from idea to validated campaign)