---
name: crawlee-scraper
description: Scrape e-commerce competitor catalogs, extract customer reviews, and monitor pricing changes using Crawlee and Playwright with automatic anti-bot stealth and session management.
---

# Crawlee E-Commerce Scraper Skill

This skill teaches agents how to construct resilient, production-grade e-commerce scrapers using **Crawlee (TypeScript/Python)** without incurring paid proxy fees.

---

## 1. Why Crawlee over Raw Playwright/Puppeteer

- **Built-in Session Pools & Fingerprint Rotation**: Automatically rotates browser fingerprints to avoid Cloudflare/anti-bot blocks.
- **Request Queues & Auto-Retries**: Handles network timeouts, exponential backoff, and pagination without custom boilerplate.
- **Storage Management**: Automatically dumps structured datasets to JSON/CSV.

---

## 2. Competitor Catalog & Review Scraper Pattern

```typescript
import { PlaywrightCrawler, Dataset } from 'crawlee';

export const crawler = new PlaywrightCrawler({
  maxRequestsPerCrawl: 50,
  headless: true,
  // Use stealth browser fingerprints
  browserPoolOptions: {
    useFingerprints: true,
  },

  async requestHandler({ request, page, log }) {
    log.info(`Processing URL: ${request.url}`);

    // Wait for product title and pricing elements
    await page.waitForSelector('h1');

    const title = await page.title();
    const priceText = await page.locator('.price, [data-price], [class*="price"]').first().textContent();
    
    // Extract customer reviews for hook mining
    const reviewElements = await page.locator('.review-text, [data-review-text], .customer-review').all();
    const reviews: string[] = [];
    for (const el of reviewElements.slice(0, 10)) {
      const text = await el.textContent();
      if (text) reviews.push(text.trim());
    }

    // Save structured dataset
    await Dataset.pushData({
      url: request.url,
      title: title.trim(),
      priceText: priceText?.trim(),
      reviews,
      scrapedAt: new Date().toISOString(),
    });
  },

  async failedRequestHandler({ request, log }) {
    log.error(`Request failed permanently: ${request.url}`);
  },
});

// Run against target competitor product pages
// await crawler.run(['https://competitor-store.com/products/example-item']);
```

---

## 3. Review Mining for Direct-Response Ad Hooks
When scraping competitor product pages, extract customer reviews matching:
1. **Pain Frustrations** (*"I hated when..."*, *"Every time I tried to..."*): Feeds **Hook 1 (Problem-Oriented)**.
2. **Transformations** (*"In 2 minutes it changed..."*, *"Now my desk is..."*): Feeds **Hook 2 (Transformation)**.
3. **Surprise Benefits** (*"I was skeptical but..."*, *"Much sturdier than expected"*): Feeds Landing Page Social Proof & FAQ.

---

## 4. Operational Guardrails
- **Zero Scraping of Meta / TikTok Ad Libraries**: Scrapers violate platform terms and risk banning the primary ad-buying accounts. Use the official `scripts/ad_library.py` API client for competitor ad research.
