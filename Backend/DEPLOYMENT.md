# QDOCTOR Backend - Deployment Guide for Render

## Overview
This guide walks you through deploying the QDOCTOR backend to Render with Qdrant as the vector database.

## Prerequisites
1. **Render Account**: Sign up at https://render.com
2. **Qdrant Cloud Account**: Sign up at https://qdrant.io/cloud
3. **GitHub Repository**: Your code pushed to GitHub

## Step 1: Set up Qdrant Cloud

1. Go to https://qdrant.io/cloud and create an account
2. Create a new cluster:
   - Choose a region close to your Render deployment
   - Note the **Cluster URL** and **API Key**
3. Create a collection (optional - the backend will auto-create it):
   - Collection Name: `documents`
   - Vector Size: `384` (for all-MiniLM-L6-v2)
   - Distance Metric: `Cosine`

## Step 2: Prepare Your Repository

1. Ensure your GitHub repo has the updated code with Qdrant integration
2. Create a `.env` file (locally, don't commit):
   ```
   QDRANT_URL=https://your-cluster.qdrant.io:6333
   QDRANT_API_KEY=your-qdrant-api-key
   GROQ_API_KEY=your-groq-api-key
   FRONTEND_ORIGINS=https://your-frontend-domain.com
   ```

## Step 3: Deploy Backend to Render

1. **Create a new Web Service**:
   - Go to https://dashboard.render.com/new/web
   - Connect your GitHub repository
   - Select the repo and branch

2. **Configure the service**:
   - **Name**: `qdoctor-backend`
   - **Root Directory**: `Backend` (if monorepo) or leave blank if Backend is root
   - **Environment**: Docker
   - **Plan**: Free or Starter (adjust based on needs)

3. **Build & Deploy Settings**:
   - **Docker Context**: `./Backend` (if using monorepo structure)
   - **Dockerfile Path**: `./Backend/Dockerfile`

4. **Environment Variables**:
   Add these in Render's environment variables section:
   - `QDRANT_URL`: Your Qdrant cluster URL
   - `QDRANT_API_KEY`: Your Qdrant API key
   - `GROQ_API_KEY`: Your Groq API key
   - `FRONTEND_ORIGINS`: Your frontend URL

5. **Deploy**:
   - Click "Create Web Service"
   - Wait for the deployment to complete
   - Your API will be available at `https://qdoctor-backend.onrender.com`

## Step 4: Update Frontend Configuration

Update your frontend to point to the new backend URL:
```typescript
// In your frontend environment config
API_URL=https://qdoctor-backend.onrender.com
```

## Step 5: Run Data Ingestion (One-time)

After deployment, you need to ingest your PDFs into Qdrant:

### Option A: Via Render Shell
1. In Render dashboard, go to your service
2. Click "Connect" (shell access)
3. Run: `python -m ingest`

### Option B: Via Local Script with Remote Qdrant
```bash
# Set environment variables
export QDRANT_URL=https://your-cluster.qdrant.io:6333
export QDRANT_API_KEY=your-qdrant-api-key
export GROQ_API_KEY=your-groq-api-key

# Run ingestion locally
python Backend/ingest.py
```

## Key Configuration Details

### Dockerfile Changes
- Added `PYTHONUNBUFFERED=1` for real-time logging
- Added health check endpoint
- Exposed port 8000
- Running Uvicorn with `0.0.0.0` binding (required for Render)

### Environment Variables
All sensitive data should be set in Render's dashboard:
- Never commit `.env` to git
- Use `.env.example` as reference for required variables

### Auto-Collection Creation
The backend automatically creates the Qdrant collection if it doesn't exist, so you don't need to pre-create it.

## Troubleshooting

### Connection Issues
```bash
# Test Qdrant connectivity (from Render shell)
curl -H "api-key: YOUR_API_KEY" https://your-cluster.qdrant.io:6333/health
```

### View Logs
- In Render dashboard: Service → Logs tab
- Check for connection errors or API key issues

### Memory Issues
- If you get OOM errors, upgrade your Render plan or optimize chunk sizes in `config.py`

### Collection Not Created
- Verify `QDRANT_API_KEY` is correct
- Check Qdrant Cloud dashboard for cluster status
- Try manually creating a collection in Qdrant Cloud

## Cost Considerations

- **Render**: Pay-as-you-go (around $7/month minimum for a basic web service)
- **Qdrant Cloud**: Free tier includes 1GB storage; scales with usage
- **Groq API**: Free tier for inference (check groq.com for limits)

## Next Steps

1. Test the `/ask` endpoint:
   ```bash
   curl -X POST https://qdoctor-backend.onrender.com/ask \
     -H "Content-Type: application/json" \
     -d '{"question": "What is mental health?", "top_k": 5}'
   ```

2. Monitor logs in Render dashboard
3. Update frontend CORS origins in Render env vars if needed
4. Set up auto-deployment from GitHub (enabled by default)

---

**Notes**:
- The PDFs should be pre-ingested before going to production
- Consider setting up a separate ingestion service/job if you want to add PDFs dynamically
- The free tier of Render will auto-suspend after 15 minutes of inactivity; upgrade for 24/7 uptime
