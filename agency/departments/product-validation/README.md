# Product Validation Department - Hermes-Ecom Drop Shipping Agency

## Department Mandate
**Primary Function**: Apply rigorous product validation using the 6-Criteria Formula and True Margin Matrix to ensure only profitable opportunities enter the pipeline.

### Key Objectives:
- Validate products against 6-Criteria + CAC gate + True Margin Matrix
- Maintain strict risk-adjusted return discipline
- Protect capital through comprehensive validation
- Apply learning heuristics from HEURISTICS.md
- Generate qualified creative briefs for winning products
- Execute PROTOCOL-01 and PROTOCOL-02 requirements

## Department Skills & Tools

### Core Skills Required:
- **margin_solver** - True Margin Matrix calculations
- **profitability** - CAC gate validation and net margin analysis
- **demand_screen** - Demo burden screening (OBSERVE phase)
- **ad_library** - Competitive validation (PROTOCOL-01)
- **learning_loop** - Self-improvement and heuristic updates
- **ecommerce-validator** - Additional validation capabilities
- **margin-calculator variants** - Product-specific margin analysis

### Critical Tools:
- **Python Execution** - For scripts/profitability.py, margin_solver.py
- **Terminal** - Command line validation and calculations
- **Memory** - Cross-campaign learning and pattern recognition
- **Session Search** - Previous validation outcomes and lessons

### Scripts Integration (Core to Hermes-Ecom):
- **scripts/margin_solver.py** - True Margin Matrix (corrected 2026-08-30 formula)
- **scripts/profitability.py** - CAC gate validation (EUR 21.48 median CPA)
- **scripts/demand_screen.py** - Demo burden screening
- **scripts/ad_library.py** - Facebook Ad Library validation
- **scripts/learning_loop.py** - PROTOCOL-03 learning integration

### Department Protocols (Hermes-Ecom Strict):

#### OBSERVE Phase (Quality Gate):
1. Run `scripts/demand_screen.py` on market-intelligence candidates
2. Check skeptic ratio - if ≥50%, increase proof burden
3. Identify 5-10 distinct competitors actively running ads
4. Validate 3+ competitor ads have 30+ days active history (Meta API)

#### ORIENT Phase (Scoring):
1. **Read learnings/HEURISTICS.md** first (MANDATORY)
2. Apply SUPPORTED heuristics as scoring modifiers, RETIRED as eliminators
3. Filter through 6-Criteria Product Selection Formula:
   - Wow Factor: Immediate emotional impact (<3 seconds)
   - Problem Solving: Resolves painful friction point
   - Visual Appeal: Communicable in 9:16 vertical video
   - Healthy Margins: ≥€15-30 gross margin per sale (retail ≥€20)
   - Low Return Potential: Simple, durable mechanics
   - Low Retail Availability: Hard to find locally
4. Calculate True Margin Matrix (corrected formula):
   ```
   Net Margin = (Retail / (1 + VAT)) - (Product Cost + Shipping + Import Duty) - (0.03 x Retail)
   ```
5. Apply CAC gate: Net Margin must be ≥2x median CPA benchmark (EUR 21.48)
6. Target retail band: EUR 62-93 (not EUR 30-45)

#### DECIDE Phase (Hypothesis):
1. **Formulate explicit numeric predictions** for:
   - CTR: Specific percentage (e.g., "2% CTR on TikTok")
   - CVR: Specific conversion rate
   - Net Margin: Expected profit per unit
   - CPA: Expected acquisition cost
2. **Discount by running bias** from HEURISTICS.md Calibration Log
3. **Score objectively** using weighted criteria

#### ACT Phase (Production):
1. Generate 3 creative briefs (problem, transformation, aspirational)
2. Create landing page structure (PROTOCOL-02)
3. Integrate with Remotion for programmatic video compilation
4. Output ready for campaign launch

## Department Agents

### Product Validation Lead Agent
**Purpose**: Primary product validation and scoring
**Skills**: margin_solver, profitability, ad_library, demand_screen, learning_loop
**Tools**: Python execution, terminal, memory, session_search
**Knowledge Base**: learnings/HEURISTICS.md, learnings/_TEMPLATE.md, learnings/YYYY-MM-DD-*.md
**Directives**: Strict adherence to Hermes-Ecom protocols, zero compromise on validation standards

### Margin Analysis Agent
**Purpose**: True Margin Matrix calculations and CAC validation
**Skills**: margin_solver, profitability, margin-calculator variants
**Tools**: Python execution, terminal, memory
**Focus**: Anti-de-minimis compliance, EU warehouse strategy, VAT calculations

### Competitive Validation Agent
**Purpose**: PROTOCOL-01 competitive intelligence verification
**Skills**: ad_library, demand_screen, ecommerce-competitor-analysis
**Tools**: browser, web, terminal (Meta API calls)
**Output**: Competitor check blocks, saturation analysis

