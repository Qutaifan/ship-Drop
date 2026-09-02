# Listmonk Configuration for Hermes-Ecom

## Self-Hosted Email Sequences (AGPL-3.0)

### Deployment
Listmonk runs as a Docker service in the main stack (`docker-compose.yml`), sharing the PostgreSQL database with Medusa and Umami.

### Configuration via Environment Variables
| Variable | Description | Required |
|----------|-------------|----------|
| `LISTMONK_DATABASE_HOST` | PostgreSQL host (`postgres` in Docker network) | Yes |
| `LISTMONK_DATABASE_USER` | PostgreSQL user (same as Medusa) | Yes |
| `LISTMONK_DATABASE_PASSWORD` | PostgreSQL password (same as Medusa) | Yes |
| `LISTMONK_DATABASE_NAME` | PostgreSQL database (same as Medusa) | Yes |
| `LISTMONK_DATABASE_SSL_MODE` | `disable` for local Docker network | Yes |
| `LISTMONK_APP_ADMIN_USERNAME` | Admin username for Listmonk UI | Yes |
| `LISTMONK_APP_ADMIN_PASSWORD` | Strong password for admin | Yes |
| `LISTMONK_APP_ADDRESS` | Bind address (`0.0.0.0:9000` inside container) | Yes |

### Initial Setup
1. After `make up`, Listmonk auto-migrates schema on first boot
2. Access at `http://127.0.0.1:9001` (or via tunnel at `https://lists.yourdomain.com`)
3. Log in with `LISTMONK_ADMIN_USER` / `LISTMONK_ADMIN_PASSWORD`
4. **Immediately configure SMTP** before sending any email

### SMTP Configuration (Free-Tier Relay)
Configure in Listmonk UI → Settings → SMTP:

| Provider | Free Tier | Host | Port | Auth |
|----------|-----------|------|------|------|
| **Brevo (Sendinblue)** | 300 emails/day | smtp-relay.brevo.com | 587 | API key as username |
| **SendGrid** | 100 emails/day | smtp.sendgrid.net | 587 | API key as username |
| **Mailgun** | Trial only | smtp.mailgun.org | 587 | API key as username |
| **Amazon SES** | 62,000/mo if in EC2 | email-smtp.region.amazonaws.com | 587 | SMTP credentials |

**Recommended: Brevo** — highest free daily volume, EU-based, good deliverability.

### Required Transactional Templates

Create these in Listmonk UI → Templates → New:

#### 1. Welcome Email (`welcome`)
**Subject:** Welcome to {{ .StoreName }} — here's 10% off your first order
**Body (HTML):**
```html
<h1>Welcome to {{ .StoreName }}!</h1>
<p>Hi {{ .FirstName }},</p>
<p>Thanks for joining us. Here's a welcome code for 10% off:</p>
<p style="font-size: 1.5rem; font-weight: bold;">{{ .DiscountCode }}</p>
<p><a href="{{ .StoreURL }}">Start shopping</a></p>
<p>— The {{ .StoreName }} Team</p>
```

#### 2. Abandoned Cart (`abandoned-cart`)
**Subject:** You left something behind — {{ .CartItemName }}
**Body (HTML):**
```html
<h1>Your cart is waiting</h1>
<p>Hi {{ .FirstName }},</p>
<p>You added <strong>{{ .CartItemName }}</strong> to your cart but didn't check out.</p>
<p><a href="{{ .CartRecoveryURL }}">Complete your order</a></p>
<p>Expires in 24 hours.</p>
<p>— The {{ .StoreName }} Team</p>
```

#### 3. Order Confirmation (`order-confirmation`)
**Subject:** Order #{{ .OrderNumber }} confirmed — {{ .StoreName }}
**Body (HTML):**
```html
<h1>Order Confirmed</h1>
<p>Hi {{ .FirstName }},</p>
<p>Thanks for your order <strong>#{{ .OrderNumber }}</strong>.</p>
<p><strong>Total:</strong> {{ .OrderTotal }}</p>
<p><strong>Items:</strong></p>
<ul>
{{ range .LineItems }}<li>{{ .Title }} × {{ .Quantity }} — {{ .Total }}</li>{{ end }}
</ul>
<p>We'll notify you when it ships.</p>
<p><a href="{{ .OrderURL }}">View order</a></p>
<p>— The {{ .StoreName }} Team</p>
```

