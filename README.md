# InternTrack

A simple web app that helps college students track their internship and job applications in one place.

![InternTrack dashboard](screenshots/dashboard.png)

## Features

- Dashboard with application stats
- Add, view, edit and delete applications
- Track status: Applied, Shortlisted, Interview, Selected, Rejected
- Search by company or role
- Filter by status
- Store deadlines and notes
- Export records to CSV
- Input validation for required fields
- Automated tests with Pytest

## Tech Stack

- Python
- Flask
- SQLite
- HTML, CSS, Jinja2
- Pytest
- Git and GitHub

## Project Structure

```
InternTrack/
├── app.py
├── test_app.py
├── requirements.txt
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── add.html
│   └── edit.html
├── static/
│   └── style.css
└── screenshots/
    └── dashboard.png
```

## How to Run

1. Clone the repository:

   ```
   git clone https://github.com/YOUR-USERNAME/InternTrack.git
   cd InternTrack
   ```

2. Create and activate a virtual environment:

   ```
   python -m venv venv
   venv\Scripts\activate
   ```

   On Mac/Linux, use `source venv/bin/activate` instead.

3. Install the requirements:

   ```
   pip install -r requirements.txt
   ```

4. Start the app:

   ```
   python app.py
   ```

5. Open `http://127.0.0.1:5000` in your browser.

## Run the Tests

```
pytest
```

## What I Learned

- Building routes and handling forms in Flask
- CRUD operations with SQLite and parameterized queries
- Template inheritance with Jinja2
- Validating user input
- Writing automated tests with Pytest

## Author

Hasin, B.Tech CSE student, Dr.RVR NRI Institute of Technology Deemed to be university.