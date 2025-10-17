# Setting Up Real LinkedIn Job Scraping with Apify

## Overview
The NAVICA backend now supports real LinkedIn job scraping using Apify's LinkedIn Jobs Search Scraper.

## Current Status
- ✅ **Filtered Mock Data**: Jobs are now filtered by selected roles (UI/UX Designer gets UI/UX jobs)
- ⚠️ **Real LinkedIn Scraping**: Requires Apify API token (optional)

## How It Works Now

### Without Apify Token (Current Setup)
The system uses **role-filtered mock data**:
- Select "UI/UX Designer" → Get UI/UX design jobs
- Select "Backend Developer" → Get backend jobs
- Select "Machine Learning Engineer" → Get ML jobs
- Select multiple roles → Get jobs for all selected roles

### With Apify Token (Real LinkedIn Jobs)
When configured with Apify, the system:
1. Searches LinkedIn for each selected role
2. Scrapes real job postings (5 per role)
3. Returns actual job descriptions, companies, and links
4. Falls back to mock data if scraping fails

## Setting Up Apify (Optional)

### Step 1: Create Apify Account
1. Go to https://apify.com/
2. Sign up for a free account
3. Free tier includes: 5 actor runs per month

### Step 2: Get API Token
1. Log into your Apify account
2. Go to Settings → Integrations → API Token
3. Copy your API token

### Step 3: Configure NAVICA
Edit your `.env` file:
```bash
APIFY_API_TOKEN=your_actual_apify_token_here
```

### Step 4: Install Apify Client (if not already installed)
```bash
pip install apify-client
```

### Step 5: Restart the Server
```bash
uvicorn app:app --host 127.0.0.1 --port 8000
```

## Testing

### Test with Mock Data (No Apify)
1. Upload your resume
2. Select "UI/UX Designer"
3. You should see:
   - "Senior UI/UX Designer" at Design Studio Co
   - "Product Designer (UI/UX)" at Tech Startup Inc

### Test with Real LinkedIn Data (With Apify)
1. Configure Apify token in `.env`
2. Upload resume and select roles
3. Wait 10-30 seconds for scraping
4. Get real LinkedIn job postings

## Available Mock Job Roles

When using mock data (without Apify), jobs are available for:

| Role | Number of Jobs |
|------|---------------|
| Software Engineer | 1 |
| Backend Developer | 1 |
| Frontend Developer | 1 |
| Full Stack Developer | 1 |
| **UI/UX Designer** | **2** |
| Data Scientist | 1 |
| Machine Learning Engineer | 1 |
| DevOps Engineer | 1 |
| Mobile Developer | 1 |
| Cloud Architect | 1 |
| Data Engineer | 1 |
| Product Manager | 1 |
| QA Engineer | 1 |
| Security Engineer | 1 |

## Benefits of Real Scraping

### Mock Data
- ✅ Instant results
- ✅ No API costs
- ✅ Always available
- ❌ Limited job variety
- ❌ Not current

### Real LinkedIn Data
- ✅ Current job postings
- ✅ Real companies
- ✅ Actual job descriptions
- ✅ Direct application links
- ❌ Requires API token
- ❌ Takes 10-30 seconds
- ❌ Limited free tier

## Apify Actor Used

**Actor**: `misceres/linkedin-jobs-search-scraper`
- Searches LinkedIn job postings
- Extracts job details
- Returns structured data

### Input Parameters
```json
{
  "searches": [
    {
      "keywords": "UI/UX Designer",
      "location": "United States",
      "maxResults": 5
    }
  ]
}
```

### Output Format
```json
{
  "jobId": "linkedin-job-id",
  "title": "Senior UI/UX Designer",
  "company": "Tech Company",
  "location": "San Francisco, CA",
  "description": "Job description...",
  "url": "https://www.linkedin.com/jobs/..."
}
```

## Troubleshooting

### Issue: Still seeing wrong jobs for selected role
**Solution**: Make sure server has restarted after updating `agent_core.py`

### Issue: Jobs take too long to load
**Solution**: Reduce `maxResults` in the Apify configuration or use mock data

### Issue: Apify rate limit exceeded
**Solution**: System automatically falls back to filtered mock data

### Issue: Connection timeout
**Solution**: Check internet connection; system will use mock data as fallback

## Cost Estimation

### Apify Free Tier
- 5 actor runs per month
- Each search uses 1 actor run
- Example: Search 3 roles = 1 actor run

### Paid Plans
- Starter: $49/month - 100 actor runs
- Team: $499/month - Unlimited runs

## Recommendation

**For Development/Testing**: Use filtered mock data (current setup)
**For Production**: Configure Apify for real LinkedIn jobs

## Current Implementation

The system is now configured to:
1. ✅ **Filter mock jobs by selected roles**
2. ✅ **Attempt real LinkedIn scraping if Apify token is configured**
3. ✅ **Gracefully fall back to mock data if scraping fails**
4. ✅ **Provide relevant job matches based on user selection**

## Next Steps

1. **Test the current setup** with role filtering (no Apify needed)
2. **If satisfied with mock data**, continue using it
3. **For real LinkedIn jobs**, sign up for Apify and configure token
4. **For production**, consider Apify paid plan or alternative scrapers

---

**Current Status**: ✅ **Role-filtered mock data is working!**  
Select "UI/UX Designer" and you'll get UI/UX jobs only.
