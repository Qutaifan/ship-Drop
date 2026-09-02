# Hermes-Ecom Storefront — Deployment Verification Checklist

## Pre-Deployment (on ahmad-thinkbook)

### 1. Prerequisites
- [ ] Ubuntu 22.04+ with Docker Engine 24+ and Docker Compose v2
- [ ] Cloudflare account with domain added to Cloudflare DNS
- [ ] Cloudflare Tunnel (`cloudflared`) installed and authenticated
- [ ] Cloudflare R2 bucket created (free tier: 10GB, zero egress)
- [ ] Free-tier SMTP relay configured (e.g., Brevo 300/day, SendGrid 100/day, Mailgun trial)

### 2. Repository Sync
- [ ] Copy `infra/` folder to ahmad-thinkbook: `/opt/hermes-ecom/infra/`
- [ ] Ensure `medusa/` and `medusa-storefront/` directories exist beside `infra/`
  ```bash
  # On ahmad-thinkbook:
  npx create-medusa-app@latest medusa
  # During setup: choose PostgreSQL, decline managed hosting
  # Then: cd medusa && npx create-next-app@latest storefront --use-npm --tailwind --eslint
  # Or use Medusa starter: npx @medusajs/create-medusa-app@latest medusa-storefront --starter
  ```

### 3. Secrets Generation
```bash
cd /opt/hermes-ecom/infra
cp .env.example .env

# Generate secrets (run each twice - once for JWT_SECRET, once for COOKIE_SECRET, etc.)
openssl rand -base64 32  # JWT_SECRET
openssl rand -base64 32  # COOKIE_SECRET
openssl rand -base64 32  # UMAMI_HASH_SALT
# Set strong passwords for POSTGRES_PASSWORD, LISTMONK_ADMIN_PASSWORD
```

### 4. Configure Real Values in `.env`
- [ ] `POSTGRES_PASSWORD` — strong random string
- [ ] `JWT_SECRET` — 32-byte base64
- [ ] `COOKIE_SECRET` — 32-byte base64
- [ ] `UMAMI_HASH_SALT` — 32-byte base64
- [ ] `LISTMONK_ADMIN_PASSWORD` — strong random string
- [ ] `MEDUSA_BACKEND_URL` — `https://api.yourdomain.com`
- [ ] `STORE_CORS` — `https://shop.yourdomain.com`
- [ ] `ADMIN_CORS` — `https://admin.yourdomain.com`
- [ ] `AUTH_CORS` — `https://shop.yourdomain.com,https://admin.yourdomain.com`
- [ ] `NEXT_PUBLIC_MEDUSA_BACKEND_URL` — `https://api.yourdomain.com`
- [ ] `NEXT_PUBLIC_BASE_URL` — `https://shop.yourdomain.com`
- [ ] `R2_ACCOUNT_ID`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_BUCKET`, `R2_ENDPOINT_URL`, `R2_PUBLIC_DOMAIN` — from Cloudflare R2
- [ ] `DATABASE_URL` — auto-constructed from above, verify format

## Deployment Steps

### 5. Build and Start Stack
```bash
cd /opt/hermes-ecom/infra
make up
```

### 6. Run Migrations
```bash
make migrate
```

### 7. Create Admin User
```bash
make admin EMAIL=admin@yourdomain.com PASSWORD=strong-random-password
```

### 8. Verify Services Health
```bash
make ps
# All services should show "healthy" or "Up"

# Health endpoints (all on localhost):
# - Medusa API:    http://127.0.0.1:9000/health
# - Storefront:    http://127.0.0.1:8000
# - Umami:         http://127.0.0.1:3000
# - Uptime Kuma:   http://127.0.0.1:3001
# - Listmonk:      http://127.0.0.1:9001
```

### 9. Configure Cloudflare Tunnel
```bash
# On ahmad-thinkbook:
cloudflared tunnel login
cloudflared tunnel create hermes-shop
# Note the TUNNEL-UUID output

# Edit config.yml with real UUID and hostnames:
# tunnel: <TUNNEL-UUID>
# credentials-file: /etc/cloudflared/<TUNNEL-UUID>.json
# ingress hostnames: api.yourdomain.com, shop.yourdomain.com, analytics.yourdomain.com

