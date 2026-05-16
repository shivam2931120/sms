# College Management System (SMS)

A comprehensive Flask-based College/School Management System with admin, teacher, and student portals.

## Features

### 🎛️ Admin Dashboard
- Student, Teacher, Class, Subject management
- Attendance tracking with analytics
- Fee management
- Library system
- Exam & Homework management
- Role-based permissions

### 📊 Analytics
- Attendance trends (30-day charts)
- Student performance dashboard
- Department-wise statistics

### 👨‍🎓 Student Portal
- View attendance, marks, fees
- Class timetable
- Homework assignments

### 👨‍🏫 Teacher Portal
- Mark attendance (bulk)
- Enter grades
- View personal schedule

## Tech Stack

- **Backend**: Flask, SQLAlchemy
- **Database**: PostgreSQL (Supabase) / SQLite (local dev)
- **Frontend**: Jinja2, Bootstrap 5, Chart.js
- **Deployment**: Vercel (serverless)

## Setup

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/yourusername/sms.git
cd sms
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your values
```

5. Initialize database:
```bash
.venv/bin/python seed_demo.py
```

6. Run development server:
```bash
.venv/bin/python run.py
```

## Demo Logins

After running `seed_demo.py`, the login page shows demo credentials for every role:

| Role | Login | Password |
|------|-------|----------|
| Admin | `admin@demo.com` | `admin123` |
| Teacher | `john@demo.com` | `teacher123` |
| Student | `alice@demo.com` | `student123` |

Set `SHOW_DEMO_CREDENTIALS=false` in production.

### Supabase Setup

1. Create a new project at [supabase.com](https://supabase.com)
2. Go to **Settings > Database > Connection string**
3. Copy the URI and add to your `.env`:
```
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
```

### Vercel Deployment

1. Push code to GitHub
2. Connect repository to Vercel
3. Add environment variables in Vercel dashboard:
   - `SECRET_KEY`
   - `DATABASE_URL` (Supabase connection string)
4. Deploy!

## Environment Variables

Use `SETUP_VALUES.md` as the fill-in checklist for Supabase, Vercel, SMTP, Razorpay, and school details.

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | Flask secret key for sessions |
| `DATABASE_URL` | Supabase PostgreSQL connection string |
| `FLASK_ENV` | `development` or `production` |
| `SHOW_DEMO_CREDENTIALS` | Set to `true` to show demo login cards |
| `SMTP_HOST` / `SMTP_PORT` / `SMTP_USERNAME` / `SMTP_PASSWORD` | Email provider placeholders |
| `RAZORPAY_KEY_ID` / `RAZORPAY_KEY_SECRET` / `RAZORPAY_WEBHOOK_SECRET` | Razorpay placeholders |

## School Details

Edit `school_details.json` to update the institution name, address, contact details, and logo path used by PDFs and shared templates.

## Vercel Notes

Add the values from `.env.example` in Vercel Project Settings. Use Supabase for `DATABASE_URL`, set a real `SECRET_KEY`, and keep `SHOW_DEMO_CREDENTIALS=true` if you want the demo cards visible on the deployed login page.

## Default Admin Login

For a non-demo admin, create an admin user:
```python
from app import create_app, db
from app.models import User

app = create_app()
with app.app_context():
    admin = User(username='admin', email='admin@example.com', role='admin')
    admin.set_password('admin123')
    db.session.add(admin)
    db.session.commit()
```

## Project Structure

```
sms/
├── api/
│   └── index.py          # Vercel serverless entry
├── app/
│   ├── routes/
│   │   ├── admin.py      # Admin routes
│   │   ├── student.py    # Student portal
│   │   └── teacher.py    # Teacher portal
│   ├── templates/
│   ├── static/
│   └── models.py
├── config.py
├── requirements.txt
├── vercel.json
└── run.py
```

## License

MIT License
