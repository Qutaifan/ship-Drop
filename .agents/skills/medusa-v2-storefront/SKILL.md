---
name: medusa-v2-storefront
description: Architect, configure, and optimize headless e-commerce storefronts on Medusa v2 with Next.js 15+, Stripe Express Checkout (Apple/Google Pay), EU IOSS tax handling, and cookieless Umami analytics.
---

# Medusa v2 Storefront & Checkout Optimization Skill

This skill provides architectural patterns and code blueprints for high-converting, headless e-commerce storefronts using **Medusa v2** and **Next.js**.

---

## 1. Core Architecture Principles

```
Next.js 15+ Storefront (Cloudflare Tunnel / Pages)
        │
        ▼ (Typed Store API / SDK)
Medusa v2 Backend (127.0.0.1:9000)
  ├── medusa-server  ──► HTTP Routes, CORS, Auth
  └── medusa-worker  ──► Scheduled Workflows, Order Processing, Email Subscribers
        │
        ├── PostgreSQL 16 (Relational DB)
        └── Valkey 8 (Task Queue & Cache)
```

---

## 2. 1-Tap Stripe Express Checkout (Apple Pay & Google Pay)

To achieve maximum mobile conversion on paid dropshipping traffic ($\ge 2.5\%$ CVR), implement Stripe's `ExpressCheckoutElement`:

### Next.js Client Component
```tsx
'use client';

import React from 'react';
import { ExpressCheckoutElement, useElements, useStripe } from '@stripe/react-stripe-js';
import { StripeExpressCheckoutElementConfirmEvent } from '@stripe/stripe-js';

export function ExpressCheckout({ cartId, onComplete }: { cartId: string; onComplete: () => void }) {
  const stripe = useStripe();
  const elements = useElements();

  const handleConfirm = async (event: StripeExpressCheckoutElementConfirmEvent) => {
    if (!stripe || !elements) return;

    // 1. Sync shipping address from Apple/Google Wallet to Medusa Cart
    const { shippingAddress, billingDetails } = event;
    // 2. Submit payment intent
    const { error } = await stripe.confirmPayment({
      elements,
      clientSecret: event.clientSecret,
      confirmParams: {
        return_url: `${window.location.origin}/order/confirmed`,
      },
    });

    if (error) {
      console.error('Express checkout error:', error.message);
    } else {
      onComplete();
    }
  };

  return (
    <div className="w-full my-4">
      <ExpressCheckoutElement
        onConfirm={handleConfirm}
        options={{
          buttonHeight: 50,
          buttonTheme: { applePay: 'black', googlePay: 'black' },
          paymentMethods: { applePay: 'auto', googlePay: 'auto' },
        }}
      />
    </div>
  );
}
```

---

## 3. EU IOSS & Multi-Region Tax Rules

In Medusa v2, tax rates are configured per region:
- **Germany (DE)**: 19% VAT
- **France (FR)**: 20% VAT
- **Netherlands (NL)**: 21% VAT
- **Italy (IT)**: 22% VAT
- **Spain (ES)**: 21% VAT

All B2C prices are displayed VAT-inclusive on the product page (PDP), with destination-specific VAT calculated automatically during cart checkout for single-point IOSS tax filing.

---

## 4. Performance & Core Web Vitals (Mobile LCP < 1.2s)
- **Partial Prerendering (PPR)**: Statically prerender PDP layout, shell, and reviews; dynamically stream cart state and real-time inventory.
- **Modern Image Optimization**: Serve WebP/AVIF from Cloudflare R2 with explicit `fetchpriority="high"` on above-the-fold hero images.
- **Cookieless Analytics**: Use self-hosted Umami (`127.0.0.1:3000`) for privacy-first tracking without GDPR consent popups slowing down page load.
