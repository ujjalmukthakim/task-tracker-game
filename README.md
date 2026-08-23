# Questly — game-like task tracker

## Run it locally

In one terminal, start the Django API:

```bash
python3 manage.py migrate
python3 manage.py runserver
```

In another terminal, start the React app:

```bash
cd frontend
npm install
npm run dev
```

Open the local address Vite prints (normally `http://localhost:5173`).

## Rules

- One-time quests appear on their scheduled date; daily quests recur automatically.
- Completing a quest grants 10, 25, 50, or 100 XP depending on importance.
- Unfinished overdue quests deduct half their XP value when the next day is opened.
- Every 250 XP is a new level. The dashboard tracks current and best completion streaks.
