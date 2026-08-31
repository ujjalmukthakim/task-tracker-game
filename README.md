# Questly — game-like task tracker

## Run it locally

The easiest way is one command from the project folder:

```bash
zsh run-local.sh
```

It applies safe database migrations, starts the Django API, then starts the React app. Open `http://127.0.0.1:5173` and keep that terminal open.

Or run the two services separately:

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
- Level 2 costs 200 lifetime XP; each following level costs 150 XP more than the one before it. The dashboard always shows the exact next-level requirement.
- Daily missions rotate between different objective combinations and scale as you level. Their reward and penalty are shown before you commit to the day.
- Every XP gain, loss, purchase, and boost activation is recorded in the XP Ledger. Consumables can be used from Inventory.
