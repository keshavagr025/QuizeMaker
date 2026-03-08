quizforge/
├── backend/
│   ├── app.py                  # Flask app entry point
│   ├── config.py               # Config & env vars
│   ├── routes/
│   │   ├── auth.py             # Login, signup, logout
│   │   ├── quiz.py             # Generate, submit quiz
│   │   └── dashboard.py        # History, analytics
│   ├── models/
│   │   ├── user.py             # User schema
│   │   └── quiz.py             # Quiz/result schema
│   ├── services/
│   │   ├── llm_service.py      # Groq API calls
│   │   └── pdf_service.py      # PDF text extraction
│   └── utils/
│       └── auth_utils.py       # JWT helpers
├── frontend/
│   ├── pages/
│   │   ├── index.html          # Landing page
│   │   ├── login.html          # Login
│   │   ├── signup.html         # Signup
│   │   ├── dashboard.html      # User dashboard + history
│   │   ├── create_quiz.html    # Quiz config
│   │   ├── quiz.html           # Take quiz
│   │   └── results.html        # Results + analytics
│   ├── css/
│   │   └── style.css           # Global styles
│   └── js/
│       ├── auth.js             # Auth logic
│       ├── quiz.js             # Quiz logic
│       ├── dashboard.js        # Dashboard + charts
│       └── api.js              # API helper
├── .env                        # Secrets (not committed)
├── .env.example
├── requirements.txt
└── README.md
