# Market Intelligence Department - Hermes-Ecom Drop Shipping Agency

## Department Mandate
**Primary Function**: Identify and validate market opportunities through systematic competitive analysis, demand validation, and competitive intelligence gathering.

### Key Objectives:
- Discover profitable market gaps using 6-Criteria Product Selection Formula
- Validate sustained profitability through competitor analysis
- Maintain demand-side intelligence (TikTok, YouTube, web)
- Generate qualified product feed for validation pipeline
- Track market saturation indicators and emerging trends

## Department Skills & Tools

### Core Skills Required:
- **agent-reach** - YouTube, web, RSS intelligence gathering
- **web_search** - Market research, trend identification
- **session_search** - Cross-campaign knowledge sharing
- **ecommerce-competitor-analysis** - Competitor profiling
- **competitor-price-tracker** - Price intelligence
- **domain-monitoring** - Market opportunity detection
- **trend-scan** - Market trend analysis
- **dropshipping-product-research** - Product viability assessment

### Critical Tools:
- **Agent-Reach CLI** - Free demand intelligence from multiple platforms
- **Firecrawl MCP** - Competitor storefront intelligence
- **Meta Ad Library API** - Competitive validation (via scripts/ad_library.py)
- **Web Extract** - Market data harvesting
- **Terminal** - API integration for pricing tools

### Scripts Integration:
- **scripts/demand_screen.py** - Demo burden screening (OBSERVE phase)
- **scripts/ad_library.py** - Facebook Ad Library validation (PROTOCOL-01)
- **scripts/profitability.py** - CAC gate validation

## Department Agents

### Market Intelligence Lead Agent
**Purpose**: Primary market intelligence gathering and analysis
**Skills**: All market intelligence skills + cross-department communication
**Tools**: web_search, session_search, agent-reach, firecrawl, browser
**Knowledge Base**: learnings/HEURISTICS.md + learnings/_TEMPLATE.md

### Competitive Intelligence Agent
**Purpose**: Deep competitor analysis and saturation monitoring
**Skills**: ecommerce-competitor-analysis, competitor-price-tracker, domain-monitoring
**Tools**: web, browser, terminal (for API pricing tools)
**Output**: Competitor check blocks for PROTOCOL-01 validation

### Demand Validation Agent
**Purpose**: Consumer demand validation and trend analysis
**Skills**: dropshipping-product-research, trend-scan, agent-reach
**Tools**: agent-reach, web_search, session_search
**Output**: Demand metrics for product viability scoring

## Department Protocols

### OBSERVE Phase (Quality Gate):
1. Run `scripts/demand_screen.py` on trending product categories
2. Use agent-reach for YouTube trend analysis (median duration, share rate, skeptic ratio)
3. Cross-reference with Meta Ad Library for existing commercial presence
4. Flag categories with high skeptic ratio (>50%) for increased proof burden

### ORIENT Phase (Scoring):
1. Read learnings/HEURISTICS.md for scoring modifiers
2. Filter through 6-Criteria Product Selection Formula
3. Apply competitive saturation analysis (15+ advertisers = saturated)
4. Calculate market opportunity score

### Output Standards:
- **Candidate List**: Minimum 5 products per review cycle
- **Competitor Data**: 5-10 active competitors per product
- **Demand Metrics**: YouTube views, engagement rates, sentiment analysis
- **Market Signals**: Pricing intelligence, saturation indicators
- **Confidence Scores**: 60-90% confidence threshold for pipeline

## Risk Management

### Market Risks:
- **Saturated Markets**: Reject categories with >15 sustained advertisers
- **Low Demand**: Filter by YouTube median views (<1,000 for viral novelties)
- **High Proof Burden**: Flag skeptic ratio (>50%) for increased validation rigor

### Execution Risks:
- **Resource Allocation**: Focus on categories with proven demand
- **Competitive Intelligence**: Prioritize markets with accessible data
- **Trend Volatility**: Regular revalidation of demand metrics

### Capital Preservation:
- **Zero-Cost Intelligence**: Agent-Reach, web tools (no API fees)
- **Free Validation**: Scripts use existing data sources
- **Prioritization**: High-confidence, low-cost opportunities first

## Integration Points

### With Product Validation Department:
- Feed qualified candidates for PROTOCOL-01 validation
- Provide competitive intelligence for CAC gates
- Supply demand metrics for True Margin Matrix calculations

### With Creative Production Department:
- Identify viral novelty opportunities for creative testing
- Provide consumer insights for hook development
- Share market trends for aspirational lifestyle hooks

### With Learning & Optimization:
- Feed market intelligence into HEURISTICS.md
- Track competitive landscape changes
- Identify emerging patterns for heuristic updates

## Performance Metrics

### Lead Generation:
- **Candidates Analyzed**: 20+ products per month
- **Competitor Profiles**: 5-10 per product
- **Demand Validations**: 60%+ confidence rate
- **Market Saturation Detection**: Early warning for category shifts

### Quality Standards:
- **Validation Success Rate**: 15-20% pipeline conversion
- **Competitive Intelligence Coverage**: 100% of candidate products
- **Demand Data Completeness**: 90%+ of candidates have validated demand
- **Risk Mitigation**: Zero false positives in competitive analysis

### Continuous Improvement:
- **Learning Loop**: All findings feed into learnings/HEURISTICS.md
- **Heuristic Updates**: Quarterly review of market intelligence effectiveness
- **Process Optimization**: Feedback from validation pipeline for intelligence improvements

## Command Examples

### Start Market Intelligence Agent:
```
hdemis chat -s market-intelligence-lead "Research viral novelties in home organization category"
```

### Run Demand Screen on Category:
```
python3 scripts/demand_screen.py --category "home-organization"
```

### Check Competitive Saturation:
```
python3 scripts/ad_library.py --category "home-organization" --market eu
```

### Generate Market Report:
```
hdemis -s market-intelligence "Generate comprehensive market intelligence report for home organization products"
```