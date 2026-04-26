# ClaDOSCheckIn

GitHub Actions automation for daily GLaDOS check-in.

## What it does

- Runs on a daily schedule
- Sends a status request to GLaDOS
- Sends a check-in request using your saved session cookie
- Supports manual workflow runs from the GitHub Actions page

## Repository layout

- `checkin.py`: the Python check-in script
- `.github/workflows/glados-checkin.yml`: the GitHub Actions workflow

## Setup

1. Open your GitHub repository settings.
2. Go to `Settings -> Secrets and variables -> Actions`.
3. Add this secret:
   - `GLADOS_COOKIE`
   - `FEISHU_WEBHOOK_URL` (optional, needed if you want Feishu notifications)
   - `FEISHU_BOT_SECRET` (optional, only needed if your Feishu bot has signature verification enabled)
4. Optional variables:
   - `GLADOS_BASE_URL`
   - `GLADOS_CHECKIN_TOKEN`
   - `GLADOS_ORIGIN`
   - `GLADOS_REFERER`

Defaults:

- `GLADOS_BASE_URL`: `https://glados.one`
- `GLADOS_CHECKIN_TOKEN`: derived from the host in `GLADOS_BASE_URL`
- `GLADOS_ORIGIN`: same as `GLADOS_BASE_URL`
- `GLADOS_REFERER`: `${GLADOS_ORIGIN}/console/checkin`

## Local test

```powershell
$env:GLADOS_COOKIE="your_cookie_here"
py -3 checkin.py
```

## Notes

- The workflow schedule uses UTC.
- The included cron runs at `01:05 UTC`, which is `09:05` China Standard Time.
- Keep your cookie only in GitHub Secrets.
- If `FEISHU_WEBHOOK_URL` is configured, the workflow sends a Feishu text message for both success and failure.
