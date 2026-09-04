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
  Pencil,
  ArrowUpDown,
  Zap,
  Brain,
  RotateCcw,
  ClipboardList,
  Heart,
  BookOpen,
  CalendarDays,
  ScrollText,
  Coins,
  SkipForward,
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
        <div key={x.date} className="bar-point">
          <i
            style={{
              height: `${Math.max(5, (Math.abs(x[value]) / max) * 100)}%`,
            }}
          />
          <span className="bar-tooltip">{x.date}: {x[value]} {value}</span>
          <small>{x.date}</small>
        </div>
      ))}
    </div>
  );
};
const Shape = ({ data, value, kind }) => {
  const [hovered, setHovered] = useState(null);
  const values = data.map((item) => Math.max(0, item[value]));
  const max = Math.max(...values, 1);
  const points = values.map((v, i) => `${i * 45 + 8},${112 - (v / max) * 92}`).join(" ");
  const area = `8,112 ${points} 278,112`;
  if (kind === "donut") return <div className="data-donut"><b>{values.reduce((a,b)=>a+b,0)}</b><small>total</small></div>;
  if (kind === "radar") return <svg className="shape radar-shape" viewBox="0 0 290 125"><polygon points="145,8 270,98 20,98" /><polyline points={points} /></svg>;
  return <div className="shape-wrap"><svg className="shape" viewBox="0 0 290 125">{kind === "area" && <polygon className="area-fill" points={area}/>}<polyline points={points} />{kind === "line" && values.map((v,i)=><circle key={i} cx={i*45+8} cy={112-(v/max)*92} r="6" onMouseEnter={()=>setHovered(i)} onMouseLeave={()=>setHovered(null)} />)}</svg>{hovered !== null && <span className="line-tooltip">{data[hovered].date}: {data[hovered][value]} {value}</span>}</div>;
};
const FiveCharts=({title,data,value,color})=><section className="data-set"><div className="set-heading"><p className="eyebrow">{title}</p><h2>Five views · same data</h2></div><div className="five-charts"><article className="panel graph-card"><h3>Bar chart</h3><Bar data={data} value={value} color={color}/></article><article className="panel graph-card"><h3>Line chart</h3><Shape data={data} value={value} kind="line"/></article><article className="panel graph-card"><h3>Area chart</h3><Shape data={data} value={value} kind="area"/></article><article className="panel graph-card"><h3>Focus radar</h3><Shape data={data} value={value} kind="radar"/></article><article className="panel graph-card"><h3>Weekly total</h3><Shape data={data} value={value} kind="donut"/></article></div></section>;
const CompletionOverview = ({ data }) => {
  const activeDays = data.filter((day) => day.total > 0);
  const average = activeDays.length ? Math.round(activeDays.reduce((sum, day) => sum + day.percent, 0) / activeDays.length) : 0;
  const best = activeDays.reduce((winner, day) => !winner || day.percent > winner.percent ? day : winner, null);
  const completed = data.reduce((sum, day) => sum + day.done, 0);
  return <section className="completion-overview panel">
    <div className="completion-heading"><div><p className="eyebrow">FIRST LOOK · TASK COMPLETION</p><h2>Your 7-day completion pulse</h2><span>Every bar and point is the share of scheduled quests you completed that day.</span></div><div className="completion-stats"><span><small>AVERAGE</small><b>{average}%</b></span><span><small>BEST DAY</small><b>{best ? `${best.date} · ${best.percent}%` : "—"}</b></span><span><small>QUESTS DONE</small><b>{completed}</b></span></div></div>
    <div className="completion-chart-grid"><article className="completion-chart"><div className="chart-name"><b>Daily completion</b><small>Bar view</small></div><Bar data={data} value="percent" color="gold" /></article><article className="completion-chart"><div className="chart-name"><b>Completion trend</b><small>Line view</small></div><Shape data={data} value="percent" kind="line" /></article></div>
    <div className="completion-labels">{data.map(day=><span key={day.date}><b>{day.percent}%</b><small>{day.date} · {day.done}/{day.total} quests</small></span>)}</div>
  </section>;
};
function App() {
  const [d, setD] = useState(),
    [tab, setTab] = useState("Today"),
    [modal, setModal] = useState(false),
    [shop, setShop] = useState([]),
    [nameEdit, setNameEdit] = useState(false),
    [elapsed, setElapsed] = useState(0),
    [thought, setThought] = useState(""),
    [sort, setSort] = useState("due"),
    [editing, setEditing] = useState(null),
    [expanded, setExpanded] = useState(null),
    [subText, setSubText] = useState(""),
    [timerTask, setTimerTask] = useState(null),
    [recall, setRecall] = useState(null),
    [recallForm, setRecallForm] = useState({ title: "", category: "" }),
    [plan, setPlan] = useState(null),
    [tools, setTools] = useState(null),
    [missions, setMissions] = useState(null),
    [resourceForm, setResourceForm] = useState({ title:"", url:"", category:"" }),
    [form, setForm] = useState({
      title: "",
      description: "",
      category: "",
      importance: 50,
      estimatedMinutes: 30,
      priority: "normal",
      daily: false,
      dueDate: new Date().toISOString().slice(0, 10),
    });
  const load = () =>
    fetch(API + "/dashboard/")
      .then((x) => x.json())
      .then(setD);
  useEffect(() => {
    load();
  }, []);
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
  const loadRecall = () => fetch(API + "/recall/").then((x) => x.json()).then(setRecall);
  const loadPlan = () => fetch(API + "/study-plan/").then((x) => x.json()).then(setPlan);
  const loadTools = () => fetch(API + "/study-tools/").then((x) => x.json()).then(setTools);
  useEffect(() => { if (tab === "Recall") loadRecall(); }, [tab]);
  useEffect(() => { if (tab === "Study Plan") { loadPlan(); loadRecall(); } }, [tab]);
  useEffect(() => { if (tab === "Growth") loadTools(); }, [tab]);
  useEffect(() => { if (tab === "Missions") fetch(API + "/missions/").then(x=>x.json()).then(setMissions); }, [tab]);
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
  const addSubtask = async (taskId) => { if (!subText.trim()) return; await post(`/tasks/${taskId}/subtasks/`, {title:subText}); setSubText(""); load(); };
  const toggleSubtask = async (taskId, subId) => { await post(`/tasks/${taskId}/subtasks/${subId}/`); load(); };
  const editSubtask = async (taskId, sub) => { const title=window.prompt("Edit sub-task",sub.title); if (title?.trim()) { await fetch(API+`/tasks/${taskId}/subtasks/${sub.id}/`,{method:"PATCH",headers:{"Content-Type":"application/json"},body:JSON.stringify({title})}); load(); } };
  const del = async (id) => {
    await fetch(API + `/tasks/${id}/`, { method: "DELETE" });
    load();
  };
  const openEdit = (t) => {
    setForm({ title:t.title, description:t.description, category:t.category || "", importance:t.importance ?? 50, estimatedMinutes:t.estimatedMinutes ?? 30, priority:t.priority, daily:t.daily, dueDate:t.dueDate });
    setEditing(t); setModal(true);
  };
  const edit = async (e) => {
    e.preventDefault();
    await fetch(API + `/tasks/${editing.id}/`, { method:"PATCH", headers:{"Content-Type":"application/json"}, body:JSON.stringify(form) });
    setEditing(null); setModal(false); setForm({ ...form, title:"", description:"" }); load();
  };
  const add = async (e) => {
    e.preventDefault();
    await post("/tasks/", form);
    setModal(false);
    setForm({ ...form, title: "", description: "" });
    load();
  };
  const timer = async (taskId = timerTask) => {
    await post("/timer/", { action: d.timer.running ? "stop" : "start", taskId });
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
  const useItem = async (key) => {
    let r = await fetch(API + "/shop/", { method:"PATCH", headers:{"Content-Type":"application/json"}, body:JSON.stringify({key}) });
    if (!r.ok) alert((await r.json()).error);
    else { load(); fetch(API + "/shop/").then(x=>x.json()).then(x=>setShop(x.items)); }
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
  const addRecall = async (e) => {
    e.preventDefault();
    if (!recallForm.title.trim()) return;
    const r = await post("/recall/", recallForm);
    if (!r.ok) return alert((await r.json()).error);
    setRecallForm({ title: "", category: "" }); loadRecall();
  };
  const reviewRecall = async (topic) => {
    const raw = window.prompt(`How well did you recall “${topic.title}”? (0–100)`, topic.lastScore ?? "");
    if (raw === null) return;
    const score = Number(raw);
    if (!Number.isInteger(score) || score < 0 || score > 100) return alert("Please enter a whole number from 0 to 100.");
    const r = await post(`/recall/${topic.id}/review/`, { score });
    const data = await r.json();
    if (!r.ok) return alert(data.error);
    alert(data.suggestion); loadRecall();
  };
  const savePlan = async (e) => {
    e.preventDefault();
    await fetch(API + "/study-plan/", { method:"PATCH", headers:{"Content-Type":"application/json"}, body:JSON.stringify({ intention:plan.intention, plannedMinutes:Number(plan.plannedMinutes), energy:plan.energy, reflection:plan.reflection }) });
    loadPlan();
  };
  const saveTool = async (section, payload) => { await fetch(API+"/study-tools/", {method:"PATCH",headers:{"Content-Type":"application/json"},body:JSON.stringify({section,...payload})}); loadTools(); };
  const addResource = async (e) => { e.preventDefault(); if (!resourceForm.title.trim()) return; await post("/study-tools/",resourceForm); setResourceForm({title:"",url:"",category:""}); loadTools(); };
  const removeResource = async (id) => { await fetch(API+`/resources/${id}/`,{method:"DELETE"}); loadTools(); };
  const useToken = async (task, action) => {
    const r = await post(`/tasks/${task.id}/token/`, { action });
    const result = await r.json();
    if (!r.ok) return alert(result.error);
    if (action === "choose") { setTimerTask(String(task.id)); await timer(task.id); }
    load();
    if (tab === "Missions") fetch(API + "/missions/").then(x=>x.json()).then(setMissions);
  };
  if (!d) return <div className="loading">Loading your command center…</div>;
  let { profile, tasks = [], summary, week = [], timeWeek = [], completionWeek = [], priority, breakdown, study, badges = [], mission } =
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
            ["Missions", ScrollText],
            ["Study Plan", ClipboardList],
            ["Growth", Heart],
            ["Progress", Trophy],
            ["Recall", Brain],
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
              <article className="level-card" style={{"--level-color":profile.levelIdentity?.color,"--level-soft":profile.levelIdentity?.softColor}}>
                <div className="level-ring">
                  <span>{profile.levelIdentity?.icon || "✦"}</span>
                  <b>{profile.level}</b>
                  <small>LEVEL</small>
                </div>
                <div>
                  <p>
                    <strong>{profile.levelIdentity?.title || profile.rank}</strong> · Current XP <b>{profile.currentXp} / {profile.nextXp}</b>
                  </p>
                  <div className="progress">
                    <i
                      style={{ width: `${(profile.currentXp / profile.nextXp) * 100}%` }}
                    />
                  </div>
                  <small>
                    {profile.nextXp - profile.currentXp} XP until level {profile.level + 1} · next level costs {profile.nextXp} XP
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
              {!d.timer.running && <select className="timer-task" value={timerTask || ""} onChange={e=>setTimerTask(e.target.value || null)}><option value="">General study</option>{tasks.map(t=><option key={t.id} value={t.id}>{t.title}</option>)}</select>}
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
            {d.recommendation && <article className="next-task panel"><div><p className="eyebrow">YOUR NEXT TASK</p><h2>{d.recommendation.title}</h2><span>{d.recommendation.reason} · about {d.recommendation.remainingMinutes} min remaining</span></div><button className="create" onClick={()=>{setTimerTask(String(d.recommendation.id)); timer(d.recommendation.id);}}><Play /> Start this task</button></article>}
            {d.boost.active && <div className="boost-live"><Zap /> A boost is active until {new Date(d.boost.until).toLocaleTimeString([], {hour:"2-digit",minute:"2-digit"})} — XP rewards are doubled.</div>}
            <div className="focus-tools">
              <article><p className="eyebrow">TODAY'S FOCUS QUEST</p><b>{study.todayMinutes} / {profile.dailyGoal} minutes</b><i><span style={{width: `${Math.min(100, study.todayMinutes / profile.dailyGoal * 100)}%`}} /></i><small>Set your own pace; every focused block adds XP.</small></article>
              <form onSubmit={parkThought}><p className="eyebrow">PARK A DISTRACTION</p><b>Thinking about something else?</b><div><input value={thought} onChange={e=>setThought(e.target.value)} placeholder="Write it down, then return to focus…" /><button>Park it</button></div><small>{d.distractions} thought{d.distractions===1?"":"s"} safely parked</small></form>
            </div>
            <article className={"daily-mission " + (mission.completed ? "mission-complete" : "")}>
              <div className="mission-medal">⚔️</div>
              <div className="mission-copy"><p className="eyebrow">LEVEL-SCALED DAILY MISSION</p><h2>{mission.completed ? "Mission complete — reward claimed!" : mission.title}</h2><p>{mission.flavor} Study <b>{study.todayMinutes}/{mission.studyMinutes} min</b> · Complete <b>{mission.easyDone}/{mission.easyTarget} easy</b> · Complete <b>{mission.legendaryDone}/{mission.legendaryTarget} legendary</b></p><div className="mission-progress"><i><span style={{width:`${Math.min(100,(study.todayMinutes/mission.studyMinutes*34)+(mission.easyDone/Math.max(1,mission.easyTarget)*33)+(mission.legendaryDone/Math.max(1,mission.legendaryTarget)*33))}%`}}/></i></div></div>
              <div className="mission-reward"><b>{mission.completed ? "✓" : `+${mission.reward}`}</b><small>{mission.completed ? "COMPLETED" : "MISSION XP"}</small><strong>+{mission.tokens} token</strong><em>Miss it: −{mission.penalty} XP</em></div>
            </article>
            <section className="upcoming-missions"><div className="section-title"><p className="eyebrow">MISSION RADAR</p><h2>Coming up this week</h2><span>Preview the next 7 missions from the 100-mission rotation.</span></div><div className="mission-preview-grid">{(d.upcomingMissions || []).map(m=><article key={m.date}><b>{m.day} · {m.title}</b><p>{m.flavor}</p><small>{m.studyMinutes} min · {m.easyTarget} easy · {m.legendaryTarget} legendary</small><em>+{m.reward} XP · miss −{m.penalty}</em></article>)}</div></section>
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
                <label className="sort-control"><ArrowUpDown /> Order <select value={sort} onChange={e=>setSort(e.target.value)}><option value="due">Due date</option><option value="priority">Priority</option><option value="title">Name</option></select></label>
                <div className="quest-list">
                  {tasks.length ? (
                    [...tasks].sort((a,b)=>sort==="title"?a.title.localeCompare(b.title):sort==="priority"?["legendary","high","normal","low"].indexOf(a.priority)-["legendary","high","normal","low"].indexOf(b.priority):a.dueDate.localeCompare(b.dueDate)).map((t) => (
                      <React.Fragment key={t.id}><div
                        className={"quest " + (t.completed ? "done" : "")}
                        key={t.id}
                      >
                        <button className="check" onClick={() => toggle(t.id)}>
                          {t.completed && <Check />}
                        </button>
                        <div className="quest-copy" onClick={() => setExpanded(expanded===t.id ? null : t.id)}>
                          <b>{t.title} {t.subtasks?.length ? <span className="sub-count">{t.subtasks.filter(s=>s.completed).length}/{t.subtasks.length} steps</span> : ""}</b>
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
                          <span className="importance">{t.importance}/100 important</span>
                          {t.category && <span className="repeat">{t.category}</span>}
                          {t.daily && <span className="repeat">↻ Daily</span>}
                        </div>
                        <div className="xp">
                          +{t.xp}
                          <small>XP</small>
                        </div>
                        {t.skipped && <span className="skipped-tag">Ignored</span>}
                        <button className="delete" onClick={() => del(t.id)}>
                          <Trash2 />
                        </button>
                        <button className="delete edit-task" onClick={() => openEdit(t)} title="Edit quest"><Pencil /></button>
                      </div>
                      {expanded===t.id && <div className="subtasks"><p>SUB-TASKS · {t.subtaskXp} XP EACH</p>{t.subtasks?.map(s=><div className={s.completed?"sub done":"sub"} key={s.id}><button onClick={()=>toggleSubtask(t.id,s.id)}>{s.completed?<Check/>:""}</button><span>{s.title}</span><small>+{s.xp} XP</small><button className="sub-edit" onClick={()=>editSubtask(t.id,s)}><Pencil/></button></div>)}<div className="sub-add"><input value={subText} onChange={e=>setSubText(e.target.value)} placeholder="Add a sub-task"/><button onClick={()=>addSubtask(t.id)}><Plus/> Add</button></div></div>}</React.Fragment>
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
            <CompletionOverview data={completionWeek} />
            <FiveCharts title="WEEKLY XP PERFORMANCE" data={week} value="xp" color="purple" />
            <FiveCharts title="DAILY STUDY HOURS" data={timeWeek} value="minutes" color="mint" />
            <section className="task-insights">
              <div className="section-title"><p className="eyebrow">TASK COACH</p><h2>{d.recommendation ? `Focus on ${d.recommendation.title}` : "Create a quest to get coaching"}</h2><span>{d.recommendation ? d.recommendation.reason : ""}</span></div>
              <div className="task-graph-grid">{(d.taskStats || []).map(t=><article className="panel" key={t.id}><b>{t.title}</b><small>{t.done} done · {t.misses} missed · {t.minutes} min ({t.timePercent}% of total)</small><Shape data={t.history} value="xp" kind="line" /><span className="line-caption">7-day XP trend</span><Shape data={t.timeHistory} value="minutes" kind="line" /><span className="line-caption">7-day study-time trend</span></article>)}</div>
            </section>
            <section className="activity panel"><p className="eyebrow">REWARD LEDGER</p><h2>Every change explained</h2>{(d.activity || []).length ? d.activity.map((a,i)=><div key={i} className={a.amount<0?"loss":"gain"}><b>{a.amount>0?"+": ""}{a.amount} {a.kind === "token" ? "token" : "XP"}</b><span>{a.reason}<small>{a.at}</small></span></div>):<p>No reward events yet.</p>}</section>
          </section>
        )}
        {tab === "Missions" && (
          <section className="missions-page">
            <div className="section-title"><p className="eyebrow">MISSION BOARD</p><h2>One hundred missions await</h2><span>Complete each daily mission for XP and tokens. Tokens give you one tactical choice.</span></div>
            <div className="token-summary panel"><Coins /><div><small>MISSION TOKENS</small><b>{profile.tokens}</b><span>Earned from completed missions</span></div><p>Spend 1 token to choose the quest you want to focus on now, or to ignore one quest scheduled today. Ignoring a quest costs half its XP reward.</p></div>
            <section className="token-powers"><article className="panel"><p className="eyebrow">CHOOSE YOUR NEXT QUEST · 1 TOKEN</p><h2>Set your own focus</h2><span>Choose a quest and immediately begin a focus session.</span><div className="token-task-list">{tasks.filter(t=>!t.completed&&!t.skipped).map(t=><button key={t.id} disabled={!profile.tokens || d.timer.running} onClick={()=>useToken(t,"choose")}><b>{t.title}</b><small>{t.tokenSelected ? "Chosen now" : "Choose & start"}</small></button>)}{!tasks.filter(t=>!t.completed&&!t.skipped).length&&<p className="empty">No unfinished quests for today.</p>}</div></article><article className="panel"><p className="eyebrow">IGNORE ONE QUEST · 1 TOKEN</p><h2>Protect your day</h2><span>Skip a scheduled quest today for a half-XP penalty. It cannot be completed later today.</span><div className="token-task-list">{tasks.filter(t=>!t.completed&&!t.skipped).map(t=><button key={t.id} disabled={!profile.tokens} onClick={()=>{if(window.confirm(`Ignore “${t.title}” for today? You will lose ${Math.floor(t.xp/2)} XP.`))useToken(t,"skip")}}><b>{t.title}</b><small><SkipForward /> Ignore · −{Math.floor(t.xp/2)} XP</small></button>)}</div></article></section>
            <section className="mission-catalog"><div className="section-title"><p className="eyebrow">100-MISSION ROTATION</p><h2>Your mission path</h2><span>Each mission has its own requirements, XP, and token reward.</span></div><div className="mission-catalog-grid">{missions?.missions.map(m=><article className={m.completed?"done":""} key={m.date}><small>MISSION #{m.number} · {new Date(m.date+"T00:00:00").toLocaleDateString(undefined,{month:"short",day:"numeric"})}</small><b>{m.completed?"✓ ":""}{m.title}</b><p>{m.flavor}</p><span>{m.studyMinutes} min · {m.easyTarget} easy · {m.legendaryTarget} legendary</span><footer>+{m.reward} XP · +{m.tokens} <Coins /></footer></article>)}</div></section>
          </section>
        )}
        {tab === "Study Plan" && plan && (
          <section className="study-plan-page">
            <div className="section-title"><p className="eyebrow">DAILY STUDY SYSTEM</p><h2>Make a realistic plan</h2><span>Choose one meaningful outcome, match the workload to your energy, then close the day with a note.</span></div>
            <div className="plan-map">
              <article className="plan-hero"><p className="eyebrow">TODAY’S STUDY MAP</p><h2>{plan.intention || "Set an intention below"}</h2><div><span><Timer /> {plan.studiedMinutes} / {plan.plannedMinutes} min focused</span><span><Target /> {plan.todayQuests} quest{plan.todayQuests===1?"":"s"}</span><span><Brain /> {plan.dueRecall} recall due</span></div><i><b style={{width:`${Math.min(100, plan.studiedMinutes / Math.max(1,plan.plannedMinutes) * 100)}%`}} /></i></article>
              <article className="plan-tip"><p className="eyebrow">SMART PACING</p><b>{plan.energy <= 2 ? "Low energy: choose one small win, then rest." : plan.energy === 3 ? "Steady energy: use one focused block before switching tasks." : "High energy: begin with the hardest thing while momentum is strong."}</b><small>Recall topics due today: {plan.dueRecall}. Use the Recall tab after your focus block.</small></article>
            </div>
            <form className="plan-form panel" onSubmit={savePlan}><p className="eyebrow">CHECK IN</p><h2>Design today</h2><label>Most important outcome<input value={plan.intention} onChange={e=>setPlan({...plan,intention:e.target.value})} placeholder="e.g. Understand chapter 4 and solve 10 problems" /></label><div className="plan-fields"><label>Planned focus minutes<input type="number" min="15" max="600" value={plan.plannedMinutes} onChange={e=>setPlan({...plan,plannedMinutes:e.target.value})} /></label><label>Energy right now<div className="energy-picks">{[1,2,3,4,5].map(n=><button type="button" className={plan.energy===n?"picked":""} onClick={()=>setPlan({...plan,energy:n})} key={n}>{n}</button>)}</div></label></div><label>End-of-day reflection <textarea value={plan.reflection} onChange={e=>setPlan({...plan,reflection:e.target.value})} placeholder="What worked, what was difficult, and what will you change tomorrow?" /></label><button className="create">Save study plan <Sparkles /></button></form>
            <section className="plan-queue panel"><p className="eyebrow">SUGGESTED ORDER</p><h2>Start with the next useful action</h2><ol>{plan.dueRecall > 0 && <li>Review {plan.dueRecall} memory topic{plan.dueRecall===1?"":"s"} due today.</li>}{(d.recommendedTasks || []).slice(0,3).map(t=><li key={t.id}>Work on: <b>{t.title}</b> <small>({t.reason})</small></li>)}{!plan.dueRecall && !(d.recommendedTasks || []).length && <li>Add one quest or a recall topic to begin.</li>}</ol></section>
          </section>
        )}
        {tab === "Growth" && tools && (
          <section className="growth-page">
            <div className="section-title"><p className="eyebrow">STUDY FOUNDATION</p><h2>Growth tools</h2><span>Five small systems that protect your focus and make your study time more effective.</span></div>
            <div className="growth-grid">
              <form className="growth-card exam-card" onSubmit={e=>{e.preventDefault();saveTool("settings",{examName:tools.settings.examName,examDate:tools.settings.examDate,weeklyGoal:Number(tools.settings.weeklyGoal)})}}><CalendarDays /><p className="eyebrow">1 · EXAM COMPASS</p><h3>{tools.settings.daysLeft === null ? "Set your next milestone" : tools.settings.daysLeft < 0 ? "Exam date has passed" : `${tools.settings.daysLeft} days to go`}</h3><input value={tools.settings.examName} onChange={e=>setTools({...tools,settings:{...tools.settings,examName:e.target.value}})} placeholder="Exam or milestone name"/><input type="date" value={tools.settings.examDate} onChange={e=>setTools({...tools,settings:{...tools.settings,examDate:e.target.value}})}/><button>Save countdown</button></form>
              <form className="growth-card" onSubmit={e=>{e.preventDefault();saveTool("settings",{weeklyGoal:Number(tools.settings.weeklyGoal)})}}><Timer /><p className="eyebrow">2 · WEEKLY TARGET</p><h3>{tools.weekMinutes} / {tools.settings.weeklyGoal} minutes</h3><i><b style={{width:`${Math.min(100,tools.weekMinutes/Math.max(1,tools.settings.weeklyGoal)*100)}%`}}/></i><input type="number" min="30" value={tools.settings.weeklyGoal} onChange={e=>setTools({...tools,settings:{...tools.settings,weeklyGoal:e.target.value}})} /><small>Set a realistic weekly focus target.</small><button>Save target</button></form>
              <form className="growth-card wellbeing-card" onSubmit={e=>{e.preventDefault();saveTool("wellbeing",{...tools.wellbeing,sleepHours:Number(tools.wellbeing.sleepHours),waterCups:Number(tools.wellbeing.waterCups),movementMinutes:Number(tools.wellbeing.movementMinutes)})}}><Heart /><p className="eyebrow">3 · WELLBEING CHECK</p><h3>Support your brain</h3><div className="wellbeing-fields"><label>Sleep<input type="number" step="0.5" value={tools.wellbeing.sleepHours} onChange={e=>setTools({...tools,wellbeing:{...tools.wellbeing,sleepHours:e.target.value}})}/></label><label>Water<input type="number" value={tools.wellbeing.waterCups} onChange={e=>setTools({...tools,wellbeing:{...tools.wellbeing,waterCups:e.target.value}})}/></label><label>Move min<input type="number" value={tools.wellbeing.movementMinutes} onChange={e=>setTools({...tools,wellbeing:{...tools.wellbeing,movementMinutes:e.target.value}})}/></label></div><button>Save check-in</button></form>
              <form className="growth-card reflection-card" onSubmit={e=>{e.preventDefault();saveTool("reflection",tools.reflection)}}><ClipboardList /><p className="eyebrow">4 · WEEKLY REVIEW</p><h3>Learn from the week</h3><textarea value={tools.reflection.win} onChange={e=>setTools({...tools,reflection:{...tools.reflection,win:e.target.value}})} placeholder="What went well?"/><textarea value={tools.reflection.blocker} onChange={e=>setTools({...tools,reflection:{...tools.reflection,blocker:e.target.value}})} placeholder="What got in the way?"/><textarea value={tools.reflection.nextFocus} onChange={e=>setTools({...tools,reflection:{...tools.reflection,nextFocus:e.target.value}})} placeholder="Next week's focus"/><button>Save review</button></form>
              <article className="growth-card resource-card"><BookOpen /><p className="eyebrow">5 · STUDY SHELF</p><h3>Resources and distractions</h3><form onSubmit={addResource}><input value={resourceForm.title} onChange={e=>setResourceForm({...resourceForm,title:e.target.value})} placeholder="Resource title"/><input value={resourceForm.category} onChange={e=>setResourceForm({...resourceForm,category:e.target.value})} placeholder="Subject"/><input value={resourceForm.url} onChange={e=>setResourceForm({...resourceForm,url:e.target.value})} placeholder="Link (optional)"/><button>Add resource</button></form><div className="tool-list">{tools.resources.map(r=><div key={r.id}>{r.url?<a href={r.url} target="_blank" rel="noreferrer">{r.title}</a>:<b>{r.title}</b>}<button onClick={()=>removeResource(r.id)}>×</button></div>)}{tools.distractions.map(x=><div className="parked" key={x.id}><span>Parked: {x.text}</span><button onClick={()=>saveTool("distraction",{id:x.id})}>Done</button></div>)}</div></article>
            </div>
          </section>
        )}
        {tab === "Inventory" && (
          <section className="inventory">
            <div className="section-title">
              <p className="eyebrow">REWARD VAULT</p>
              <h2>Spend XP with purpose</h2>
              <span>
                You have <b>{profile.points} XP</b> in your wallet and <b>{shop.length}</b> items to discover.
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
                  <button disabled={!item.quantity && profile.points < item.cost} onClick={() => item.quantity ? useItem(item.key) : buy(item.key)}>
                    {item.activeUntil ? "Active now" : item.quantity ? `Use item (${item.quantity})` : `${item.cost} XP`}
                  </button>
                </article>
              ))}
            </div>
          </section>
        )}
        {tab === "Recall" && (
          <section className="recall-page">
            <div className="section-title"><p className="eyebrow">SPACED REPETITION</p><h2>Recall lab</h2><span>Capture what you learned today. Your score decides when it comes back.</span></div>
            <div className="recall-summary">
              <article><Brain /><small>TOPICS</small><b>{recall?.stats.topics || 0}</b></article>
              <article><RotateCcw /><small>DUE TODAY</small><b>{recall?.stats.due || 0}</b></article>
              <article><Trophy /><small>AVERAGE RECALL</small><b>{recall?.stats.average || 0}%</b></article>
            </div>
            <form className="recall-capture panel" onSubmit={addRecall}>
              <div><p className="eyebrow">LEARNED TODAY</p><h3>Save a memory for tomorrow</h3></div>
              <input value={recallForm.title} onChange={e=>setRecallForm({...recallForm,title:e.target.value})} placeholder="What did you learn? e.g. The phases of mitosis" />
              <input value={recallForm.category} onChange={e=>setRecallForm({...recallForm,category:e.target.value})} placeholder="Task category / subject (optional)" />
              <button className="create"><Plus /> Add to recall</button>
            </form>
            <section className="recall-due panel"><div className="panel-head"><div><p className="eyebrow">REVIEW QUEUE</p><h2>What to recall today</h2></div><span className="badge">{recall?.due.length || 0} ready</span></div>
              {recall?.due.length ? recall.due.map(t=><article className="recall-topic" key={t.id}><div><b>{t.title}</b><small>{t.category || "Uncategorized"} · learned {new Date(t.learnedOn+"T00:00:00").toLocaleDateString()}</small></div><button onClick={()=>reviewRecall(t)}>Recall & score <Brain /></button></article>) : <div className="empty">Nothing is due today. Add something you learned, or enjoy the breathing room. ✦</div>}
            </section>
            <section className="recall-analytics"><div className="section-title"><p className="eyebrow">MEMORY SIGNALS</p><h2>Recall progress</h2><span>Five views of your 7-day recall score. Scores appear after your first review.</span></div><FiveCharts title="RECALL ACCURACY" data={recall?.history || []} value="score" color="gold" /></section>
            <section className="recall-upcoming panel"><p className="eyebrow">NEXT UP</p><h2>Scheduled reviews</h2>{recall?.upcoming.length ? recall.upcoming.map(t=><div className="recall-topic" key={t.id}><div><b>{t.title}</b><small>{t.category || "Uncategorized"} · {t.reviewCount ? `last score ${t.lastScore}%` : "first recall"}</small></div><span className="pill">{t.when}</span></div>) : <p className="empty">Your future review schedule will appear here.</p>}</section>
          </section>
        )}
        {modal && (
          <div className="overlay">
            <form className="modal" onSubmit={editing ? edit : add}>
              <button
                type="button"
                className="close"
                onClick={() => { setModal(false); setEditing(null); }}
              >
                <X />
              </button>
              <p className="eyebrow">{editing ? "EDIT QUEST" : "NEW QUEST"}</p>
              <h2>{editing ? "Tune your challenge" : "What will you conquer?"}</h2>
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
              <div className="planning-fields"><label>Category (optional)<input value={form.category} placeholder="e.g. Maths" onChange={e=>setForm({...form,category:e.target.value})} /></label><label>Importance: <b>{form.importance}/100</b><input type="range" min="0" max="100" value={form.importance} onChange={e=>setForm({...form,importance:Number(e.target.value)})} /></label><label>Estimated minutes<input type="number" min="5" max="1440" value={form.estimatedMinutes} onChange={e=>setForm({...form,estimatedMinutes:Number(e.target.value)})} /></label></div>
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
                {editing ? "Save changes" : "Begin quest"} <Sparkles />
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
