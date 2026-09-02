# Creative Production Department - Hermes-Ecom Drop Shipping Agency

## Department Mandate
**Primary Function**: Generate viral creative assets and conversion-optimized landing pages for validated products using AI and programmatic production.

### Key Objectives:
- Produce 3 distinct creative hooks per product (PROTOCOL-02)
- Create conversion-optimized landing pages
- Maintain zero marginal cost for creative production
- Integrate with Remotion for programmatic 9:16 video compilation
- Support both test phase (local GPU) and winner phase (Veo)
- Ensure brand consistency and campaign effectiveness

## Department Skills & Tools

### Core Skills Required:
- **comfyui-product-staging** - AI image generation and staging
- **remotion-video-ads** - Programmatic video production
- **tiktok-shop-content-strategy** - Vertical video strategy
- **ecommerce-video-marketing** - Video marketing expertise
- **product-description-generator** - Copywriting
- **ecommerce-landing-page** - Landing page optimization
- **ecommerce-personalization** - User-specific creative
- **visual-regression-testing** - Quality assurance
- **shoppable-video** - Direct response capabilities

### Critical Tools:
- **ComfyUI (local RTX 4060)** - Unlimited AI image/video generation for testing
- **Remotion** - Programmatic video compilation (9:16 vertical)
- **Veo (Google AI)** - Cinematic production for proven winners only
- **AI Image Gen** - Product visualization and lifestyle imagery
- **Video Analysis** - Performance measurement and optimization
- **Terminal** - Workflow automation and batch processing

### Creative Production Workflow (Hermes-Ecom):

#### Test Phase (Local GPU - Zero Cost):
1. **Hook Generation**: Create 3 variants (problem, transformation, aspirational)
2. **Visual Production**: Use ComfyUI + IC-Light + BiRefNet for product shots
3. **A/B Testing**: Ship 40+ variants to identify winners
4. **Local GPU Advantage**: Unlimited generations for testing

#### Winner Phase (Veo - Measured Cost):
1. **Re-shoot Proven Hooks**: Use Veo for cinematic quality
2. **Native Audio Integration**: Veo provides authentic soundtrack
3. **Scale Production**: Limited credits for winners only
4. **Creative Inversion**: Stop AI creative above ~$100 AOV (ROAS 3.7x vs 3.1x)

## Department Agents

### Creative Production Lead Agent
**Purpose**: Oversee creative workflow and quality control
**Skills**: comfyui-product-staging, remotion-video-ads, ecommerce-video-marketing
**Tools**: ComfyUI, Remotion, Veo, image_gen, terminal
**Directives**: Zero-cost testing first, measured scaling later, anti-AI-overhead discipline

### Hook Development Agent
**Purpose**: Generate and optimize creative hooks (3 per product)
**Skills**: product-description-generator, ecommerce-personalization, tiktok-shop-content-strategy
**Tools**: AI image generation, video analysis, terminal
**Output**: 3 distinct creative briefs + visual assets

### Landing Page Agent
**Purpose**: Build conversion-optimized landing pages
**Skills**: ecommerce-landing-page, shoppable-video, visual-regression-testing
**Tools**: web design tools, terminal, browser
**Focus**: No-account checkout, Apple/Google Pay integration

### Quality Assurance Agent
**Purpose**: Ensure creative effectiveness and brand consistency
**Skills**: visual-regression-testing, ecommerce-video-marketing
**Tools**: regression testing, performance analytics
**Standard**: 4.5+ star equivalent visual quality

## Department Protocols (PROTOCOL-02):

### Creative Brief Generation:
1. **Ad Hook 1 (Problem-Oriented)**: Deep customer pain point in first 3 seconds
2. **Ad Hook 2 (Transformation)**: Visual before-and-after showing immediate change
3. **Ad Hook 3 (Aspirational Lifestyle)**: Product in high-end desirable environment
4. **Landing Page Framework**:
   - Above-the-Fold: Clear hero statement, high-quality visuals, trust badges
   - Social Proof: 4.5+ star reviews, customer lifestyle photos
   - Checkout: Integrated Stripe ExpressCheckout, Apple/Google Pay
   - No-Account: Direct frictionless one-click checkout

### Remotion Programmatic Video Scaffold:
- **JSON Props Schema**: Parameterizable creative generation
- **9:16 Vertical Format**: Mobile-first optimization
- **Batch Processing**: Automated asset compilation
- **Quality Control**: Visual regression testing

### AI Creative Integration:
- **Test Phase**: Unlimited local Wan generations (RTX 4060)
- **Winner Phase**: Veo re-shoots with native audio
- **Creative Penalty**: Above ~$100 AOV, human creative beats AI (ROAS 3.7x vs 3.1x)
- **SynthID Watermark**: EU AI Act compliance, no watermark stripping

## Risk Management (Creative Risks):