### Learning Integration Agent
**Purpose**: Protocol-03 learning loop and heuristic updates
**Skills**: learning_loop, memory, session_search
**Tools**: all tools (for analysis), memory
**Function**: Updates HEURISTICS.md, manages Calibration Log

## Risk Management (Hermes-Ecom Focus)

### Capital Protection:
- **CAC Gate Enforcement**: No product fails 2x CPA threshold
- **Margin Floor**: Net margin ≥€15, 3x COGS minimum
- **Retail Ceiling**: EUR 62-93 target band (prevents overpricing)
- **Proof Burden**: High skeptic ratio → increased validation rigor

### Quality Assurance:
- **No Emotional Trading**: Only data-driven decisions
- **No Revenge Trading**: Strict pipeline discipline
- **No Oversizing**: Position sizing based on confidence
- **No Chasing Volatility**: Focus on sustainable opportunities

### Validation Standards:
- **Competitor Requirement**: 5-10 distinct competitors
- **Ad Duration**: 30+ days active (proven profitability)
- **YouTube Demand**: Median views, share rates, skeptic ratios
- **Margin Accuracy**: True Margin Matrix (corrected for VAT, duty)

## Integration Points

### With Market Intelligence:
- Receive validated candidates for PROTOCOL-01
- Apply competitive intelligence to scoring
- Share demand metrics for margin calculations

### With Creative Production:
- Generate creative briefs for validated products
- Provide margin targets for creative messaging
- Share consumer insights for hook development

### With Campaign Operations:
- Launch validated campaigns with proven ROAS
- Monitor margin performance vs. projections
- Provide optimization recommendations

### With Learning & Optimization:
- Feed validation outcomes into learning loop
- Update heuristics based on validation results
- Maintain Calibration Log for bias correction

## Performance Metrics (Hermes-Ecom):

### Validation Quality:
- **CAC Gate Success Rate**: 100% (no products fail 2x CPA)
- **Margin Gate Success Rate**: 100% (net margin ≥€15)
- **Retail Target Success Rate**: 100% (EUR 62-93 range)
- **6-Criteria Pass Rate**: 60-80% (high bar for quality)

### Risk Metrics:
- **Drawdown Control**: Aggressive risk reduction during volatility
- **Capital Preservation**: Zero losses from validation failures
- **Learning Velocity**: Heuristic updates every campaign cycle
- **Process Consistency**: 95%+ protocol adherence

### Output Standards:
- **Validated Products**: 1 qualified creative brief per approved product
- **Margin Projections**: Detailed True Margin Matrix with scenarios
- **Creative Specs**: 3 hooks + 1 landing page per product
- **Launch Readiness**: Full campaign package for scaling

## Command Examples

### Validate Candidate Product:
```
python3 scripts/margin_solver.py --retail 49.90 --cost 8.20 --shipping 3.10 --vat 0.19 --duty 3.0
# Should FAIL (returns €29.13 < €33.90 COGS gate)
```

### Run Full Validation:
```
python3 scripts/profitability.py --retail 85.00 --cost 12.00 --shipping 4.50 --vat 0.19 --duty 3.0
# Should PASS (returns €46.13 ≥ €33.90 COGS gate)
```

### Generate Creative Brief:
```
python3 scripts/generate_brief.py --product "high-ticket modular wall shelf" --target-margin 25.00
```

### Run Learning Loop:
```
python3 scripts/learning_loop.py --campaign campaigns/bamboo-drawer-organizers.md
```

## Hermes-Ecom Compliance Checklist:
- [ ] Read learnings/HEURISTICS.md first
- [ ] Apply SUPPORTED heuristics as modifiers
- [ ] Reject RETIRED heuristics entirely
- [ ] Use corrected True Margin Matrix formula
- [ ] Enforce CAC gate (2x median CPA)
- [ ] Target EUR 62-93 retail band
- [ ] Formulate numeric hypotheses
- [ ] Discount by running bias
- [ ] Apply 6-Criteria formula strictly
- [ ] Generate 3+1 creative deliverables
- [ ] Integrate with Remotion system
- [ ] Feed all outcomes to learning loop

## Success Criteria

### Capital Preservation:
- Zero losses from validation failures
- Aggressive risk reduction during drawdowns
- Protection of liquidity at all times

### Sustainable Growth:
- 15-20% validation success rate
- Consistent net margin of €15-30 per sale
- ROAS ≥3.0x on launched campaigns
- 3-6 month average campaign lifespan

### Continuous Improvement:
- Monthly heuristic updates
- Quarterly process refinement
- Annual bias recalibration
- Daily learning loop completion