cloudflared tunnel route dns hermes-shop api.yourdomain.com
cloudflared tunnel route dns hermes-shop shop.yourdomain.com
cloudflared tunnel route dns hermes-shop analytics.yourdomain.com

# Run tunnel (as systemd service for production):
sudo cloudflared service install
sudo systemctl enable cloudflared
sudo systemctl start cloudflared
```

### 10. Verify Public Access
- [ ] `https://api.yourdomain.com/health` → returns JSON health check
- [ ] `https://shop.yourdomain.com` → loads Next.js storefront
- [ ] `https://analytics.yourdomain.com` → loads Umami dashboard (login with admin user created in Umami)
- [ ] TLS certificate valid (Cloudflare issues automatically)

### 11. Configure Umami
- [ ] Log in at `https://analytics.yourdomain.com`
- [ ] Add website: `shop.yourdomain.com`
- [ ] Copy tracking script to Medusa storefront `layout.tsx` or `_document.tsx`
- [ ] Verify events flowing in real-time dashboard

### 12. Configure Listmonk
- [ ] Log in at `https://lists.yourdomain.com` (add DNS route for lists.yourdomain.com → localhost:9001)
- [ ] Configure SMTP settings (free-tier relay credentials)
- [ ] Create transactional templates for: welcome, abandoned cart, post-purchase, win-back
- [ ] Test send to verify deliverability

### 13. Test Full Order Flow
- [ ] Add product to cart on storefront
- [ ] Complete checkout (test mode in Stripe)
- [ ] Verify order appears in Medusa admin at `https://admin.yourdomain.com`
- [ ] Verify email received via Listmonk
- [ ] Verify analytics event in Umami

### 14. Configure Backups
```bash
# Add R2 credentials to .env (already in .env.example)
# Test backup:
make backup
# Verify backup appears in Cloudflare R2 bucket
```

### 15. Set Up Monitoring
- [ ] Add uptime checks in Uptime Kuma for:
  - `https://api.yourdomain.com/health`
  - `https://shop.yourdomain.com`
  - `https://analytics.yourdomain.com`
- [ ] Configure notifications (Telegram, email, etc.)
- [ ] Test alert by stopping a container

## Post-Deployment

### 16. Security Hardening
- [ ] All services bind only to 127.0.0.1 (verified by `validate_infra.py`)
- [ ] No ports exposed on public interfaces
- [ ] Cloudflare WAF enabled (free plan includes basic rules)
- [ ] Rate limiting on /admin and /auth endpoints via Cloudflare

### 17. Documentation
- [ ] Record domain, tunnel UUID, and all endpoints in team wiki
- [ ] Document `.env` location and backup procedure
- [ ] Note R2 bucket name and credentials location

### 18. Handoff to Creative/Ads Team
- [ ] Create kanban task for `dropship-creative-ads` to build first product pages
- [ ] Create kanban task for `dropship-product-research` to integrate first live product
- [ ] Provide storefront URL and Medusa admin credentials

## Rollback Plan
```bash
# Quick rollback (keeps data):
make down && make up

# Full rollback (restore from R2):
# 1. Download latest backup from R2
# 2. Stop stack: make down
# 3. Restore Postgres: docker compose exec -T postgres psql -U medusa -d medusa < backup.sql
# 4. Start stack: make up
```

## Known Risks (Accepted for Testing Phase)
- Residential ISP uptime — no SLA
- Dynamic IP — Cloudflare Tunnel handles this automatically
- Single point of failure (one host) — revisit before scaling past validation spend
- No CDN caching for dynamic Medusa API — Cloudflare caches static assets only

## Cost Summary
| Item | Cost |
|------|------|
| Domain | ~€10/year |
| Cloudflare Tunnel, DNS, CDN, WAF | €0 (free tier) |
| Cloudflare R2 (10GB) | €0 (free tier) |
| SMTP relay (free tier) | €0 |
| Hardware (ahmad-thinkbook) | €0 (already running) |
| **Total marginal cost** | **€0/month** |

## Support Contacts
- Infrastructure: dropship-storefront-tech
- Creative/Ads: dropship-creative-ads
- Product Research: dropship-product-research