### Cost Control:
- **Zero-Cost Testing**: Local GPU generation for first 40 variants
- **Measured Scaling**: Veo only for proven concepts
- **Creative Inversion**: Stop AI above ~$100 AOV
- **Budget Allocation**: 90% testing, 10% scaling

### Quality Assurance:
- **Brand Consistency**: All assets follow brand guidelines
- **Visual Regression**: Automated quality testing
- **Performance Testing**: A/B against proven creative
- **Localization**: 9:16 vertical video standard

### Creative Risks:
- **AI Dependency**: Fallback to human creative for high-AOV products
- **Platform Changes**: Adapt creative format for TikTok/IG Reels
- **Performance Degradation**: Continuous optimization based on metrics
- **Regulatory Compliance**: EU AI Act disclosures on AI imagery

## Integration Points

### With Product Validation:
- Receive validated products for creative production
- Apply creative insights to hook development
- Provide creative performance feedback for learning loop

### With Campaign Operations:
- Supply creative assets for campaign launch
- Monitor creative performance and ROI
- Optimize creative based on A/B test results

### With Learning & Optimization:
- Feed creative performance data into heuristics
- Identify high-performing creative patterns
- Update creative strategy based on results

## Performance Metrics:

### Creative Quality:
- **Hook Production Rate**: 3 hooks per validated product
- **Asset Quality**: 4.5+ star equivalent visual quality
- **Testing Volume**: 40+ variants per product (test phase)
- **Conversion Optimization**: A/B tested against proven baselines

### Cost Efficiency:
- **Test Phase Cost**: €0 (local GPU)
- **Scaling Cost**: Measured (Veo credits only)
- **Creative Inversion ROI**: Human creative beats AI above ~$100 AOV
- **Production Speed**: Rapid iteration and optimization

### Campaign Impact:
- **Hook Performance**: CTR improvement across campaigns
- **Conversion Rate**: Landing page optimization results
- **Brand Consistency**: Uniform visual presentation
- **Platform Optimization**: 9:16 vertical video standard

## Technical Specifications

### Local GPU Setup (RTX 4060):
- **Software**: ComfyUI, IC-Light, BiRefNet
- **Capacity**: Unlimited generations for testing
- **Format**: 9:16 vertical video
- **Quality**: High-fidelity product visualization

### Veo Integration:
- **Provider**: Google AI Plus/Pro/Ultra (50-10,000 credits/month)
- **Usage**: Winners only (5% of concepts)
- **Advantages**: Native audio, cinematic quality
- **Limitations**: Credit constraints, commercial use restrictions

### Remotion Pipeline:
- **Input**: JSON props schema
- **Process**: Automated video compilation
- **Output**: 9:16 vertical videos ready for platforms
- **Quality**: Consistent branding and formatting

## Command Examples

### Generate Creative Briefs:
```
python3 scripts/generate_brief.py --product "high-ticket modular wall shelf" \
  --hooks 3 --format remotion --vertical
```

### Run Remotion Compilation:
```
remotion render "creative-brieffs/wall-shelf.json" \
  --output /campaigns/wall-shelf/episode-1
```

### Quality Check:
```
python3 scripts/selftest.py --creative --visual-regression --product "wall-shelf"
```

### A/B Creative Performance:
```
hdemis -s creative-production "Analyze creative performance of problem vs aspirational hooks"
```

## Hermes-Ecom Compliance Checklist:
- [ ] Test Phase: Unlimited local generations
- [ ] Winner Phase: Measured Veo scaling
- [ ] Creative Inversion: Human creative above ~$100 AOV
- [ ] 3+1 Creative Output: Problem, transformation, aspirational + landing page
- [ ] Remotion Integration: Programmatic video compilation
- [ ] Quality Control: Visual regression testing
- [ ] Platform Optimization: 9:16 vertical video
- [ ] Budget Allocation: 90% testing, 10% scaling
- [ ] EU AI Act Compliance: SynthID watermark
- [ ] Anti-Fragility: Human fallback for high-AOV products

## Success Criteria

### Creative Excellence:
- **Hook Innovation**: Proven creative outperforms baseline
- **Conversion Optimization**: Landing pages achieve >2% CVR
- **Brand Consistency**: All assets pass visual regression
- **Platform Fit**: 9:16 videos optimized for mobile

### Cost Management:
- **Testing ROI**: €0 cost for 40+ variants
- **Scaling Efficiency**: Measured cost for winners only
- **Creative Inversion**: Budget shifted to human creative for high-AOV
- **Production Speed**: Rapid iteration without quality compromise

### Campaign Integration:
- **Ad Performance**: Creative contributes to 3.0x+ ROAS
- **Conversion Rate**: Above 2% average across products
- **Brand Impact**: Consistent visual identity across campaigns
- **Market Response**: Positive consumer engagement metrics

## Agency Integration Role

The Creative Production Department is the bridge between product validation and campaign success, transforming validated opportunities into compelling marketing assets that drive conversion while maintaining strict cost discipline and creative quality standards.