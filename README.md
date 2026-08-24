# 🏔️ ComplaintDesk — Smart Complaint Classifier
### AI-powered Complaint Management System for Nepali Colleges

> **4th Semester College Project** | Python + Flask + MySQL + AI/ML

---

## 📋 Project Overview

ComplaintDesk is a full-stack web application that lets students submit complaints to their college administration. An AI engine automatically **classifies, prioritizes, and analyzes sentiment** of each complaint — removing manual triaging work from admins.

### Key Features
- 🤖 **AI Auto-Classification** — categorizes complaints into Academic, Hostel, Transport, Infrastructure, Administration
- 🎯 **Smart Priority Detection** — Critical / High / Medium / Low based on urgency keywords
- 💬 **Sentiment Analysis** — detects emotional tone using TextBlob NLP
- 🔒 **Privacy-Aware Visibility** — see "How Complaint Visibility Works" below
- 📊 **Admin Analytics Dashboard** — bar charts for categories, priorities, sentiment
- 👍 **Upvoting System** — students can upvote shared issues
- 📋 **Activity Timeline** — full audit trail per complaint
- 🎓 **Nepali University Support** — TU, PU, KU, etc.

---

## 🔒 How Complaint Visibility Works

This was changed from the original version, where each student could only see their own complaints.

| Complaint type | Who can see it |
|---|---|
| **Regular (non-anonymous)** | Everyone — it appears in the shared complaints feed so other students can see and upvote it |
| **Anonymous** | Only the **admin** and the **student who submitted it**. It never appears to other students, in the feed or otherwise. |

This means if a student is reporting something sensitive — harassment, bullying, abuse — they should submit it **anonymously**, which routes it to admin-only visibility instead of the public feed. Regular complaints (broken wifi, hostel food, bus delays, etc.) are meant to be seen by everyone so students can upvote shared issues.

Admins always see the real name behind every complaint, anonymous or not, since they're the ones responsible for acting on it.

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.10+ + Flask |
| Database | **MySQL** (via `PyMySQL`) |
| AI/ML | TextBlob (NLP) + Keyword Classifier |
| Frontend | HTML5 + CSS3 + Vanilla JS |
| Fonts | Google Fonts (Syne + DM Sans) |

---

## 🚀 Setup Instructions

### Step 1: Install Python & MySQL
Make sure Python 3.10+ and MySQL Server (5.7+/8.0+) are installed.
```bash
python --version
mysql --version
```

### Step 2: Create Virtual Environment (Recommended)
```bash
# Create venv
python -m venv venv

# Activate (Windows Command Prompt)
venv\Scripts\activate.bat

# Activate (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Activate (Mac/Linux)
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

Also download TextBlob's language data:
```bash
python -m textblob.download_corpora
```

### Step 4: Configure MySQL Connection
The app reads connection details from environment variables (with sensible localhost defaults). Set them if your setup differs from the defaults:

```bash
# Mac/Linux
export MYSQL_HOST=localhost
export MYSQL_PORT=3306
export MYSQL_USER=root
export MYSQL_PASSWORD=your_mysql_password
export MYSQL_DB=complaintdesk

# Windows (cmd)
set MYSQL_HOST=localhost
set MYSQL_PORT=3306
set MYSQL_USER=root
set MYSQL_PASSWORD=your_mysql_password
set MYSQL_DB=complaintdesk
```

You don't need to create the database or tables manually — `app.py` creates the `complaintdesk` database and all tables automatically on first run (via `database/schema.sql`).

### Step 5: Run the App
```bash
python app.py
```

### Step 6: Open in Browser
```
http://localhost:5000
```

---

## 👤 Demo Accounts

| Role | Email | Password |
|------|-------|----------|
| 🎓 Student | ram@student.edu.np | student123 |
| 🛡️ Admin | admin@college.edu.np | admin123 |

---

## 📁 Project Structure

```
complaintdesk/
├── app.py                  # Main Flask application & all API routes (MySQL via PyMySQL)
├── requirements.txt        # Python dependencies
├── README.md               # This file
│
├── classifier/
│   └── classifier.py       # AI Classification Engine
│                           # - Category classifier (keyword-based)
│                           # - Priority detector
│                           # - Sentiment analysis (TextBlob)
│                           # - Tag extractor
│
├── database/
│   └── schema.sql          # MySQL schema (tables, auto-run on first launch)
│
└── templates/
    ├── base.html           # Base layout (nav, styles, JS utilities)
    ├── login.html          # Login page
    ├── register.html       # Registration page
    ├── submit.html         # Submit complaint + live AI preview
    ├── dashboard.html       # Student: shared complaints feed + own complaints
    └── admin.html          # Admin: all complaints + analytics
```

---

## 🤖 How the AI Works

### 1. Category Classification
Uses keyword matching with weighted scoring across 6 categories:
- Each category has 30-50+ relevant keywords
- Text is tokenized and matched against keyword lists
- Category with highest match score wins
- Confidence score = matched_keywords / total_matches

### 2. Priority Detection
Rule-based priority with 3 levels:
- **Critical**: emergency/danger words (violence, accident, fire...)
- **High**: serious/urgent words + repeated issues
- **Medium**: general problem words
- **Low**: default (no urgent keywords found)

### 3. Sentiment Analysis
Uses `TextBlob` library's built-in sentiment polarity:
- Score range: -1.0 (very negative) to +1.0 (very positive)
- Maps to: Very Negative / Negative / Neutral / Positive
- Also boosts priority if sentiment is very negative

### 4. Tag Extraction
Extracts top-5 most relevant keywords from the complaint text based on the detected category.

---

## 🗄️ Database Schema (MySQL)

| Table | Purpose |
|-------|---------|
| `users` | Students & admins (name, email, role, dept, semester) |
| `complaints` | Main complaints table with AI results stored |
| `complaint_tags` | Tags extracted per complaint |
| `activity_log` | Audit trail (who did what, when) |
| `upvotes` | Tracks which user upvoted which complaint |

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/login` | Authenticate user |
| POST | `/api/register` | Create new student account |
| POST | `/api/logout` | Clear session |
| GET | `/api/me` | Get current user info |
| POST | `/api/classify` | Preview AI classification |
| POST | `/api/complaints` | Submit new complaint |
| GET | `/api/complaints` | List complaints — admin sees all; students see the shared feed of non-anonymous complaints plus all of their own (including their own anonymous ones) |
| PATCH | `/api/complaints/<id>` | Update status/response (admin) |
| POST | `/api/complaints/<id>/upvote` | Toggle upvote |
| GET | `/api/complaints/<id>/activity` | Get activity log |
| GET | `/api/stats` | Get statistics for charts |

---

## 💡 Possible Extensions

- Export complaints to Excel/PDF
- Email notifications when status changes
- Image/file attachment support
- Multi-college support
- Department-level admin accounts
- ML model trained on real data (replace keyword classifier)
- Mobile app (React Native)

---

## 📝 For Submission

**Project Title:** ComplaintDesk — College Complaint Management System
**Tech Stack:** Python, Flask, MySQL, TextBlob NLP
**Database:** MySQL with 5 tables
**AI/ML:** Keyword-based classifier + TextBlob sentiment analysis
**Frontend:** HTML/CSS/JS (no framework)

---

*Built for TU/PU affiliated colleges in Nepal* 🇳🇵
