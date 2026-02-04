backend :

# 1. Make your code changes
# (Edit any files in backend/)

# 2. Test locally (optional)
cd backend
python app.py  # Test on http://localhost:5000

# 3. Push to GitHub
cd /Users/nitheshkg/Desktop/CodeFlow/GJ_POS/GJ_PI
git add backend/
git commit -m "Description of your changes"
git push origin main

# 4. Deploy to Cloud Run
gcloud run deploy gj-pos-backend \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated



Frontend:

# 1. Make your code changes
# (Edit any files in frontend/src/)

# 2. Test locally (optional)
cd frontend
npm run dev  # Visit http://localhost:5173

# 3. Build the production version
npm run build

# 4. Copy to docs folder (for GitHub Pages)
cd /Users/nitheshkg/Desktop/CodeFlow/GJ_POS/GJ_PI
rm -rf docs && cp -r frontend/dist docs

# 5. Commit and push to GitHub
git add .
git commit -m "Description of your changes"
git push origin main


# Local Development Setup

This guide shows how to run the entire application locally with a free JSON-based database (no Firebase costs).

## Quick Start

### Backend Setup (Flask + Local JSON Database)

1. **Install dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Start the backend with local database:**
   ```bash
   ENVIRONMENT=development PORT=5000 python app.py
   ```

   This will:
   - Initialize a `local_data/` folder with JSON files for: users, customers, tickets, payments, reports
   - Start Flask on `http://localhost:5000`
   - Print confirmation: `✓ Local database initialized (JSON files - Development Mode)`

### Frontend Setup (Vue.js + Vite)

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Start the dev server:**
   ```bash
   npm run dev
   ```

   This will:
   - Start Vite dev server on `http://localhost:5173`
   - Auto-detect backend URL and use `http://localhost:5000`
   - Hot reload on file changes

3. **Access the app:**
   - Open browser to `http://localhost:5173`
   - Login credentials: Use any username/password (first time creates user)

## How It Works

### Environment-Based Database Selection

The application automatically selects the database based on `ENVIRONMENT` variable:

| ENVIRONMENT | Database | Use Case | Cost |
|---|---|---|---|
| `development` | Local JSON files | Local testing | Free |
| `production` | Firebase Firestore | Cloud Run deployment | ~$0-1/month |

### Data Storage

**Development (Local):**
- Data stored in `local_data/` folder as JSON files
- Files: `users.json`, `customers.json`, `tickets.json`, `payments.json`, `reports.json`
- Data persists between restarts (stays in local_data folder)
- Completely isolated from production Firebase

**Production:**
- Data stored in Firebase Firestore (gj-pawn-interest project)
- Cloud-based, secure, backed up
- Never touched during local development

### Architecture

```
Frontend (Vue.js)
    ↓ (auto-detects environment)
    ↓
Config.js (API_URL selector)
    ↓
Backend (Flask)
    ↓ (checks ENVIRONMENT variable)
    ↓
db.py (Init router)
    ├─→ Development: LocalDB (JSON files) ✓
    └─→ Production: Firebase Firestore
```

## Complete Local Testing Workflow

### Terminal 1: Start Backend
```bash
cd backend
ENVIRONMENT=development PORT=5000 python app.py
```

Expected output:
```
✓ Local database initialized (JSON files - Development Mode)
 * Running on http://0.0.0.0:5000
```

### Terminal 2: Start Frontend
```bash
cd frontend
npm run dev
```

Expected output:
```
  VITE v5.x ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  press h to show help
```

### In Browser
1. Navigate to `http://localhost:5173`
2. Create account or login
3. All data is stored locally in `backend/local_data/` folder
4. Refresh page, data persists (same browser session)
5. Restart backend, data persists (stored in JSON files)

## Verifying Local Database

### Check Created Data Files
```bash
ls -la backend/local_data/
```

You should see:
```
users.json
customers.json
tickets.json
payments.json
reports.json
```

### View JSON Data (pretty-printed)
```bash
cat backend/local_data/customers.json | python -m json.tool
```

### Sample data structure
```json
{
  "uuid-1234-5678": {
    "id": "uuid-1234-5678",
    "name": "John Doe",
    "phone": "1234567890",
    "created_at": "2024-01-15T10:30:45.123456",
    "updated_at": "2024-01-15T10:35:00.654321"
  }
}
```

## Switching Back to Production

### Deploy to Cloud Run (Production with Firebase)
```bash
gcloud run deploy gj-pos-backend --source . --region us-central1 --no-allow-unauthenticated
```

The `ENVIRONMENT` defaults to `production` in Cloud Run, so:
- Firebase Firestore is automatically used
- Production data is completely safe (never touched by local development)
- No interference with live app

### Local → Production Transition
1. **Local testing done?** Continue with local dev setup
2. **Ready to deploy?** Just push to GitHub
3. **Cloud Run auto-builds** using ENVIRONMENT=production
4. **Firebase takes over** automatically

## Clean Local Data

### Remove all local data and start fresh
```bash
rm -rf backend/local_data
```

Next time you start the backend with `ENVIRONMENT=development`, new JSON files will be created automatically.

## Troubleshooting

### Backend won't start with local database
**Error:** `No module named 'services.local_db'`

**Solution:**
1. Make sure you're in the `backend/` directory
2. Check `ENVIRONMENT=development` is set
3. Verify file exists: `backend/services/local_db.py`

### Frontend can't connect to backend
**Error:** `ERR_CONNECTION_REFUSED` in browser console

**Solution:**
1. Check backend is running: `ENVIRONMENT=development PORT=5000 python app.py`
2. Check port 5000 is available: `lsof -i :5000`
3. Check frontend config: `frontend/src/config/api.js`

### Data not persisting
**Symptom:** Restart backend, data gone

**Solution:**
1. Check `local_data/` folder exists and has JSON files
2. Check file permissions: `ls -la backend/local_data/`
3. Restart and check JSON files are being updated

### Production database accidentally modified during local testing
**Safety:** This cannot happen! Local development completely isolated:
- Uses `ENVIRONMENT=development` (never production)
- Firebase only initialized when `ENVIRONMENT != development`
- Production credentials never loaded in local mode

## Environment Variables Reference

### Local Development (.env or command line)
```bash
ENVIRONMENT=development    # Must be set to use LocalDB
PORT=5000                  # Backend port
SECRET_KEY=dev-secret      # Dev secret key
```

### Production (Cloud Run auto-set)
```bash
ENVIRONMENT=production     # Default, uses Firebase
PORT=8080                  # Cloud Run standard port
SECRET_KEY=<from secret>   # From Secret Manager
```

## What's New in This Setup

✅ **Zero Firebase Cost** - Local JSON storage completely free
✅ **Production Safe** - No risk of modifying live data
✅ **Fast Iteration** - No network latency, instant data access
✅ **Offline Testing** - Works without internet connection
✅ **Simple Deployment** - Same code, just set ENVIRONMENT variable

## Next Steps

1. **Test locally** - Follow "Complete Local Testing Workflow" above
2. **Verify databases** - Check `local_data/` has JSON files
3. **Make code changes** - Frontend auto-reloads, backend restart needed
4. **Deploy to production** - Push to GitHub, Cloud Run auto-builds

For detailed deployment info, see [DEPLOYMENT.md](DEPLOYMENT.md)