#### 4. Shipping Confirmation (`shipping-confirmation`)
**Subject:** Your order #{{ .OrderNumber }} has shipped 📦
**Body (HTML):**
```html
<h1>It's on the way!</h1>
<p>Hi {{ .FirstName }},</p>
<p>Order <strong>#{{ .OrderNumber }}</strong> has shipped.</p>
<p><strong>Tracking:</strong> <a href="{{ .TrackingURL }}">{{ .TrackingNumber }}</a></p>
<p><strong>Carrier:</strong> {{ .Carrier }}</p>
<p>Estimated delivery: {{ .EstimatedDelivery }}</p>
<p>— The {{ .StoreName }} Team</p>
```

#### 5. Post-Purchase Review Request (`review-request`)
**Subject:** How's your {{ .ProductName }}? 🌟
**Body (HTML):**
```html
<h1>Loving your {{ .ProductName }}?</h1>
<p>Hi {{ .FirstName }},</p>
<p>It's been a couple weeks since your order #{{ .OrderNumber }} arrived.</p>
<p><a href="{{ .ReviewURL }}">Leave a review</a> — it helps others and earns you {{ .ReviewIncentive }} off next order.</p>
<p>— The {{ .StoreName }} Team</p>
```

#### 6. Win-Back / Re-engagement (`win-back`)
**Subject:** We miss you — here's 15% off {{ .StoreName }}
**Body (HTML):**
```html
<h1>Come back for 15% off</h1>
<p>Hi {{ .FirstName }},</p>
<p>It's been a while. Here's a code to welcome you back:</p>
<p style="font-size: 1.5rem; font-weight: bold;">{{ .DiscountCode }}</p>
<p><a href="{{ .StoreURL }}">Shop now</a></p>
<p>Expires in 7 days.</p>
<p>— The {{ .StoreName }} Team</p>
```

### Medusa Integration (Webhooks)
Configure in Medusa Admin → Settings → Webhooks:

| Event | Listmonk Endpoint | Template |
|-------|-------------------|----------|
| `customer.created` | `POST https://lists.yourdomain.com/api/tx` | `welcome` |
| `cart.abandoned` | `POST https://lists.yourdomain.com/api/tx` | `abandoned-cart` |
| `order.placed` | `POST https://lists.yourdomain.com/api/tx` | `order-confirmation` |
| `order.shipped` | `POST https://lists.yourdomain.com/api/tx` | `shipping-confirmation` |
| `order.delivered` (delay 14 days) | `POST https://lists.yourdomain.com/api/tx` | `review-request` |
| `customer.inactive` (90 days) | `POST https://lists.yourdomain.com/api/tx` | `win-back` |

**Webhook payload format for Listmonk transactional API:**
```json
{
  "template_id": 1,
  "subscriber_email": "customer@example.com",
  "data": {
    "FirstName": "John",
    "StoreName": "Hermes Shop",
    "StoreURL": "https://shop.yourdomain.com",
    "DiscountCode": "WELCOME10",
    "CartItemName": "Premium Pepper Grinder",
    "CartRecoveryURL": "https://shop.yourdomain.com/cart/recover/abc123",
    "OrderNumber": "ORD-2026-001",
    "OrderTotal": "€79.90",
    "LineItems": [...],
    "TrackingNumber": "1Z999AA10123456784",
    "TrackingURL": "https://track.example.com/1Z999AA10123456784",
    "Carrier": "DHL",
    "EstimatedDelivery": "2026-09-15",
    "ProductName": "Premium Pepper Grinder",
    "ReviewURL": "https://shop.yourdomain.com/review/ORD-2026-001",
    "ReviewIncentive": "10%"
  }
}
```

### Medusa → Listmonk Webhook Handler (Edge Function)
Create `medusa/src/api/middlewares.ts` or a separate worker to transform Medusa events → Listmonk transactional API calls. The Listmonk transactional endpoint expects:
```
POST /api/tx
Authorization: Bearer <LISTMONK_API_KEY>
Content-Type: application/json

{
  "template_id": 1,
  "subscriber_email": "user@example.com",
  "data": { ... }
}
```

### Compliance (GDPR / CAN-SPAM)
- [ ] Double opt-in enabled for marketing lists (not required for transactional)
- [ ] Unsubscribe link in every email footer
- [ ] Physical address in footer (registered business address)
- [ ] Data retention policy: delete subscriber data on request
- [ ] Transactional emails exempt from consent — but keep audit trail

### Backup
Listmonk data lives in shared PostgreSQL → covered by `make backup`

### Troubleshooting
| Issue | Fix |
|-------|-----|
| "Authentication failed" | Verify SMTP username/password — Brevo uses API key as username, not email |
| Emails going to spam | Warm up domain, add SPF/DKIM/DMARC in Cloudflare DNS |
| "Database connection failed" | Verify `LISTMONK_DATABASE_HOST=postgres` (Docker service name) |
| Webhook 401 | Generate API key in Listmonk UI → Settings → API Keys |