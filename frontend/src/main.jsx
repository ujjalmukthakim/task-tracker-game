import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  Plus,
  Flame,
  Trophy,
  Target,
  Check,
  Trash2,
  Sparkles,
  X,
  Timer,
  Play,
  Square,
  ShoppingBag,
  User,
  Clock,
} from "lucide-react";
import "./style.css";
const API = "/api",
  pri = {
    low: ["Easy", "#53d6c5"],
    normal: ["Important", "#858cf6"],
    high: ["Very important", "#fb9d48"],
    legendary: ["Legendary", "#ff5f93"],
  };
const Bar = ({ data, value = "xp", color = "purple" }) => {
  let max = Math.max(...data.map((x) => Math.abs(x[value])), 1);
  return (
    <div className={"mini-bars " + color}>
      {data.map((x) => (
        <div key={x.date}>
          <i
            style={{
              height: `${Math.max(5, (Math.abs(x[value]) / max) * 100)}%`,
            }}
          />
          <small>{x.date}</small>
        </div>
      ))}
    </div>
  );
};
const Shape = ({ data, value, kind }) => {
  const values = data.map((item) => Math.max(0, item[value]));
  const max = Math.max(...values, 1);
  const points = values.map((v, i) => `${i * 45 + 8},${112 - (v / max) * 92}`).join(" ");
  const area = `8,112 ${points} 278,112`;
  if (kind === "donut") return <div className="data-donut"><b>{values.reduce((a,b)=>a+b,0)}</b><small>total</small></div>;
  if (kind === "radar") return <svg className="shape radar-shape" viewBox="0 0 290 125"><polygon points="145,8 270,98 20,98" /><polyline points={points} /></svg>;
  return <svg className="shape" viewBox="0 0 290 125">{kind === "area" && <polygon className="area-fill" points={area}/>}<polyline points={points} />{kind === "line" && values.map((v,i)=><circle key={i} cx={i*45+8} cy={112-(v/max)*92} r="4"/>)}</svg>;
};
const FiveCharts=({title,data,value,color})=><section className="data-set"><div className="set-heading"><p className="eyebrow">{title}</p><h2>Five views · same data</h2></div><div className="five-charts"><article className="panel graph-card"><h3>Bar chart</h3><Bar data={data} value={value} color={color}/></article><article className="panel graph-card"><h3>Line chart</h3><Shape data={data} value={value} kind="line"/></article><article className="panel graph-card"><h3>Area chart</h3><Shape data={data} value={value} kind="area"/></article><article className="panel graph-card"><h3>Focus radar</h3><Shape data={data} value={value} kind="radar"/></article><article className="panel graph-card"><h3>Weekly total</h3><Shape data={data} value={value} kind="donut"/></article></div></section>;
function App() {
  const [d, setD] = useState(),
    [tab, setTab] = useState("Today"),
    [modal, setModal] = useState(false),
    [shop, setShop] = useState([]),
    [nameEdit, setNameEdit] = useState(false),
    [elapsed, setElapsed] = useState(0),
    [thought, setThought] = useState(""),
    [form, setForm] = useState({
      title: "",
      description: "",
      priority: "normal",
      daily: false,
      dueDate: new Date().toISOString().slice(0, 10),
    });
  const load = () =>
    fetch(API + "/dashboard/")
      .then((x) => x.json())
      .then(setD);
  useEffect(load, []);
  useEffect(() => {
    if (!d?.timer.running) return;
    let go = () =>
      setElapsed(Math.floor((Date.now() - new Date(d.timer.startedAt)) / 1000));
    go();
    let i = setInterval(go, 1000);
    return () => clearInterval(i);
  }, [d?.timer.running, d?.timer.startedAt]);
  useEffect(() => {
    if (tab === "Inventory")
      fetch(API + "/shop/")
        .then((x) => x.json())
        .then((x) => setShop(x.items));
  }, [tab]);
  const post = (url, payload = {}) =>
    fetch(API + url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
  const toggle = async (id) => {
    await post(`/tasks/${id}/toggle/`);
    load();
  };
  const del = async (id) => {
    await fetch(API + `/tasks/${id}/`, { method: "DELETE" });
    load();
  };
  const add = async (e) => {
    e.preventDefault();
    await post("/tasks/", form);
    setModal(false);
    setForm({ ...form, title: "", description: "" });
    load();
  };
  const timer = async () => {
    await post("/timer/", { action: d.timer.running ? "stop" : "start" });
    setElapsed(0);
    load();
  };
  const parkThought = async (e) => {
    e.preventDefault();
    if (!thought.trim()) return;
    await post("/distractions/", { text: thought });
    setThought("");
    load();
  };
  const buy = async (key) => {
    let r = await post("/shop/", { key });
    if (!r.ok) alert((await r.json()).error);
    else {
      load();
      fetch(API + "/shop/")
        .then((x) => x.json())
        .then((x) => setShop(x.items));
    }
  };
  const saveName = async () => {
    await fetch(API + "/profile/", {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: d.profile.name }),
    });
    setNameEdit(false);
    load();
  };
  if (!d) return <div className="loading">Loading your command center…</div>;
  let { profile, tasks, summary, week, timeWeek, priority, breakdown, study, badges, mission } =
      d,
    fmt = (s) =>
      `${String(Math.floor(s / 3600)).padStart(2, "0")}:${String(Math.floor(s / 60) % 60).padStart(2, "0")}:${String(s % 60).padStart(2, "0")}`;
  let label = new Intl.DateTimeFormat("en-US", {
    weekday: "long",
    month: "long",
    day: "numeric",
  })
    .format(new Date())
    .toUpperCase();
  return (
    <main>
      <aside>
        <div className="brand">
          <span>✦</span> Questly
        </div>
        <p className="tag">YOUR DAILY ADVENTURE</p>
        <nav>
          {[
            ["Today", Target],
            ["Progress", Trophy],
            ["Inventory", ShoppingBag],
          ].map(([x, I]) => (
            <button
              key={x}
              className={tab === x ? "active" : ""}
              onClick={() => setTab(x)}
            >
              <I />
              {x}
            </button>
          ))}
        </nav>
        <div className="side-bottom">
          <div className="mini-avatar">✦</div>
          <div>
            <b>{profile.name}</b>
            <small>{profile.rank} · Lv. {profile.level}</small>
          </div>
        </div>
      </aside>
      <section className="content">
        <header>
          <div>
            <p className="eyebrow">{label}</p>
            <h1>
              Good morning, <em>{profile.name}.</em>{" "}
              <button className="edit-name" onClick={() => setNameEdit(true)}>
                <User />
              </button>
            </h1>
            <p className="sub">
              Trade distraction for progress — one focused quest at a time.
            </p>
          </div>
          <button className="add" onClick={() => setModal(true)}>
            <Plus /> New quest
          </button>
        </header>
        {tab === "Today" && (
          <>
            <div className="stat-grid">
              <article className="level-card">
                <div className="level-ring">
                  <b>{profile.level}</b>
                  <small>LEVEL</small>
                </div>
                <div>
                  <p>
                    Current XP <b>{profile.currentXp} / 250</b>
                  </p>
                  <div className="progress">
                    <i
                      style={{ width: `${(profile.currentXp / 250) * 100}%` }}
                    />
                  </div>
                  <small>
                    {250 - profile.currentXp} XP until level {profile.level + 1}
                  </small>
                </div>
                <Sparkles className="spark" />
              </article>
              <article className="stat">
                <span className="icon flame">
                  <Flame />
                </span>
                <div>
                  <small>Current streak</small>
                  <b>{profile.streak} days</b>
                  <em>Best: {profile.bestStreak} days</em>
                </div>
              </article>
              <article className="stat">
                <span className="icon target">
                  <Target />
                </span>
                <div>
                  <small>Today’s progress</small>
                  <b>
                    {summary.completed} / {summary.total} quests
                  </b>
                  <em>{summary.rate}% complete</em>
                </div>
              </article>
            </div>
            <div className="focus-timer">
              <div>
                <span className="timer-icon">
                  <Timer />
                </span>
                <p className="eyebrow">FOCUS FORGE · +5 XP PER 5 MINUTES</p>
                <h2>
                  {d.timer.running
                    ? "Focus session in progress"
                    : "Ready for a deep-work session?"}
                </h2>
              </div>
              <b className="clock">{fmt(elapsed)}</b>
              <button
                className={d.timer.running ? "stop" : "start"}
                onClick={timer}
              >
                {d.timer.running ? (
                  <>
                    <Square /> Finish & claim XP
                  </>
                ) : (
                  <>
                    <Play /> Start focus timer
                  </>
                )}
              </button>
            </div>
            <div className="focus-tools">
              <article><p className="eyebrow">TODAY'S FOCUS QUEST</p><b>{study.todayMinutes} / {profile.dailyGoal} minutes</b><i><span style={{width: `${Math.min(100, study.todayMinutes / profile.dailyGoal * 100)}%`}} /></i><small>Set your own pace; every focused block adds XP.</small></article>
              <form onSubmit={parkThought}><p className="eyebrow">PARK A DISTRACTION</p><b>Thinking about something else?</b><div><input value={thought} onChange={e=>setThought(e.target.value)} placeholder="Write it down, then return to focus…" /><button>Park it</button></div><small>{d.distractions} thought{d.distractions===1?"":"s"} safely parked</small></form>
            </div>
            <article className={"daily-mission " + (mission.completed ? "mission-complete" : "")}>
              <div className="mission-medal">⚔️</div>
              <div className="mission-copy"><p className="eyebrow">LEVEL-SCALED DAILY MISSION</p><h2>{mission.completed ? "Mission complete — reward claimed!" : "The Discipline Trial"}</h2><p>Study <b>{study.todayMinutes}/{mission.studyMinutes} min</b> · Complete <b>{mission.easyDone}/{mission.easyTarget} easy</b> · Complete <b>{mission.legendaryDone}/{mission.legendaryTarget} legendary</b></p><div className="mission-progress"><i><span style={{width:`${Math.min(100,(study.todayMinutes/mission.studyMinutes*34)+(mission.easyDone/Math.max(1,mission.easyTarget)*33)+(mission.legendaryDone/Math.max(1,mission.legendaryTarget)*33))}%`}}/></i></div></div>
              <div className="mission-reward"><b>{mission.completed ? "✓" : `+${mission.reward}`}</b><small>{mission.completed ? "COMPLETED" : "MISSION XP"}</small><em>Miss it: −{mission.penalty} XP</em></div>
            </article>
            <div className="board">
              <div className="panel quests">
                <div className="panel-head">
                  <div>
                    <p className="eyebrow">TODAY’S QUESTS</p>
                    <h2>Make today count.</h2>
                  </div>
                  <span className="badge">
                    {summary.total - summary.completed} remaining
                  </span>
                </div>
                <div className="quest-list">
                  {tasks.length ? (
                    tasks.map((t) => (
                      <div
                        className={"quest " + (t.completed ? "done" : "")}
                        key={t.id}
                      >
                        <button className="check" onClick={() => toggle(t.id)}>
                          {t.completed && <Check />}
                        </button>
                        <div className="quest-copy">
                          <b>{t.title}</b>
                          {t.description && <small>{t.description}</small>}
                          <span
                            className="priority"
                            style={{
                              color: pri[t.priority][1],
                              background: pri[t.priority][1] + "18",
                            }}
                          >
                            {pri[t.priority][0]}
                          </span>
                          {t.daily && <span className="repeat">↻ Daily</span>}
                        </div>
                        <div className="xp">
                          +{t.xp}
                          <small>XP</small>
                        </div>
                        <button className="delete" onClick={() => del(t.id)}>
                          <Trash2 />
                        </button>
                      </div>
                    ))
                  ) : (
                    <div className="empty">
                      No quests yet. Add one and begin your streak! ✦
                    </div>
                  )}
                </div>
                <button className="new-row" onClick={() => setModal(true)}>
                  <Plus /> Add another quest
                </button>
              </div>
              <div className="panel chart">
                <p className="eyebrow">WEEKLY XP</p>
                <h2>Momentum graph</h2>
                <Bar data={week} />
                <div className="chart-footer">
                  <span>
                    <i /> XP earned
                  </span>
                  <b>
                    <Trophy /> {profile.points} XP wallet
                  </b>
                </div>
              </div>
            </div>
            <div className="game-row">
              <article className="boss-card">
                <div><p className="eyebrow">DAILY BOSS BATTLE</p><h2>{summary.completed === summary.total && summary.total ? "Boss defeated! ✦" : "Defeat the distraction dragon"}</h2><p>Complete every quest today to protect your streak.</p></div>
                <div className="boss-meter"><b>{summary.completed}/{summary.total}</b><i><span style={{width:`${summary.rate}%`}}/></i><small>{summary.rate}% power</small></div>
              </article>
              <article className="badge-panel"><p className="eyebrow">ACHIEVEMENTS</p><div>{badges.map(b=><span key={b.name} title={b.hint} className={b.unlocked ? "earned" : ""}><i>{b.icon}</i><small>{b.name}</small></span>)}</div></article>
            </div>
            <div className="insight">
              <span>✦</span>
              <div>
                <b>Daily rule</b>
                <p>
                  Unfinished dated and daily quests automatically lose half
                  their XP at midnight. Your streak needs action!
                </p>
              </div>
            </div>
          </>
        )}
        {tab === "Progress" && (
          <section className="analytics">
            <div className="section-title">
              <p className="eyebrow">YOUR COMMAND CENTER</p>
              <h2>Progress analytics</h2>
              <span>Ten charts: five for weekly XP, five for study time.</span>
            </div>
            <FiveCharts title="WEEKLY XP PERFORMANCE" data={week} value="xp" color="purple" />
            <FiveCharts title="DAILY STUDY HOURS" data={timeWeek} value="minutes" color="mint" />
          </section>
        )}
        {tab === "Inventory" && (
          <section className="inventory">
            <div className="section-title">
              <p className="eyebrow">REWARD VAULT</p>
              <h2>Spend XP with purpose</h2>
              <span>
                You have <b>{profile.points} XP</b> in your wallet. Earn it with
                quests and focus sessions.
              </span>
            </div>
            <div className="shop-grid">
              {shop.map((item) => (
                <article
                  className={"shop-item " + (item.owned ? "owned" : "")}
                  key={item.key}
                >
                  <span>{item.icon}</span>
                  <h3>{item.name}</h3>
                  <p>{item.description}</p>
                  <button disabled={item.owned} onClick={() => buy(item.key)}>
                    {item.owned ? "In your inventory" : `${item.cost} XP`}
                  </button>
                </article>
              ))}
            </div>
          </section>
        )}
        {modal && (
          <div className="overlay">
            <form className="modal" onSubmit={add}>
              <button
                type="button"
                className="close"
                onClick={() => setModal(false)}
              >
                <X />
              </button>
              <p className="eyebrow">NEW QUEST</p>
              <h2>What will you conquer?</h2>
              <input
                autoFocus
                placeholder="Quest name"
                value={form.title}
                onChange={(e) => setForm({ ...form, title: e.target.value })}
              />
              <textarea
                placeholder="A short note (optional)"
                value={form.description}
                onChange={(e) =>
                  setForm({ ...form, description: e.target.value })
                }
              />
              <label>Challenge level</label>
              <div className="priorities">
                {Object.entries(pri).map(([k, v]) => (
                  <button
                    type="button"
                    onClick={() => setForm({ ...form, priority: k })}
                    className={form.priority === k ? "chosen" : ""}
                    key={k}
                    style={{ "--c": v[1] }}
                  >
                    {v[0]}
                  </button>
                ))}
              </div>
              <label className="daily-toggle">
                <input
                  type="checkbox"
                  checked={form.daily}
                  onChange={(e) =>
                    setForm({ ...form, daily: e.target.checked })
                  }
                />{" "}
                Repeat every day
              </label>
              {!form.daily && (
                <input
                  type="date"
                  value={form.dueDate}
                  onChange={(e) =>
                    setForm({ ...form, dueDate: e.target.value })
                  }
                />
              )}
              <button className="create">
                Begin quest <Sparkles />
              </button>
            </form>
          </div>
        )}
        {nameEdit && (
          <div className="overlay">
            <form
              className="name-modal"
              onSubmit={(e) => {
                e.preventDefault();
                saveName();
              }}
            >
              <p className="eyebrow">YOUR ADVENTURER NAME</p>
              <h2>What should we call you?</h2>
              <input
                autoFocus
                value={profile.name}
                onChange={(e) =>
                  setD({ ...d, profile: { ...profile, name: e.target.value } })
                }
              />
              <button className="create">Save name</button>
            </form>
          </div>
        )}
      </section>
    </main>
  );
}
createRoot(document.getElementById("root")).render(<App />);
