# Setup Values You Need To Fill

Use this file as the checklist for values that are not safe to hard-code.

Do not paste real secrets into GitHub commits. Put secrets in:

- Local development: `.env`
- Vercel deployment: Vercel Project Settings -> Environment Variables

The tracked reference file is `.env.example`.

## 1. School Details

Put these values in `school_details.json`.

```json
{
  "name": "Your School Name",
  "address": "Your school address",
  "phone": "Your school phone",
  "email": "admin@example.com",
  "website": "https://example.com",
  "logo_filename": "img/shikshan.png"
}
```

Where to get them:

- School name/address/phone/email: your institution details.
- Website: your public school website, or leave the placeholder until you have one.
- Logo: put the logo file under `app/static/img/`, then set `logo_filename` to `img/your-logo.png`.

## 2. Flask Secret Key

Put this value in `.env` and Vercel Environment Variables:

```env
SECRET_KEY=
```

Where to get it:

Run this locally and paste the output:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(48))"
```

## 3. Supabase Database

Put this value in `.env` and Vercel Environment Variables:

```env
DATABASE_URL=
```

Where to get it:

1. Open Supabase.
2. Select your project.
3. Go to Project Settings -> Database.
4. Copy the PostgreSQL connection string.
5. Prefer the Session Pooler or direct connection string.
6. Replace `[YOUR-PASSWORD]` with your database password.

Example shape:

```env
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
```

If Vercel logs show `tenant/user ... not found`, the deployed `DATABASE_URL` points to a Supabase project ref, pooler host, or database user that Supabase no longer recognizes. Copy a fresh connection string from the current Supabase project and replace the Vercel variable.

Optional fallback, only if you want a second variable:

```env
SUPABASE_DB_URL=
```

## 4. Flask And Demo Settings

Put these in `.env` and Vercel Environment Variables:

```env
FLASK_ENV=production
FLASK_DEBUG=0
AUTO_SETUP_DATABASE=false
SHOW_DEMO_CREDENTIALS=true
```

Notes:

- Keep `AUTO_SETUP_DATABASE=false` for normal deployments. Temporarily set it to `true` only for first-time schema setup, then redeploy with it set back to `false`.
- `SHOW_DEMO_CREDENTIALS=true` keeps the demo login cards visible.
- Change it to `false` later if you want to hide demo credentials.

## 5. SMTP Email

Put these in `.env` and Vercel Environment Variables when you are ready to enable email:

```env
SMTP_HOST=
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=
SMTP_USE_TLS=true
MAIL_FROM=
```

Where to get them:

- Gmail: create an App Password in Google Account -> Security -> 2-Step Verification -> App passwords.
- SendGrid/Mailgun/Brevo/other SMTP provider: copy SMTP host, port, username, and password from that provider's dashboard.
- `MAIL_FROM`: the verified sender email from your provider.

No SMS or WhatsApp values are needed because that feature is intentionally not wired.

## 6. Razorpay

Put these in `.env` and Vercel Environment Variables when you are ready to enable real payments:

```env
RAZORPAY_KEY_ID=
RAZORPAY_KEY_SECRET=
RAZORPAY_WEBHOOK_SECRET=
RAZORPAY_CURRENCY=INR
```

Where to get them:

1. Open Razorpay Dashboard.
2. Go to Account & Settings -> API Keys.
3. Generate/copy `KEY_ID` and `KEY_SECRET`.
4. Go to Webhooks and create a webhook for your deployed Vercel URL.
5. Copy the webhook secret into `RAZORPAY_WEBHOOK_SECRET`.

Current status:

- The app has placeholders ready.
- Real Razorpay payment capture is not enabled until these values are added and payment routes are wired.

## 7. Vercel Deployment

Where to put values:

1. Open Vercel.
2. Select the `sms` project.
3. Go to Settings -> Environment Variables.
4. Add every required env value above.
5. Redeploy after changing env vars.

Required Vercel values for current deployment:

```env
SECRET_KEY=
DATABASE_URL=
FLASK_ENV=production
FLASK_DEBUG=0
AUTO_SETUP_DATABASE=false
SHOW_DEMO_CREDENTIALS=true
```

Optional Vercel values for later:

```env
SMTP_HOST=
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=
SMTP_USE_TLS=true
MAIL_FROM=
RAZORPAY_KEY_ID=
RAZORPAY_KEY_SECRET=
RAZORPAY_WEBHOOK_SECRET=
RAZORPAY_CURRENCY=INR
```

## 8. Local Development

Create a local `.env` from `.env.example`. The example uses SQLite so a local demo can run before you add Supabase:

```bash
cp .env.example .env
```

Keep `DATABASE_URL=sqlite:///dev.db` for local development, or replace it with your Supabase URL when testing PostgreSQL. `.env` is ignored by Git and should stay local.

Run the app:

```bash
.venv/bin/python seed_demo.py
.venv/bin/python run.py
```

Open:

```text
http://127.0.0.1:5000/login
```
