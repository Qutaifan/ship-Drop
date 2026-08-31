# Financial Analytics Department - Hermes-Ecom Drop Shipping Agency

## Department Mandate
**Primary Function**: Comprehensive financial analysis, ROI tracking, and profitability optimization to ensure sustainable capital growth and risk-adjusted returns.

### Key Objectives:
- Real-time profit and loss tracking across all campaigns
- Comprehensive ROI analysis and budget optimization
- Price optimization and margin management
- Financial risk assessment and capital preservation
- Compliance with Hermes-Ecom capital protection principles
- Integration with all department financial data

## Department Skills & Tools

### Core Skills Required:
- **profit-margin-calculator** - Amazon, Shopify, TikTok, Walmart variants
- **price-optimization-tool** - Dynamic price optimization
- **minimum-advertised-price** - Price floor enforcement
- **online-reputation-management** - Financial reputation tracking
- **public-status-page** - Financial transparency and reporting
- **sales-tracking-tool** - Revenue and performance tracking
- **share-of-shelf** - Market position analysis
- **synthetic-monitoring** - Financial metrics monitoring
- **margin-calculator variants** - Product-specific financial analysis

### Critical Tools:
- **DuckDB + Python** - True Margin Matrix calculations
- **Metabase OSS** - Financial reporting and dashboards
- **Terminal** - Financial calculations and analysis
- **Memory** - Financial history and learning
- **Session Search** - Previous financial performance
- **Cronjob** - Scheduled financial reporting and analysis
- **Financial APIs** - Real-time market and pricing data

### Financial Analysis Framework (Hermes-Ecom):

#### True Margin Matrix (Corrected 2026-08-30):
```
Net Margin = (Retail / (1 + VAT)) - (Product Cost + Shipping + Import Duty) - (0.03 x Retail)
```

#### Key Financial Metrics:
- **Gross Margin**: Revenue - COGS
- **Net Margin**: Gross margin - operational costs
- **ROAS**: Revenue / Ad Spend (target ≥3.0x)
- **CPA**: Customer acquisition cost benchmark (EUR 21.48)
- **LTV**: Customer lifetime value
- **Conversion Rate**: Revenue / Impressions
- **Inventory Turns**: How frequently inventory sells

#### Compliance Requirements:
- **VAT Treatment**: VAT-inclusive retail, VAT-exclusive margin calculation
- **Import Duties**: €3 per customs item (direct imports), €0 from EU warehouses
- **Payment Fees**: 3% on gross amount, not divided by VAT
- **Minimum Margin**: €15 net margin per sale, 3x COGS minimum

## Department Agents

### Financial Analytics Lead Agent
**Purpose**: Overall financial strategy and compliance
**Skills**: profit-margin-calculator, price-optimization-tool, margin-calculator variants
**Tools**: DuckDB, Metabase, Terminal, Memory
**Directives**: Hermes-Ecom compliance, capital preservation, sustainable growth

### Margin Analysis Agent
**Purpose**: Detailed margin calculations and optimization
**Skills**: margin_solver, profitability, margin-calculator variants
**Tools**: Python execution, Terminal, Memory
**Focus**: True Margin Matrix, CAC gates, retail band enforcement

### ROI Optimization Agent
**Purpose**: Campaign ROI analysis and optimization
**Skills**: sales-tracking-tool, share-of-shelf, price-optimization-tool
**Tools**: Terminal, Memory, Financial APIs
**Objective**: Maximize returns while minimizing risk

### Price Management Agent
**Purpose**: Dynamic pricing and market positioning
**Skills**: price-optimization-tool, minimum-advertised-price, profit-margin-calculator
**Tools**: Terminal, Memory, Market data APIs
**Goal**: Optimal pricing for maximum profitability

## Department Protocols (Financial Discipline):

### Financial Compliance (Hermes-Ecom):
1. **True Margin Matrix**: Corrected formula with VAT and duty considerations
2. **CAC Gate**: Net margin must be ≥2x median CPA (EUR 21.48)
3. **Retail Band**: EUR 62-93 target range (not EUR 30-45)
4. **Margin Floor**: Net margin ≥€15, 3x COGS minimum
5. **VAT Treatment**: VAT-inclusive retail, VAT-exclusive margin calculation
6. **Import Strategy**: EU warehouse fulfilment for duty elimination

### Price Optimization:
1. **Dynamic Pricing**: Adjust based on demand, competition, margins
2. **Minimum Advertised Price**: Enforce price floors
3. **Market Positioning**: Competitive pricing analysis
4. **Volume Discounts**: Bulk pricing for high-volume customers

### Risk Management (Financial):

#### Capital Preservation:
- **Position Sizing**: Maximum 5% per campaign
- **Drawdown Control**: Immediate reduction during volatility
- **Liquidity Protection**: Always maintain cash buffer
- **Cost Discipline**: Zero overhead where alternatives exist

#### Financial Risks:
- **Margin Compression**: Continuous margin monitoring
- **Price Volatility**: Dynamic price adjustments
- **Market Saturation**: Portfolio diversification
- **Currency Risk**: Hedging strategies where needed

### Financial Reporting:
1. **Real-time Tracking**: Live P&L across all campaigns
2. **Scheduled Reports**: Daily, weekly, monthly financial analysis
3. **Dashboard**: Metabase financial reporting
4. **Alerts**: Abnormal financial activity notifications

