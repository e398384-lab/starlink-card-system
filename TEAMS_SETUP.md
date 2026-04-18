# Microsoft Teams Bot Setup Guide

## Overview

Integrate your StarLink Card Platform with Microsoft Teams Bot for remote management and monitoring.

---

## Prerequisites

### Microsoft Account
- Microsoft 365 account (personal or business)
- Azure subscription (free tier works)
- Teams account for testing

### Required Information
- StarLink API URL (from Render.com deployment)
- Microsoft Azure access

---

## Step 1: Azure Bot Registration

### 1.1 Create Azure Account (if needed)
1. Go to [azure.microsoft.com](https://azure.microsoft.com)
2. Click "Start free" or "Sign in"
3. **Requires**: Credit card for verification (no charge for bot registration)

### 1.2 Create Bot Resource
1. Go to [portal.azure.com](https://portal.azure.com)
2. Click "Create a resource"
3. Search for "Azure Bot"
4. Click "Create"

### 1.3 Configure Bot
**Project Details:**
- **Subscription**: Choose your subscription (use free trial if available)
- **Resource group**: Click "Create new"
  - Name: `starlink-bot-rg`

**Bot Details:**
- **Bot handle**: `starlink-card-bot`
- **Pricing tier**: `Free F0 (10k messages/month)`
- **Type**: `Multi Tenant`

**Microsoft App ID:**
- Check: "Create new Microsoft App ID"
- Click "Review + create"

### 1.4 Complete Setup
1. Review settings
2. Click "Create"
3. Wait 2-3 minutes for deployment
4. Go to "Go to resource"

**✅ Azure Bot created!**

---

## Step 2: Configure Bot Credentials

### 2.1 Get App ID and Password

**App ID:**
1. In your bot resource, go to "Configuration" (left menu)
2. Copy **Microsoft App ID** (looks like: `a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6`)
3. Save this!

**App Password:**
1. Under "Microsoft App ID", click "Manage Password"
2. This opens Azure AD
3. Under "Client secrets", click "New client secret"
4. **Description**: `bot-secret`
5. **Expires**: `24 months`
6. Click "Add"
7. Copy the **Value** immediately (won't show again!)
8. Save this!

### 2.2 Add Credentials to Environment

Add these to your `.env` file:

```env
TEAMS_APP_ID=a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6
TEAMS_APP_PASSWORD=your_secret_value_here
```

Also add to Render.com environment variables:
1. Go to your Render service
2. Settings → Environment Variables
3. Add:
   - `TEAMS_APP_ID`: your_app_id
   - `TEAMS_APP_PASSWORD`: your_secret
4. Save changes
5. Redeploy (or wait for auto-redeploy)

---

## Step 3: Configure Messaging Endpoint

### 3.1 Set Webhook URL

1. In Azure Bot, go to "Configuration" again
2. Find "Messaging endpoint"
3. Enter your StarLink API webhook URL:
   ```
   https://your-app.onrender.com/api/bot/messages
   ```
4. Click "Apply"

### 3.2 Verify SSL
Render provides HTTPS automatically (with Let's Encrypt), so SSL verification will pass.

---

## Step 4: Test in Bot Framework Emulator

### 4.1 Install Emulator
1. Download [Bot Framework Emulator](https://github.com/microsoft/BotFramework-Emulator/releases)
2. Install on your computer

### 4.2 Test Connection
1. Open emulator
2. Click "Open Bot"
3. Enter:
   - **Bot URL**: `http://localhost:3978/api/messages` (for local testing)
   - Or use: `https://your-app.onrender.com/api/bot/messages`
   - **Microsoft App ID**: your_app_id
   - **Microsoft App Password**: your_password
4. Click "Connect"

### 4.3 Send Test Message
Type `/status` and see if you get system status response.

---

## Step 5: Deploy to Teams

### 5.1 Create App Manifest

Create a file `manifest.json`:

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/teams/v1.12/MicrosoftTeams.schema.json",
  "manifestVersion": "1.12",
  "version": "1.0.0",
  "id": "YOUR_APP_ID_HERE",
  "packageName": "com.starlink.cardbot",
  "developer": {
    "name": "StarLink Card Platform",
    "websiteUrl": "https://your-domain.com",
    "privacyUrl": "https://your-domain.com/privacy",
    "termsOfUseUrl": "https://your-domain.com/terms"
  },
  "name": {
    "short": "StarLink Bot",
    "full": "StarLink Card Platform Bot"
  },
  "description": {
    "short": "Manage StarLink card system",
    "full": "Remote management and monitoring for StarLink Card Platform"
  },
  "icons": {
    "outline": "outline.png",
    "color": "color.png"
  },
  "accentColor": "#FFFFFF",
  "bots": [
    {
      "botId": "YOUR_APP_ID_HERE",
      "scopes": ["team", "personal"],
      "supportsFiles": false,
      "isNotificationOnly": false
    }
  ],
  "permissions": ["identity", "messageTeamMembers"],
  "validDomains": ["*.onrender.com", "your-domain.com"]
}
```

### 5.2 Create Icons
Create two PNG images:
- `outline.png`: 32x32px, transparent background
- `color.png`: 192x192px, full color

### 5.3 Package App
Zip these files into `manifest.zip`:
- manifest.json
- outline.png
- color.png

### 5.4 Install in Teams

**For Testing:**
1. Open Teams app (desktop or web)
2. Go to Apps → Upload a custom app
3. Select `manifest.zip`
4. Choose: "Add for me" or "Add to a team"
5. Search for and add your bot

**Or use Developer Portal:**
1. Go to [dev.teams.microsoft.com](https://dev.teams.microsoft.com)
2. Sign in with Microsoft account
3. Click "Apps" → "Import app"
4. Upload `manifest.zip`
5. Click "Install in Teams"

### 5.5 Test in Teams

1. Go to Chat
2. Search for "StarLink Bot" (or your bot name)
3. Send a message: `/help`
4. Should see available commands

---

## Step 6: Production Deployment

### 6.1 Finalize Webhook

Ensure messaging endpoint is set to your production URL:
```
https://your-production-domain.com/api/bot/messages
```

### 6.2 Security

- Never commit `TEAMS_APP_PASSWORD` to Git
- Use Render environment variables
- Rotate secrets every 90 days
- Set up IP whitelist if using paid tier

### 6.3 Monitoring

Enable Azure monitoring:
1. In Azure Bot, go to "Monitoring"
2. View message volume
3. Check error rates
4. Set up alerts

---

## Bot Commands

Available commands once bot is integrated:

### `/status`
Shows system health, database connection, card/merchant counts

### `/cards`
Displays card inventory by status

### `/exec <command>`
Execute limited system commands:
- `ls` - List files
- `df` - Disk space
- `ps` - Process list
- `docker` - Docker status
- `free` - Memory usage

### `/help`
Show all available commands

---

## Troubleshooting

### Bot doesn't respond
- Check Azure Bot Configuration - is messaging endpoint correct?
- Verify App ID and Password in environment variables
- Check Render logs for errors
- Ensure webhook is reachable from public internet

### Message delivery failures
- Verify SSL certificate is valid
- Check network connectivity to your API
- Review Azure Bot metrics for delivery status

### Authentication errors
- Regenerate App Password in Azure AD
- Update environment variables
- Restart Render service
- Redeploy

### Can't install in Teams
- Verify manifest.json syntax (use JSON validator)
- Check all required fields present
- Ensure icons are correct size
- App ID matches Azure Bot

---

## Security Best Practices

✅ **Do:**
- Store credentials in environment variables
- Use HTTPS webhook endpoints
- Rotate secrets regularly
- Limit bot permissions to minimum needed
- Monitor message logs

❌ **Don't:**
- Commit secrets to Git repository
- Use HTTP webhook endpoints
- Give bot broad permissions
- Ignore error messages

---

## Alternative: ngrok for Local Development

For testing bots locally:

```bash
# Install ngrok
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
tar -xzf ngrok-v3-stable-linux-amd64.tgz
sudo mv ngrok /usr/local/bin/

# Start ngrok (opens HTTPS tunnel to localhost)
ngrok http 10000

# Copy the HTTPS URL (looks like: https://abc123.ngrok.io)
# Set as messaging endpoint in Azure Bot:
# https://abc123.ngrok.io/api/bot/messages
```

This creates a public HTTPS URL to your local development server.

**⚠️ Warning**: ngrok free tier tunnels expire every 2 hours. Use for development only.

---

## Setup Timeline

- **Azure Bot Registration**: 10 minutes
- **App ID/Password**: 5 minutes
- **Local Testing**: 10 minutes
- **Teams Integration**: 15 minutes
- **Total**: ~45 minutes

---

## Resources

- [Azure Bot Documentation](https://docs.microsoft.com/azure/bot-service/)
- [Teams Bot Tutorial](https://docs.microsoft.com/microsoftteams/platform/bots/what-are-bots)
- [Bot Framework Emulator](https://github.com/microsoft/BotFramework-Emulator)
- [ngrok Documentation](https://ngrok.com/docs)

---

**✅ Teams Bot setup complete!** Your bot is now integrated with Microsoft Teams for remote management.