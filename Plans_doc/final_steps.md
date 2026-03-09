# Final Steps — Deployment & Submission

## What You're Submitting

You submit the **entire project** (all code, templates, static files, tests, etc.) by pushing it
to the Qwasar git remote. The `my_dark_sky_url.txt` file with your live URL is part of that push.
It's not just the txt file — it's the whole codebase.

---

## Step 1: Deploy to a Cloud Provider

You need to host the app on a public URL. Below are instructions for **Render** (free tier,
easiest) and **Railway** (also easy). Pick one.

### Option A: Render (Recommended — Free)

1. Go to [https://render.com](https://render.com) and sign up (GitHub login works).

2. Click **"New" → "Web Service"**.

3. Choose **"Build and deploy from a Git repository"** → connect your GitHub account.

4. You need the code on GitHub first. Create a **private** repo on GitHub:
   ```bash
   # From the project root:
   cd /Users/apple/Documents/IT.Projects/STARTSCHOOL_QWASAR/My_dark_sky

   git init
   git add -A
   git commit -m "My Dark Sky - weather app"

   # ✅ DONE — already pushed to:
   # https://github.com/AlbertoAlbertoAlberts/My_Dark_Sky.git
   ```

5. Back in Render, select your `my-dark-sky` repo.

6. Configure the service:
   | Setting          | Value                      |
   |------------------|----------------------------|
   | Name             | `my-dark-sky`              |
   | Region           | Any (pick closest)         |
   | Branch           | `main`                     |
   | Runtime           | `Python 3`                |
   | Build Command    | `pip install -r requirements.txt` |
   | Start Command    | `gunicorn app:app`         |
   | Instance Type    | **Free**                   |

7. Add **Environment Variables** (in the "Environment" section):
   | Key                  | Value                                  |
   |----------------------|----------------------------------------|
   | `OPENWEATHER_API_KEY`| `92e59cdffd99d1e0fbf87715e84ded1b`     |
   | `FLASK_SECRET_KEY`   | `mysupersecretkey123`                  |
   | `PYTHON_VERSION`     | `3.13.0`                               |

8. Click **"Create Web Service"** and wait for the build to finish.

9. Your URL will be something like: `https://my-dark-sky.onrender.com`

10. **Test it!** Open the URL in your browser, try searching a city, try geolocation, try
    Time Machine.

> **Note:** Render free tier spins down after 15 minutes of inactivity. First request after
> spin-down takes ~30 seconds. This is fine for a school project.

---

### Option B: Railway (Alternative)

1. Go to [https://railway.app](https://railway.app) and sign up.

2. Click **"New Project" → "Deploy from GitHub Repo"**.

3. Push your code to GitHub first (same steps as Option A, step 4).

4. Select your repo. Railway auto-detects Python + Procfile.

5. Add environment variables:
   - `OPENWEATHER_API_KEY` = `92e59cdffd99d1e0fbf87715e84ded1b`
   - `FLASK_SECRET_KEY` = `mysupersecretkey123`

6. Click **"Deploy"**. Railway gives you a URL like `https://my-dark-sky-production.up.railway.app`.

7. Test the URL.

> **Note:** Railway gives $5/month free credits. More than enough for this project.

---

## Step 2: Write Your URL

Once deployed and tested, write the URL into the file:

```bash
cd /Users/apple/Documents/IT.Projects/STARTSCHOOL_QWASAR/My_dark_sky

# Replace with YOUR actual deployed URL:
echo "https://my-dark-sky.onrender.com" > my_dark_sky_url.txt
```

Verify it:
```bash
cat my_dark_sky_url.txt
# Should print your URL
```

---

## Step 3: Push to Qwasar Git

This is the actual submission. You push the entire project to Qwasar's git remote.

```bash
cd /Users/apple/Documents/IT.Projects/STARTSCHOOL_QWASAR/My_dark_sky

# If you already initialized git in Step 1 (for GitHub), just add the Qwasar remote:
git remote add qwasar git@git.us.qwasar.io:my_dark_sky_20702

# Stage and commit any new changes (like the URL file):
git add -A
git commit -m "Final submission with deployed URL"

# Push to Qwasar:
git push -u qwasar main
```

If you did NOT initialize git yet:
```bash
cd /Users/apple/Documents/IT.Projects/STARTSCHOOL_QWASAR/My_dark_sky

git init
git add -A
git commit -m "My Dark Sky - weather app"
git remote add qwasar git@git.us.qwasar.io:my_dark_sky_20702
git branch -M main
git push -u qwasar main
```

---

## Step 4: Verify Your Submission

1. **Check the push worked:**
   ```bash
   git log --oneline -3
   # Should show your commit(s)
   ```

2. **Check the deployed URL is accessible:**
   - Open your URL in a browser (or incognito window)
   - Test: search for a city
   - Test: click geolocation button
   - Test: open Time Machine and pick a past date
   - Test: check the daily forecast shows

3. **On Qwasar platform:**
   - Go to your project page on Docode
   - Verify it shows your latest push
   - Submit your project for review

---

## Pre-Flight Checklist

Before pushing, make sure everything is clean:

- [ ] App runs locally: `python3 app.py` → visit `http://localhost:5001`
- [ ] All 32 tests pass: `python3 test_app.py`
- [ ] `my_dark_sky_url.txt` contains your live URL (not empty)
- [ ] Live URL works in browser
- [ ] `.env` is in `.gitignore` (it is — your API key won't leak)
- [ ] `venv/` is in `.gitignore` (it is)
- [ ] `*.db` is in `.gitignore` (it is — SQLite DB won't be pushed)
- [ ] No unnecessary files in the repo

Run a final sanity check:
```bash
# See what will be committed:
git status

# See all tracked files:
git ls-files
```

Expected tracked files:
```
.env.example
.gitignore
Plans_doc/final_steps.md
Plans_doc/fix.md
Plans_doc/plan.md
Procfile
TASK_DESCRIPTION/Screenshot 2026-03-09 at 16.28.41.png
TASK_DESCRIPTION/Screenshot 2026-03-09 at 16.28.44.png
TASK_DESCRIPTION/Screenshot 2026-03-09 at 16.28.48.png
app.py
config.py
models.py
my_dark_sky_url.txt
requirements.txt
services/__init__.py
services/geocoding_service.py
services/weather_service.py
static/css/style.css
static/js/app.js
templates/index.html
templates/partials/current_weather.html
templates/partials/daily_forecast.html
templates/partials/time_machine.html
test_app.py
```

---

## Troubleshooting

### "Permission denied (publickey)" when pushing to Qwasar
You need your SSH key added to your Qwasar account:
```bash
# Check if you have an SSH key:
cat ~/.ssh/id_ed25519.pub
# or
cat ~/.ssh/id_rsa.pub

# If no key exists, create one:
ssh-keygen -t ed25519 -C "your_email@example.com"
cat ~/.ssh/id_ed25519.pub
```
Copy the public key and add it in your Qwasar account settings (SSH Keys section).

### Render build fails
- Check the build logs in Render dashboard
- Make sure `requirements.txt` has all 5 packages
- Make sure `Procfile` has `web: gunicorn app:app`
- Make sure there's no syntax error in your code

### App crashes on Render but works locally
- Check Render logs for the error
- Most common: missing environment variable (add it in Render dashboard)
- SQLite works on Render but the DB resets on each deploy (this is fine — it's just a cache)

### Geolocation doesn't work on deployed site
- Geolocation requires HTTPS. Render provides HTTPS by default, so this should work.
- If using HTTP, browsers block geolocation. Make sure your URL starts with `https://`.