## Integration Points

### With Campaign Operations:
- Track campaign ROI and profitability
- Provide budget optimization recommendations
- Monitor financial performance vs. projections
- Feed financial data into learning loop

### With Product Validation:
- Calculate True Margin Matrix for all products
- Provide margin targets for pricing strategy
- Share financial insights for product development

### With Creative Production:
- Analyze creative ROI impact on margins
- Provide financial targets for creative messaging
- Share pricing constraints for creative positioning

### With Supply Chain:
- Track fulfilment costs and profitability
- Analyze supplier cost impact on margins
- Optimize total supply chain economics
- Monitor inventory carrying costs

### With Learning & Optimization:
- Feed financial performance into heuristics
- Update pricing strategies based on results
- Identify financial patterns and biases
- Maintain financial calibration log

## Performance Metrics (Hermes-Ecom):

### Financial Quality:
- **Margin Achievement**: Net margin ≥€15 per sale
- **ROAS Performance**: ≥3.0x across all campaigns
- **Price Optimization**: Optimal pricing for maximum profitability
- **Cost Efficiency**: Minimized operational costs

### Risk Metrics:
- **Capital Preservation**: Zero losses from financial mismanagement
- **Drawdown Control**: Immediate reduction during market volatility
- **Position Sizing**: Disciplined exposure limits
- **Diversification**: Broad financial portfolio

### Operational Metrics:
- **Reporting Speed**: Real-time financial tracking
- **Analysis Depth**: Comprehensive financial insights
- **Optimization Frequency**: Regular price and budget adjustments
- **Compliance**: 100% financial regulation adherence

## Technical Specifications

### Financial Analysis Tools:
- **DuckDB**: High-performance financial database
- **Metabase**: Financial reporting and dashboards
- **Python Scripts**: Automated financial calculations
- **Financial APIs**: Real-time market and pricing data

### True Margin Matrix Implementation:
```python
# Corrected formula (2026-08-30)
def true_margin_matrix(retail, vat, cost, shipping, duty):
    net_margin = (retail / (1 + vat)) - (cost + shipping + duty) - (0.03 * retail)
    return net_margin
```

### Price Optimization:
- **Dynamic Pricing**: Real-time price adjustments
- **Minimum Advertised Price**: Price floor enforcement
- **Volume Pricing**: Bulk discounts for high-volume customers
- **Market Positioning**: Competitive pricing analysis

### Financial Reporting:
- **Real-time Dashboard**: Live P&L tracking
- **Scheduled Reports**: Automated financial analysis
- **Performance Alerts**: Abnormal activity notifications
- **Compliance Reporting**: Regulatory adherence tracking

## Command Examples

### Calculate True Margin Matrix:
```
python3 scripts/margin_solver.py --retail 85.00 --cost 12.00 --shipping 4.50 --vat 0.19 --duty 3.0
```

### Analyze Campaign ROI:
```
hdemis -s roi-analysis "Analyze campaign ROI and provide optimization recommendations"
```

### Price Optimization:
```
hdemis -s price-management "Optimize pricing for current product portfolio"
```

### Financial Compliance Check:
```
hdemis -s financial-analytics "Verify all products meet margin and CAC requirements"
```

## Hermes-Ecom Compliance Checklist:
- [ ] True Margin Matrix: Corrected formula with VAT and duty
- [ ] CAC Gate: Net margin ≥2x median CPA (EUR 21.48)
- [ ] Retail Band: EUR 62-93 target range
- [ ] Margin Floor: Net margin ≥€15, 3x COGS minimum
- [ ] VAT Treatment: Proper VAT calculation and reporting
- [ ] Import Strategy: EU warehouse fulfilment for duty elimination
- [ ] Price Optimization: Dynamic pricing based on performance
- [ ] Minimum Advertised Price: Price floor enforcement
- [ ] Risk Management: Capital preservation and drawdown control
- [ ] Position Sizing: Maximum 5% per campaign
- [ ] Reporting: Real-time financial tracking and analysis
- [ ] Compliance: 100% regulatory adherence
- [ ] Optimization: Continuous price and budget optimization
- [ ] Learning: Financial performance into heuristics

## Success Criteria

### Financial Performance:
- **Margin Achievement**: Consistent €15-30 net margin per sale
- **ROAS Performance**: Sustainable 3.0x+ returns
- **Price Optimization**: Optimal pricing for maximum profitability
- **Cost Efficiency**: Minimized operational overhead

### Risk Management:
- **Capital Preservation**: Zero losses from financial mismanagement
- **Drawdown Control**: Immediate response to market volatility
- **Position Sizing**: Disciplined exposure limits
- **Diversification**: Broad financial portfolio

### Operational Excellence:
- **Reporting Speed**: Real-time financial tracking
- **Analysis Depth**: Comprehensive financial insights
- **Optimization Frequency**: Regular adjustments
- **Compliance**: 100% regulatory adherence

## Agency Integration Role

The Financial Analytics Department is the backbone of the Hermes-Ecom drop shipping agency, ensuring that all financial decisions are made with discipline, compliance, and sustainability in mind. It embodies the Hermes-Ecom principle of capital preservation through rigorous financial analysis and risk management.