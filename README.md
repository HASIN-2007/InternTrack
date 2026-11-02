# 🚀 InternTrack – Internship Application Tracking System

**InternTrack** is a web-based application designed to help students organize, track, and manage their internship applications in one place.

Instead of maintaining internship details manually, users can manage their applications through a simple dashboard with search, filtering, and application status tracking.

## ✨ Features

- 🔐 **User Authentication** – Secure registration and login.
- 📊 **Dashboard** – View internship application statistics.
- ➕ **Add Applications** – Record company names, job roles, application dates, and other details.
- ✏️ **Edit Applications** – Update existing internship records.
- 🗑️ **Delete Applications** – Remove unwanted records.
- 🔍 **Search Applications** – Find applications by company name.
- 🎯 **Filter Applications** – Filter applications based on their status.
- 📥 **CSV Export** – Download internship application records.
- 🔒 **Data Privacy** – Users can access only their own applications.
- 🗄️ **SQLite Database** – Store application and user information.

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Flask | Web framework |
| SQLite | Database |
| HTML5 | Page structure |
| CSS3 | Styling |
| JavaScript | Frontend interactions |
| Bootstrap | Responsive UI |
| Pytest | Automated testing |

## 📁 Project Structure

```text
InternTrack/
│
├── app.py
├── test_app.py
├── requirements.txt
├── README.md
│
├── templates/
│   ├── auth_base.html
│   ├── login.html
│   ├── register.html
│   └── other application templates
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
└── database.db
```

*Note: Adjust the template and static folder entries to match the actual files in your repository.*

## ⚙️ Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/HASIN-2007/InternTrack.git
```

### 2. Navigate to the project directory

```bash
cd InternTrack
```

### 3. Install dependencies

```bash
py -m pip install -r requirements.txt
```

### 4. Run the application

```bash
py app.py
```

### 5. Open in your browser

```text
http://127.0.0.1:5000
```

## 🧪 Run Automated Tests

Execute the following command:

```bash
py -m pytest -v
```

### Test Results

The project currently has **19 automated test cases**, all of which passed in local testing.

```text
========================
19 passed in 9.50s
========================
```

## 🔐 Security Features

- Password hashing.
- User authentication and session management.
- User-specific application access.
- Parameterized SQL queries.
- Login protection for authenticated pages.

For production deployment, configure a secure environment-based Flask secret key, disable debug mode, and enable CSRF protection.

## 🎯 Project Objective

The main objective of InternTrack is to simplify internship application management for students by providing a centralized platform to organize applications, monitor progress, and maintain records efficiently.

## 👨‍💻 Developer

**Hasin**

B.Tech – Computer Science and Engineering

NRI Institute of Technology

GitHub: [HASIN-2007](https://github.com/HASIN-2007)

Project: [InternTrack](https://github.com/HASIN-2007/InternTrack)

---

⭐ If you find this project useful, consider giving the repository a star!

