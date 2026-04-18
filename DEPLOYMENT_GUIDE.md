# StarLink Card System - Deployment Guide

## Complete Free Cloud Deployment

This guide will walk you through deploying the StarLink Card System on completely free cloud infrastructure: Supabase (PostgreSQL) + Upstash (Redis) + Render.com (hosting).

---

## Prerequisites

### 1. GitHub Account
Register at [github.com](https://github.com) (free)

### 2. Git (if not already installed)
```bash
git --version
# If not installed: sudo apt install git  # Ubuntu/Debian
# Or download from: https://git-scm.com/downloads
```

### 3. Project Repository
Push this project to GitHub:

```bash
cd ~/starlink-card-system
git init
git add .
git commit -m "Initial commit: StarLink Card System"
# Create repository on GitHub and connect
```

---

## Phase 1: Free Database (Supabase)

**Cost**: FREE (500MB storage, no credit card required)

### Step 1: Register
1. Go to [supabase.com](https://supabase.com)
2. Click "Start your project" or "Sign in" (top right)
3. **Sign in with GitHub** (no new password needed!)
4. Authorize the app

### Step 2: Create Project
1. Click "New Project"
2. **Name**: `starlink-card-system`
3. **Database Password**: Generate a strong password (copy this!)
4. **Region**: Choose closest - Singapore is good for Taiwan
5. Click "Create new project"
6. Wait 2-3 minutes for database setup

### Step 3: Get Connection String
1. Go to Project Settings (gear icon)
2. Click "Database" on left side
3. Copy the connection string - look for "URI" format:
   ```
   postgresql://postgres:YOUR_PASSWORD@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres
   ```
4. **Save this!** You'll need it for .env file

**✅ Supabase setup complete!**

---

## Phase 2: Free Redis (Upstash)

**Cost**: FREE (10k commands/day, 30MB storage, no credit card required)

### Step 1: Register
1. Go to [upstash.com](https://upstash.com)
2. Click "Sign up" (top right) or "Get Started Free"
3. **Sign in with GitHub** (no new password needed!)
4. Authorize the app

### Step 2: Create Redis Database
1. Click "Create Database"
2. **Name**: `starlink-redis`
3. **Region**: Pick closest - Singapore is good for Taiwan
4. **Type**: Select "Free Tier"
5. Click "Create"
6. Wait 1 minute for setup

### Step 3: Get Connection URL
1. Click on your database name
2. Go to "Details" tab
3. Copy the "REST API" URL (looks like):
   ```
   https://us1-merry-dragonfly-12345.upstash.io
   ```
4. Use the password shown or set your own
5. Your Redis URL format:
   ```
   rediss://:PASSWORD@us1-merry-dragonfly-12345.upstash.io:6379
   ```

**✅ Upstash Redis setup complete!**

---

## Phase 3: Free Application Hosting (Render.com)

**Cost**: FREE (750 hours/month, ~25 days continuous uptime, no credit card required)

### Step 1: Register
1. Go to [render.com](https://render.com)
2. Click "Sign Up" (top right)
3. **Sign in with GitHub** (no new password needed!)
4. Authorize the app

### Step 2: Add Payment Method (Verification Only)
**Important**: Render requires a payment method for verification but **will not charge** on the free tier.

1. Go to Account Settings (top right avatar)
2. Click "Billing"
3. Add a credit/debit card (for verification - no charge)
4. Verify the card (small temporary authorization - refunded)

### Step 3: Deploy Your Application
1. Click "Dashboard" (top left)
2. Click "New" → "Web Service"
3. **Connect your GitHub account** (if not already)
4. Choose your repository: `your-username/starlink-card-system`
5. Configure:
   
   **Name**: `starlink-card-api`
   
   **Region**: Singapore (recommended for Taiwan)
   
   **Branch**: `main`
   
   **Root Directory**: `/` (leave as is)
   
   **Build Command**:
   ```bash
   pip install -r requirements.txt
   ```
   
   **Start Command**:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 10000
   ```
   
   **Plan**: Choose "Free" tier

6. Click "Advanced" button (below environment variables)
7. Add Environment Variables:
   
   **DATABASE_URL**: (paste from Supabase)
   
   **REDIS_URL**: (paste from Upstash)
   
   **SECRET_KEY**: Generate a random string (at least 32 characters)
   ```bash
   # Generate with:
   openssl rand -hex 32
   # or
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```
   
   **PORT**: `10000` (Render default)

8. Click "Create Web Service"
9. Wait 3-5 minutes for first deployment
10. Watch the logs - you should see "StarLink Card Platform is ready!"

### Step 4: Get Your URL
1. Once deployed, go to your service
2. Copy the URL (looks like): `https://starlink-card-api.onrender.com`
3. **Save this!** This is your API endpoint

**✅ Render deployment complete!**

---

## Phase 4: Configure .env File

Create a `.env` file in your project root:

```bash
cd ~/starlink-card-system
cp .env.example .env
```

Edit `.env` with your values:

```env
# Database
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres

# Redis  
REDIS_URL=rediss://:YOUR_PASSWORD@us1-merry-dragonfly-12345.upstash.io:6379

# Security (generate with: openssl rand -hex 32)
SECRET_KEY=your_random_secret_key_here

# Application
HOST=0.0.0.0
PORT=10000
```

Save and commit to GitHub:
```bash
git add .env
git commit -m "Add environment variables"
git push origin main
```

---

## Phase 5: Initialize Database

Once Render shows your service as "Live":

```bash
curl -X POST https://starlink-card-api.onrender.com/api/v1/admin/init-db
```

Or open in browser: `https://starlink-card-api.onrender.com/api/v1/admin/init-db`

You should see:
```json
{"success": true, "message": "Database tables created"}
```

---

## Phase 6: Test Your API

### Check Health
```bash
curl https://starlink-card-api.onrender.com/health
```

Expected:
```json
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected",
  "timestamp": "2026-04-18T08:30:00"
}
```

### Create a Merchant
```bash
curl -X POST https://starlink-card-api.onrender.com/api/v1/admin/merchants \
  -d '{"name": "Restaurant A", "phone": "0912345678", "role": "A_ISSUER"}' \
  -H "Content-Type: application/json"
```

### Issue Cards
```bash
curl -X POST https://starlink-card-api.onrender.com/api/v1/admin/cards/issue \
  -d '{
    "issuer_id": "YOUR_MERCHANT_ID",
    "title": "100元餐券", 
    "face_value": 100,
    "quantity": 10
  }' \
  -H "Content-Type: application/json"
```

---

## Phase 7: Keep Your Service Awake (Important!)

Render free tier sleeps after 15 minutes of inactivity. Use a free uptime monitoring service:

### Option 1: UptimeRobot (Free)
1. Sign up at [uptimerobot.com](https://uptimerobot.com)
2. Click "Add New Monitor"
3. **Type**: HTTP(s)
4. **URL**: Your Render URL (https://starlink-card-api.onrender.com)
5. Set interval to 5 minutes
6. Add your email for notifications

### Option 2: Cron-job.org (Free)
1. Sign up at [cron-job.org](https://cron-job.org)
2. Create job with URL: https://starlink-card-api.onrender.com/health
3. Every 10 minutes

This keeps your service awake 24/7 without manual intervention!

---

## Phase 8: Microsoft Teams Bot Integration (Optional)

See **TEAMS_SETUP.md** for detailed Teams Bot setup.

**Quick summary:**
1. Register Azure Bot at portal.azure.com
2. Get APP_ID and APP_PASSWORD
3. Add to Render environment variables
4. Configure webhook: `https://your-url.onrender.com/api/bot/messages`

---

## Deployment Checklist

- [x] GitHub account created
- [x] Project pushed to GitHub
- [x] Supabase project created and DATABASE_URL copied
- [x] Upstash Redis created and REDIS_URL copied
- [x] Render account created with billing verification
- [x] Web service deployed on Render
- [x] Environment variables configured on Render
- [x] Database initialized via /admin/init-db
- [x] Health check returns healthy status
- [x] Test API endpoints work
- [x] Uptime monitor configured (to prevent idle sleep)
- [x] Teams Bot configured (optional)

---

## Troubleshooting

### Render deployment fails
- Check logs in Render dashboard
- Verify all environment variables are set
- Ensure .env.example exists in repo
- Check DATABASE_URL and REDIS_URL format

### Database connection fails
- Verify Supabase is in active state
- Check firewall settings in Supabase
- Test connection string locally first

### Redis connection fails
- Ensure Upstash Redis is "Active"
- Test Redis URL format: `rediss://:password@host:port`

### Service goes to sleep
- Set up uptime monitoring (see Phase 7)
- Free tier allows 750 hours/month (25 days continuous)

### API returns 500 errors
- Check Render logs
- Test locally first: `python app/main.py`
- Verify all tables created: `/admin/init-db`

---

## Next Steps

1. Complete Teams Bot setup (see TEAMS_SETUP.md)
2. Test full card lifecycle
3. Add merchant accounts
4. Monitor platform revenue
5. Consider scaling to paid tiers when needed

---

**Total Monthly Cost: $0 USD**
**Setup Time: ~15-20 minutes**

**🎉 Deployment complete!** Your StarLink Card System is now running in the cloud, 24/7, completely free.