# Umami Configuration for Hermes-Ecom

## Self-Hosted Cookieless Analytics (MIT License)

### Deployment
Umami runs as a Docker service in the main stack (`docker-compose.yml`), sharing the PostgreSQL database with Medusa.

### Configuration via Environment Variables
| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string (shared with Medusa) | Yes |
| `APP_SECRET` | Encryption key for session/auth (use `JWT_SECRET`) | Yes |
| `HASH_SALT` | Salt for anonymizing IP addresses (generate separately) | Yes |

### Initial Setup
1. After `make up` and `make migrate`, Umami will auto-create tables on first boot
2. Access at `http://127.0.0.1:3000` (or `https://analytics.yourdomain.com` via tunnel)
3. Default login: `admin` / `umami` — **change immediately**
4. Add website: `shop.yourdomain.com`
5. Copy tracking script

### Tracking Script Integration (Next.js Storefront)
Add to `medusa-storefront/src/app/layout.tsx` or create a component:

```tsx
// components/UmamiAnalytics.tsx
'use client';

import Script from 'next/script';
import { usePathname, useSearchParams } from 'next/navigation';
import { useEffect } from 'react';

export default function UmamiAnalytics() {
  const pathname = usePathname();
  const searchParams = useSearchParams();

  useEffect(() => {
    if (window.umami) {
      window.umami.trackView(`${pathname}${searchParams ? '?' + searchParams : ''}`);
    }
  }, [pathname, searchParams]);

  return (
    <Script
      id="umami-script"
      src="https://analytics.yourdomain.com/script.js"
      data-website-id="YOUR_WEBSITE_ID_FROM_UMAMI"
      strategy="lazyOnload"
    />
  );
}
```

Then in `layout.tsx`:
```tsx
import UmamiAnalytics from '@/components/UmamiAnalytics';

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <head>...</head>
      <body>
        {children}
        <UmamiAnalytics />
      </body>
    </html>
  );
}
```

### Data Retention
- Raw events: 365 days (configurable in Umami settings)
- Aggregated metrics: indefinite
- No cookies → no GDPR consent banner needed for EU traffic

### Backup
Umami data lives in the shared PostgreSQL database → covered by `make backup`

### Troubleshooting
| Issue | Fix |
|-------|-----|
| "Cannot connect to database" | Verify `DATABASE_URL` uses `postgres` hostname (Docker service name) |
| Tracking not showing | Check `data-website-id` matches Umami website UUID |
| CSP errors | Add `analytics.yourdomain.com` to `script-src` in CSP header |