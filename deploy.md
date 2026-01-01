# Deploying to Vercel

## Prerequisites

1. Install Vercel CLI:
   ```bash
   npm install -g vercel
   ```

2. Login to Vercel:
   ```bash
   vercel login
   ```

## Deployment Steps

1. **Deploy to Vercel:**
   ```bash
   vercel
   ```

2. **Follow the prompts:**
   - Set up and deploy? **Y**
   - Which scope? Choose your account
   - Link to existing project? **N** (for first deployment)
   - What's your project's name? **onc-realty-booking**
   - In which directory is your code located? **./**

3. **Set Environment Variables (Optional):**
   ```bash
   vercel env add SECRET_KEY
   vercel env add JWT_SECRET_KEY
   ```

4. **Deploy to Production:**
   ```bash
   vercel --prod
   ```

## Configuration Details

- **Entry Point:** `api/index.py`
- **Framework:** Flask (Python)
- **Database:** SQLite (in-memory for serverless)
- **Static Files:** Served from `app/static/`

## Important Notes

1. **Database:** The app uses in-memory SQLite in production, so data won't persist between requests. For production use, consider:
   - PostgreSQL (Vercel Postgres)
   - MongoDB Atlas
   - PlanetScale
   - Supabase

2. **Static Files:** Make sure your static files are properly referenced in templates.

3. **CORS:** The app is configured to allow requests from Vercel domains.

## Testing the Deployment

After deployment, test these endpoints:
- `https://your-app.vercel.app/` - Main application
- `https://your-app.vercel.app/api/health` - Health check
- `https://your-app.vercel.app/api/auth/demo-login` - Demo login

## Troubleshooting

1. **Import Errors:** Check that all dependencies are in `requirements.txt`
2. **Database Issues:** Verify the database initializes correctly in production
3. **Static Files:** Ensure paths are correct in templates
4. **CORS Issues:** Check that your domain is in the CORS_ORIGINS list

## Environment Variables for Production

Consider setting these in Vercel dashboard:
- `SECRET_KEY`: A secure random string
- `JWT_SECRET_KEY`: A secure random string for JWT tokens
- `DATABASE_URL`: If using external database