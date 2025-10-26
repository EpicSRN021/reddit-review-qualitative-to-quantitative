# 🚀 Deploy FastAPI Backend to the Cloud

Your FastAPI backend is ready to deploy! Follow these steps to get a **public URL** that anyone can access.

## Option 1: Deploy to Render (Recommended - FREE)

### Step 1: Push to GitHub

```bash
git add .
git commit -m "Prepare backend for deployment"
git push origin branch3
```

### Step 2: Deploy on Render

1. Go to [render.com](https://render.com) and sign up (free)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Select your repository: `reddit-review-qualitative-to-quantitative`
5. Configure:
   - **Name**: `reviewradar-backend`
   - **Region**: Choose closest to you
   - **Branch**: `branch3`
   - **Root Directory**: Leave blank
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `cd backend && uvicorn server:app --host 0.0.0.0 --port $PORT`

### Step 3: Add Environment Variables

In Render dashboard, go to **Environment** and add:

- `subscription_key` = Your Azure OpenAI API key
- `REDDIT_CLIENT_ID` = Your Reddit client ID
- `REDDIT_CLIENT_SECRET` = Your Reddit client secret
- `REDDIT_USER_AGENT` = `ReviewRadar:v1.0 (by /u/YOUR_USERNAME)`

### Step 4: Deploy

Click **"Create Web Service"**

You'll get a URL like: `https://reviewradar-backend.onrender.com`

---

## Option 2: Deploy to Railway (Also FREE)

### Step 1: Push to GitHub (same as above)

### Step 2: Deploy on Railway

1. Go to [railway.app](https://railway.app) and sign up
2. Click **"New Project"** → **"Deploy from GitHub repo"**
3. Select your repository
4. Railway will auto-detect Python and deploy

### Step 3: Add Environment Variables

In Railway dashboard, add:

- `subscription_key`
- `REDDIT_CLIENT_ID`
- `REDDIT_CLIENT_SECRET`
- `REDDIT_USER_AGENT`

You'll get a URL like: `https://reviewradar-backend.up.railway.app`

---

## Test Your Deployed Backend

```bash
# Health check
curl https://YOUR-DEPLOYED-URL.com/

# Analyze a product
curl -X POST https://YOUR-DEPLOYED-URL.com/analyze \
  -H "Content-Type: application/json" \
  -d '{"keyword": "iPhone 15"}'
```

---

## Update Your Frontend

In your Next.js app, update the API URL to your deployed backend:

```javascript
const BACKEND_URL = "https://reviewradar-backend.onrender.com";

const response = await fetch(`${BACKEND_URL}/analyze`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ keyword: "MacBook Pro" }),
});
```

---

## 🎉 Done!

Your FastAPI backend is now live and accessible from anywhere in the world!
