# US Market - Campaign Operations

## Platform Differences (US vs EU)

### TikTok
- **CPM**: $8-15 (US) vs $4-8 (EU) — US ~2x
- **Top verticals**: Beauty, fashion, home, fitness, gadgets
- **Targeting**: 18-34 over-indexed; 35-54 growing
- **Creative style**: Faster pace, more text overlay, native American voice
- **Restrictions**: Few — but health/finance claims heavily policed

### Meta (Facebook + Instagram)
- **CPM**: $12-25 (US) vs $5-12 (EU) — US ~2x
- **Top verticals**: E-com, fitness, beauty, home
- **iOS 14.5+ impact**: Harder attribution; use CAPI + UTM-based attribution
- **Advantage+ Shopping**: Strong for US e-com — let Meta optimize placements
- **Restrictions**: Health claims, financial claims, before/after weight loss

### Google Shopping
- **Required**: Google Merchant Center account, product feed
- **Free to set up**; CPC $0.50-2.50 for e-com
- **Best for**: High-intent, branded, comparison shopping
- **Less viral**: No discovery / interest-based

### Pinterest
- **High US penetration**: 85M+ monthly active US users
- **CPM**: $5-12 (US, lower than TikTok/Meta)
- **Best for**: Home, fashion, beauty, wedding, DIY
- **Creative**: Vertical pins, lifestyle, less aggressive selling

## US-Specific Ad Compliance

### FTC Requirements
- **#ad / #sponsored** disclosure on every paid post (clear, conspicuous, BEFORE the link)
- **No "free" claims** that aren't actually free
- **Before/after**: must be typical, not best case
- **Testimonials**: must reflect typical results
- **Earnings claims**: must have substantiation
- **Pricing**: must show total cost (incl. shipping/fees) before checkout

### TCPA (Text Marketing)
- **Prior express written consent** required for marketing texts
- **Opt-out** must be honored within 10 days
- **Quiet hours** (before 8am / after 9pm recipient's time) per FCC

### CAN-SPAM (Email)
- **Working opt-out** in every email
- **Honored within 10 days**
- **Accurate header/subject**
- **Physical postal address** in every email
- **No deceptive subject lines**

### State-Specific
- **California (CCPA/CPRA)**: Right to delete, opt-out of sale; cookie banner required
- **New York**: Stop Addictive Feeds for Kids (under 18)
- **Texas**: Minor protection rules
- **Florida**: Telemarketing restrictions

## Creative Differences (US vs EU)

| Element | US Preference | EU Preference |
|---|---|---|
| Pacing | Fast, 1-2 sec cuts | Slower, 3-4 sec holds |
| Voice | Direct, bold, American accent | Subtle, less aggressive |
| Humor | Slapstick, self-deprecating | Ironic, dry |
| Price display | "$XX" or "Under $XX" | "€XX" with VAT note |
| Social proof | "Join 50,000+ Americans" | "Trusted by 10,000+ customers" |
| Shipping | "FREE 2-day shipping" | "Free shipping over €30" |
| Returns | "30-day free returns" | "14-day return policy" |

## US-Specific Target Audiences

### High-Value E-com Segments
- **New parents** (0-3 yr olds): high spend, gift-giving
- **Pet owners** (especially dog): discretionary income, emotional
- **Homeowners 25-40**: home improvement, organization
- **Fitness enthusiasts**: gym members, runners, yoga
- **Aging boomers** (55+): health, comfort, home mods

### Demographic Wedges
- **Hispanic/Latino**: 19% of US population, growing e-com share
- **Asian American**: Highest median income of any demographic
- **Rural vs urban**: Different platform usage (rural = Facebook heavy)
- **Income targeting**: Meta removed detailed income targeting 2022; use proxies

## US Sales Tax Filing Reality

For a dropshipper at small scale:
- **Use free Avalara TaxJar calculator** to determine nexus state
- **Register** in states where nexus triggered (~$0-100/yr each)
- **File monthly or quarterly** via state portals (mostly free)
- **Streamlined Sales Tax (SST)**: Register once, file once for 24 states

**SST is the free OSS-equivalent for US.** Use it. https://www.streamlinedsalestax.org/

## US Customer Service

- **Hours**: 9am-9pm ET minimum (covers all time zones)
- **Phone**: Required for trust; free option is Google Voice + IVR
- **Chat**: Industry standard, many free tiers (Tidio, Crisp free)
- **Response SLA**: 4h chat, 24h email
- **Returns**: Free returns = competitive necessity (~$7-12 per return; budget into margin)

## US Shipping Options

### Free Shipping Threshold Strategy
- **Amazon effect**: Free shipping is expected, but not for sub-$35
- **Recommended**: Free shipping on $50+, $5.99 flat under $50
- **Disclose in ad**: "Free shipping over $50" is a strong hook

### Carrier Mix
- **USPS First Class**: <1 lb, 3-5 day, $3-5
- **USPS Priority Mail**: 1-3 lb, 1-3 day, $7-10
- **UPS Ground**: 1-5 day, $8-12
- **FedEx Home Delivery**: 2-7 day residential, $9-13
- **Free 2-day**: Use Deliverr/ShipBob 2-day for Amazon-level expectations

## US Payment Optimization

### Stripe US Features
- **Apple Pay / Google Pay**: ~30% conversion lift, must enable
- **Shop Pay** (Shopify): Faster checkout
- **ACH Direct Debit**: For B2B or high-AOV
- **Affirm/Klarna/AfterPay**: BNPL, expected for $50+ AOV

### Conversion Rate Optimization
- **Trust badges**: BBB, Norton, McAfee, Trustpilot
- **Free shipping display**: Show in cart, not surprise at checkout
- **Single-page checkout**: Multi-step drops 20-30%
- **Address autocomplete**: USPS API is free
- **Guest checkout**: Required, no forced account creation

## US Tax Reporting (1099, sales tax)

- **1099-K** (Stripe/PayPal): Issued if >$600/year (changed from $20K/200 txn threshold 2024)
- **Income tax**: Self-employment tax on net profit (15.3% + federal + state)
- **Sales tax**: Remit monthly/quarterly per state rules
- **Duties paid**: Recoverable as COGS

**Tools (mostly free)**:
- Wave / FreshBooks for invoicing
- Free TurboTax or Cash App Tax for returns
- SST for sales tax

## US Launch Checklist

Before going live on US market:
- [ ] US 3PL selected + first inventory shipped
- [ ] Stripe US account configured (Apple Pay, Google Pay, Link)
- [ ] Sales tax registration in home state + high-volume states
- [ ] FTC-compliant ad copy (clear pricing, disclosures, claims substantiated)
- [ ] Cookie consent banner (CCPA-compliant)
- [ ] 30-day return policy published
- [ ] Privacy policy + terms of service
- [ ] Physical address in footer (required by CAN-SPAM)
- [ ] Customer service contact (email + phone)
- [ ] US-specific creative (American voice, US pricing, US social proof)
- [ ] TikTok/Meta pixel + CAPI configured for US storefront
