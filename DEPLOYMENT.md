# Frontend Deployment to GitHub Pages

Your Vue.js frontend has been updated to work with your Cloud Run backend!

## What's Changed:

✅ **Centralized API Configuration** (`src/config/api.js`)
- Automatically detects environment (production vs local development)
- Uses Cloud Run backend in production: `https://gj-pos-backend-544714625292.us-central1.run.app`
- Uses localhost in development: `http://localhost:5000`

✅ **All API calls updated**
- `authStore.js` - Login, logout, password change
- `ticketStore.js` - Ticket operations
- Vue components - Customers, Reports, Payments, Dashboard

✅ **Backend CORS enabled**
- Allows requests from: https://nitheshkg.github.io

## How to Deploy Frontend

### Option 1: Manual Deployment (Quick)

```bash
# From the project root
cd frontend

# Install dependencies (if needed)
npm install

# Build the project
npm run build

# This creates a 'dist' folder with your static files

# Commit and push to GitHub
git add .
git commit -m "Update frontend with Cloud Run backend integration"
git push origin main
```

Then setup GitHub Pages deployment:
1. Go to: https://github.com/NitheshKG/GJ_PI/settings/pages
2. Set "Source" to: `Deploy from a branch`
3. Select branch: `main` and folder: `/docs` (or `/dist` if you rename)

### Option 2: Automatic Deployment with GitHub Actions (Recommended)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy Frontend to GitHub Pages

on:
  push:
    branches: [main]
    paths:
      - 'frontend/**'
      - '.github/workflows/deploy.yml'

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
      
      - name: Install dependencies
        run: cd frontend && npm install
      
      - name: Build
        run: cd frontend && npm run build
      
      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./frontend/dist
          cname: nitheshkg.github.io/GJ_PI
```

## Testing

### Local Development:
```bash
cd frontend
npm run dev
# Visit: http://localhost:5173
```

### Production:
Visit: https://nitheshkg.github.io/GJ_PI/

## Backend Status

🟢 **Backend is live** at:
```
https://gj-pos-backend-544714625292.us-central1.run.app
```

**Features:**
- ✅ Free tier: 2 million requests/month
- ✅ Auto-scales to zero when idle
- ✅ CORS enabled for GitHub Pages
- ✅ Firebase Firestore integration

## Environment Variables

If you need environment-specific configuration, update `frontend/src/config/api.js`:

```javascript
const getApiUrl = () => {
  if (window.location.hostname === 'nitheshkg.github.io') {
    return 'https://gj-pos-backend-544714625292.us-central1.run.app'
  }
  return 'http://localhost:5000'
}
```

## Troubleshooting

**Issue: CORS errors in browser console**
- Ensure backend is deployed with GitHub Pages origin in CORS list
- Check browser console for exact error message
- Verify backend is running: `curl https://gj-pos-backend-544714625292.us-central1.run.app/`

**Issue: API calls returning 404**
- Check that all API URLs in components use `${API_URL}/api/...`
- Verify backend routes are registered correctly

**Issue: Authentication not working**
- Ensure tokens are being saved to localStorage
- Check Network tab in browser DevTools for auth endpoint responses

## Next Steps

1. ✅ Deploy updated frontend to GitHub Pages
2. ✅ Test all features in production
3. ⬜ Set custom domain (optional)
4. ⬜ Add Firebase Auth (optional)
5. ⬜ Monitor backend performance
