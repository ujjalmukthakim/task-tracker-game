import json
from datetime import date, timedelta
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from .models import ActivityLog, Completion, DailyMission, DailyStudyPlan, DailyWellbeing, Distraction, InventoryItem, Profile, RecallReview, RecallTopic, StudyResource, StudySettings, StudySession, SubTask, Task, WeeklyReflection

XP = {"low": 10, "normal": 25, "high": 50, "legendary": 100}
SHOP = [
 {"key":"double_xp","name":"Double XP Elixir","icon":"⚗️","description":"Double all quest and timer XP for 60 minutes.","cost":180,"effect":"double_xp","duration_minutes":60},
 {"key":"focus_shield","name":"Focus Shield","icon":"🛡️","description":"Blocks the next missed-mission penalty.","cost":140,"effect":"penalty_shield","duration_minutes":0},
 {"key":"time_crystal","name":"Time Crystal","icon":"⌛","description":"Double focus-timer XP for 30 minutes.","cost":110,"effect":"timer_double","duration_minutes":30},
 {"key":"study_cat","name":"Study Cat","icon":"🐈","description":"A permanent desk companion and achievement.","cost":260,"effect":"cosmetic","duration_minutes":0},
 {"key":"forest_theme","name":"Forest Theme","icon":"🌲","description":"A permanent collectible for your study realm.","cost":320,"effect":"cosmetic","duration_minutes":0},]
ITEM_SERIES = [
 ("Focus Elixir", "⚗️", "double_xp", 60, "Double all quest and timer XP for 60 minutes."),
 ("Chrono Crystal", "⌛", "timer_double", 30, "Double focus-timer XP for 30 minutes."),
 ("Guardian Seal", "🛡️", "penalty_shield", 0, "Blocks your next missed-mission penalty."),
 ("Scholar Charm", "📚", "double_xp", 30, "Double all quest and timer XP for 30 minutes."),
 ("Deep Work Rune", "🔷", "timer_double", 45, "Double focus-timer XP for 45 minutes."),
]
ITEM_ADJECTIVES = ["Amber", "Azure", "Blazing", "Celestial", "Crimson", "Dawn", "Emerald", "Frost", "Golden", "Hollow", "Indigo", "Jade", "Kindled", "Lunar", "Midnight", "Nova", "Obsidian", "Prismatic", "Quiet", "Radiant"]
for index, adjective in enumerate(ITEM_ADJECTIVES):
 for series_index, (name, icon, effect, duration, description) in enumerate(ITEM_SERIES):
  number = index * len(ITEM_SERIES) + series_index + 1
  SHOP.append({"key":f"{adjective.lower()}_{name.lower().replace(' ', '_')}","name":f"{adjective} {name}","icon":icon,"description":description,"cost":90 + number * 12,"effect":effect,"duration_minutes":duration})
MISSION_TITLES = ["Dawn Sprint", "Quiet Library", "Iron Will", "Deep Dive", "Focus Forge", "Study Storm", "Chapter Climb", "Memory Vault", "Scholar's Path", "Final Push"]
MISSION_FLAVORS = ["Build momentum before distractions arrive.", "Make a calm promise to your future self.", "Choose the harder useful thing.", "Turn one study block into progress.", "Craft a stronger study habit.", "Channel your energy into the page.", "Move one chapter closer to mastery.", "Give your brain a worthy challenge.", "A little consistency changes everything.", "Finish the day with intention."]
MISSION_PRESETS = [(30,1,0),(45,0,1),(50,2,0),(60,1,1),(75,2,0),(90,0,1),(45,3,0),(60,2,1),(75,1,1),(90,3,0)]
def body(r):
 try:return json.loads(r.body or "{}")
 except json.JSONDecodeError:return {}
def profile():return Profile.objects.get_or_create(pk=1)[0]
def log(amount,reason,kind="xp"):ActivityLog.objects.create(amount=amount,reason=reason,kind=kind)
def add_xp(p,amount,reason):
 p.points+=amount;p.lifetime_xp=max(0,p.lifetime_xp+amount);p.save(update_fields=["points","lifetime_xp","updated_at"]);log(amount,reason)
def add_tokens(p,amount,reason):
 p.tokens=max(0,p.tokens+amount);p.save(update_fields=["tokens","updated_at"]);log(amount,reason,"token")
def level_data(total_xp,wallet=None):
 remaining=max(0,total_xp);level=1;needed=200
 while remaining>=needed:remaining-=needed;level+=1;needed=200+(level-1)*150
 return {"level":level,"currentXp":remaining,"nextXp":needed,"requiredXp":needed,"points":wallet if wallet is not None else total_xp,"lifetimeXp":total_xp}
def rank_title(level):
 ranks=[(1,"Curious Recruit"),(3,"Habit Scout"),(6,"Focus Ranger"),(10,"Quest Knight"),(15,"Study Mage"),(25,"Discipline Legend")]
 return next(title for minimum,title in reversed(ranks) if level>=minimum)
def level_identity(level):
 tiers=[
  (1,"Curious Recruit","🌱","#57b88d","#e7f8ef"),(2,"Trail Starter","🧭","#5f8fd8","#eaf2ff"),
  (3,"Habit Scout","🔭","#8b70d6","#f1edff"),(4,"Routine Builder","🧱","#d78a4a","#fff1e3"),
  (5,"Focus Seeker","🎯","#d75f91","#ffebf3"),(6,"Focus Ranger","🏹","#3ea99a","#e3f8f3"),
  (7,"Knowledge Keeper","📚","#5c7bd5","#e9efff"),(8,"Momentum Maker","⚡","#d5a536","#fff7d9"),
  (9,"Study Strategist","♟️","#7c68c5","#f0ecff"),(10,"Quest Knight","🛡️","#4c91b7","#e6f6fb"),
  (15,"Study Mage","🔮","#9b5fb6","#f8eaff"),(25,"Discipline Legend","👑","#d08d32","#fff2d9"),
 ]
 title,icon,color,soft=next((name,icon,color,soft) for minimum,name,icon,color,soft in reversed(tiers) if level>=minimum)
 return {"title":title,"icon":icon,"color":color,"softColor":soft}
def active_boost(effect=None):
 qs=InventoryItem.objects.filter(active_until__gt=timezone.now(),quantity=0)
 return qs.filter(effect=effect).exists() if effect else qs.exists()
def task_is_complete(task,today):
 """Daily tasks reset each day; one-off tasks stay done once completed."""
 completions=Completion.objects.filter(task=task,completed=True)
 return completions.filter(date=today).exists() if task.is_daily else completions.exists()
def recommendation_for(today):
 """Rank unfinished work by the user's importance mark, urgency, and remaining effort."""
 ranked=[]
 for task in Task.objects.filter(active=True):
  if task_is_complete(task,today):continue
  days_until=(task.due_date-today).days
  urgency=45 if days_until<0 else 35 if days_until==0 else max(0,25-days_until*3)
  studied=StudySession.objects.filter(task=task,ended_at__isnull=False).aggregate(x=Sum("duration_seconds"))["x"] or 0
  studied_minutes=round(studied/60)
  remaining=max(0,task.estimated_minutes-studied_minutes)
  # A short, high-value task gets a small tie-breaker; importance remains dominant.
  score=task.importance+urgency+min(15,round(90/max(15,remaining)))
  reasons=[f"importance {task.importance}/100"]
  if days_until<0:reasons.append("overdue")
  elif days_until==0:reasons.append("due today")
  elif days_until<=7:reasons.append(f"due in {days_until} day" + ("s" if days_until!=1 else ""))
  if studied_minutes:reasons.append(f"{studied_minutes} min already focused")
  ranked.append({"id":task.id,"title":task.title,"category":task.category,"importance":task.importance,"estimatedMinutes":task.estimated_minutes,"studiedMinutes":studied_minutes,"remainingMinutes":remaining,"dueDate":task.due_date.isoformat(),"daily":task.is_daily,"score":score,"tokenSelected":task.token_selected_on==today,"reason":", ".join(reasons)})
 return sorted(ranked,key=lambda item:(not item["tokenSelected"],-item["score"],item["dueDate"],item["title"]))
def serialize_task(t,d):
 subs=list(t.subtasks.order_by("created_at"));share=max(1,XP[t.priority]//len(subs)) if subs else XP[t.priority]
 completion=Completion.objects.filter(task=t,date=d).first()
 return {"id":t.id,"title":t.title,"description":t.description,"category":t.category,"importance":t.importance,"estimatedMinutes":t.estimated_minutes,"priority":t.priority,"daily":t.is_daily,"dueDate":t.due_date.isoformat(),"completed":task_is_complete(t,d),"skipped":bool(completion and not completion.completed and completion.points_awarded<0),"tokenSelected":t.token_selected_on==d,"xp":XP[t.priority],"subtaskXp":share,"subtasks":[{"id":s.id,"title":s.title,"completed":s.completed,"xp":share} for s in subs]}
def active_timer():return StudySession.objects.filter(ended_at__isnull=True).order_by("-started_at").first()
def timer_data():
 s=active_timer();return {"running":bool(s),"startedAt":s.started_at.isoformat() if s else None}
def recall_interval(score):
 """Short intervals for uncertain memories; longer ones after strong recall."""
 if score < 50:return 1,"tomorrow"
 if score < 70:return 3,"in 3 days"
 if score < 85:return 7,"in 1 week"
 if score < 95:return 14,"in 2 weeks"
 return 30,"in 1 month"
def serialize_recall(t,today):
 days=(t.next_review_on-today).days
 when="Today" if days<=0 else "Tomorrow" if days==1 else f"In {days} days"
 return {"id":t.id,"title":t.title,"category":t.category,"learnedOn":t.learned_on.isoformat(),"nextReviewOn":t.next_review_on.isoformat(),"lastScore":t.last_score,"reviewCount":t.review_count,"due":days<=0,"when":when}
def apply_penalties():
 today,p,changed=timezone.localdate(),profile(),False
 for t in Task.objects.filter(active=True):
  if t.is_daily:
   start=max(t.created_at.date(),t.due_date);days=[start+timedelta(days=i) for i in range(max(0,(today-start).days))]
  else:days=[t.due_date] if t.due_date<today else []
  for day in days:
   c,made=Completion.objects.get_or_create(task=t,date=day)
   if made:
    c.points_awarded=-(XP[t.priority]//2);c.save(update_fields=["points_awarded"]);p.points+=c.points_awarded;p.lifetime_xp=max(0,p.lifetime_xp+c.points_awarded);log(c.points_awarded,f"Missed {t.title} on {day:%b %d}","penalty");changed=True
 if changed:p.save(update_fields=["points","lifetime_xp","updated_at"])
def mission_plan(day,level):
 """A deterministic 100-mission rotation; previews always match the unlocked daily mission."""
 index=day.toordinal()%100;tier=(level-1)//3;base_minutes,easy,legend=MISSION_PRESETS[index%len(MISSION_PRESETS)]
 return {"title":f"{MISSION_TITLES[index%10]} #{index+1}","flavor":MISSION_FLAVORS[(index//10)%10],"study_minutes":min(240,base_minutes+tier*15),"easy_target":easy+tier//3,"legendary_target":legend+(1 if tier>=4 and index%4==0 else 0),"reward_xp":70+tier*20+index%5*5,"reward_tokens":1+int(index%20==19),"penalty_xp":40+tier*20}
def daily_mission(today,p,minutes,counts):
 shield=InventoryItem.objects.filter(effect="penalty_shield",quantity__gt=0).first()
 for old in DailyMission.objects.filter(date__lt=today,completed=False,punished=False):
  old.punished=True;old.save(update_fields=["punished"])
  if shield:
   shield.quantity-=1;shield.save(update_fields=["quantity"]);log(0,f"Focus Shield blocked the missed mission penalty for {old.date:%b %d}","shield");shield=None
  else:add_xp(p,-old.penalty_xp,f"Missed daily mission on {old.date:%b %d}")
 plan=mission_plan(today,level_data(p.lifetime_xp,p.points)["level"])
 m,_=DailyMission.objects.get_or_create(date=today,defaults={k:plan[k] for k in ["study_minutes","easy_target","legendary_target","reward_xp","reward_tokens","penalty_xp"]})
 met=minutes>=m.study_minutes and counts["low"]>=m.easy_target and counts["legendary"]>=m.legendary_target
 if met and not m.completed:
  m.completed=True;m.save(update_fields=["completed"]);add_xp(p,m.reward_xp,f"Completed daily mission for {today:%b %d}");add_tokens(p,m.reward_tokens,f"Mission token earned for {today:%b %d}")
 return m
@csrf_exempt
def dashboard(r):
 if r.method!="GET":return JsonResponse({"error":"GET only"},status=405)
 apply_penalties();today,p=timezone.localdate(),profile();todo=[serialize_task(t,today) for t in Task.objects.filter(active=True) if t.is_daily or t.due_date==today]
 week=[];timeweek=[];completion_week=[]
 for o in range(6,-1,-1):
  day=today-timedelta(days=o);cs=Completion.objects.filter(date=day);secs=StudySession.objects.filter(started_at__date=day,ended_at__isnull=False).aggregate(x=Sum("duration_seconds"))["x"] or 0
  scheduled=Task.objects.filter(active=True,created_at__date__lte=day).filter(Q(is_daily=True)|Q(due_date=day))
  total=scheduled.count();done=cs.filter(task__in=scheduled,completed=True).count()
  week.append({"date":day.strftime("%a"),"xp":cs.aggregate(x=Sum("points_awarded"))["x"] or 0,"done":done});timeweek.append({"date":day.strftime("%a"),"minutes":round(secs/60)});completion_week.append({"date":day.strftime("%a"),"percent":round(done/total*100) if total else 0,"done":done,"total":total})
 total_secs=StudySession.objects.filter(ended_at__isnull=False).aggregate(x=Sum("duration_seconds"))["x"] or 0;today_secs=StudySession.objects.filter(started_at__date=today,ended_at__isnull=False).aggregate(x=Sum("duration_seconds"))["x"] or 0
 counts={k:Completion.objects.filter(task__priority=k,completed=True,completed_at__date=today).count() for k in XP};mission=daily_mission(today,p,round(today_secs/60),counts)
 active_days=set(Completion.objects.filter(completed=True).values_list("date",flat=True));streak=0;cursor=today
 while cursor in active_days:streak+=1;cursor-=timedelta(days=1)
 p.longest_streak=max(p.longest_streak,streak);p.save(update_fields=["longest_streak"]);level=level_data(p.lifetime_xp,p.points)
 current_plan=mission_plan(today,level["level"])
 upcoming=[]
 for offset in range(1,8):
  future=today+timedelta(days=offset);plan=mission_plan(future,level["level"])
  upcoming.append({"date":future.isoformat(),"day":future.strftime("%a"),"title":plan["title"],"flavor":plan["flavor"],"studyMinutes":plan["study_minutes"],"easyTarget":plan["easy_target"],"legendaryTarget":plan["legendary_target"],"reward":plan["reward_xp"],"penalty":plan["penalty_xp"]})
 stats=[]
 for t in Task.objects.filter(active=True).order_by("title"):
  history=[]
  for o in range(6,-1,-1):
   day=today-timedelta(days=o);c=Completion.objects.filter(task=t,date=day).first();history.append({"date":day.strftime("%a"),"xp":c.points_awarded if c else 0})
  time_history=[]
  for o in range(6,-1,-1):
   day=today-timedelta(days=o);seconds=StudySession.objects.filter(task=t,started_at__date=day,ended_at__isnull=False).aggregate(x=Sum("duration_seconds"))["x"] or 0;time_history.append({"date":day.strftime("%a"),"minutes":round(seconds/60)})
  task_minutes=sum(x["minutes"] for x in time_history);done=Completion.objects.filter(task=t,completed=True).count();misses=Completion.objects.filter(task=t,completed=False,points_awarded__lt=0).count();stats.append({"id":t.id,"title":t.title,"history":history,"timeHistory":time_history,"minutes":task_minutes,"timePercent":round(task_minutes/(total_secs/60)*100) if total_secs else 0,"done":done,"misses":misses,"focus":misses*2+(1 if done==0 else 0)})
 ranked_tasks=recommendation_for(today);recommendation=ranked_tasks[0] if ranked_tasks else None;active=InventoryItem.objects.filter(active_until__gt=timezone.now(),quantity=0).order_by("active_until").first()
 completed_total=Completion.objects.filter(completed=True).count()
 badges=[{"icon":"⚡","name":"First Strike","unlocked":completed_total>=1,"hint":"Complete your first quest"},{"icon":"🔥","name":"On Fire","unlocked":streak>=3,"hint":"Build a 3-day streak"},{"icon":"🧠","name":"Deep Thinker","unlocked":total_secs>=3600,"hint":"Study for one total hour"},{"icon":"🏆","name":"Quest Closer","unlocked":completed_total>=10,"hint":"Complete 10 quests"},{"icon":"🌟","name":"Rising Star","unlocked":level["level"]>=5,"hint":"Reach level 5"}]
 return JsonResponse({"profile":{**level,"rank":rank_title(level["level"]),"levelIdentity":level_identity(level["level"]),"name":p.name,"tokens":p.tokens,"streak":streak,"bestStreak":p.longest_streak,"dailyGoal":p.daily_focus_goal},"tasks":todo,"summary":{"total":len(todo),"completed":sum(t["completed"] for t in todo),"rate":round(sum(t["completed"] for t in todo)/len(todo)*100) if todo else 0},"week":week,"timeWeek":timeweek,"completionWeek":completion_week,"study":{"todayMinutes":round(today_secs/60),"totalMinutes":round(total_secs/60)},"timer":timer_data(),"boost":{"active":bool(active),"until":active.active_until.isoformat() if active else None},"mission":{"title":current_plan["title"],"flavor":current_plan["flavor"],"studyMinutes":mission.study_minutes,"easyTarget":mission.easy_target,"legendaryTarget":mission.legendary_target,"easyDone":counts["low"],"legendaryDone":counts["legendary"],"reward":mission.reward_xp,"tokens":mission.reward_tokens,"penalty":mission.penalty_xp,"completed":mission.completed},"upcomingMissions":upcoming,"taskStats":stats,"recommendation":recommendation,"recommendedTasks":ranked_tasks[:5],"activity":[{"amount":x.amount,"reason":x.reason,"kind":x.kind,"at":x.created_at.strftime("%b %d, %H:%M")} for x in ActivityLog.objects.order_by("-created_at")[:12]],"badges":badges,"distractions":Distraction.objects.filter(resolved=False).count()})
@csrf_exempt
def tasks(r):
 if r.method=="GET":
  order={"due":"due_date","newest":"-created_at","priority":"priority","title":"title"}.get(r.GET.get("order","due"),"due_date");return JsonResponse({"tasks":[serialize_task(t,timezone.localdate()) for t in Task.objects.filter(active=True).order_by(order)]})
 if r.method=="POST":
  x=body(r);title=x.get("title","").strip()
  if not title:return JsonResponse({"error":"A quest name is required."},status=400)
  try:due=date.fromisoformat(x.get("dueDate",timezone.localdate().isoformat()))
  except (TypeError,ValueError):due=timezone.localdate()
  importance=x.get("importance",50);estimate=x.get("estimatedMinutes",30)
  importance=importance if isinstance(importance,int) else 50;estimate=estimate if isinstance(estimate,int) else 30
  t=Task.objects.create(title=title,description=x.get("description","").strip()[:360],category=x.get("category","").strip()[:80],importance=max(0,min(100,importance)),estimated_minutes=max(5,min(1440,estimate)),priority=x.get("priority") if x.get("priority") in XP else "normal",is_daily=bool(x.get("daily")),due_date=due);return JsonResponse({"task":serialize_task(t,timezone.localdate())},status=201)
 return JsonResponse({"error":"Method not allowed"},status=405)
@csrf_exempt
def task_detail(r,task_id):
 t=Task.objects.filter(pk=task_id,active=True).first()
 if not t:return JsonResponse({"error":"Quest not found"},status=404)
 if r.method=="PATCH":
  x=body(r);t.title=x.get("title",t.title).strip()[:180] or t.title;t.description=x.get("description",t.description).strip()[:360]
  if x.get("priority") in XP:t.priority=x["priority"]
  if "category" in x:t.category=str(x["category"]).strip()[:80]
  if isinstance(x.get("importance"),int):t.importance=max(0,min(100,x["importance"]))
  if isinstance(x.get("estimatedMinutes"),int):t.estimated_minutes=max(5,min(1440,x["estimatedMinutes"]))
  if "daily" in x:t.is_daily=bool(x["daily"])
  if x.get("dueDate"):
   try:t.due_date=date.fromisoformat(x["dueDate"])
   except ValueError:pass
  t.save();return JsonResponse({"task":serialize_task(t,timezone.localdate())})
 if r.method=="DELETE":t.active=False;t.save(update_fields=["active"]);return JsonResponse({"ok":True})
 return JsonResponse({"error":"Method not allowed"},status=405)
@csrf_exempt
def subtasks(r,task_id,subtask_id=None):
 t=Task.objects.filter(pk=task_id,active=True).first()
 if not t:return JsonResponse({"error":"Quest not found"},status=404)
 if subtask_id is None and r.method=="POST":
  title=body(r).get("title","").strip()
  if not title:return JsonResponse({"error":"A sub-task name is required."},status=400)
  SubTask.objects.create(task=t,title=title[:180]);return JsonResponse({"task":serialize_task(t,timezone.localdate())},status=201)
 s=SubTask.objects.filter(pk=subtask_id,task=t).first()
 if not s:return JsonResponse({"error":"Sub-task not found"},status=404)
 if r.method=="PATCH":
  title=body(r).get("title",s.title).strip()[:180];s.title=title or s.title;s.save(update_fields=["title"]);return JsonResponse({"task":serialize_task(t,timezone.localdate())})
 if r.method=="POST":
  share=max(1,XP[t.priority]//max(1,t.subtasks.count()));p=profile()
  if s.completed:add_xp(p,-s.points_awarded,f"Undid sub-task: {s.title}");s.completed=False;s.points_awarded=0;s.completed_at=None
  else:s.completed=True;s.points_awarded=share;s.completed_at=timezone.now();add_xp(p,share,f"Completed sub-task: {s.title}")
  s.save();
  if t.subtasks.exists() and not t.subtasks.filter(completed=False).exists():
   c,_=Completion.objects.get_or_create(task=t,date=timezone.localdate());c.completed=True;c.completed_at=timezone.now();c.points_awarded=0;c.save()
  return JsonResponse({"task":serialize_task(t,timezone.localdate())})
 if r.method=="DELETE":s.delete();return JsonResponse({"task":serialize_task(t,timezone.localdate())})
 return JsonResponse({"error":"Method not allowed"},status=405)
@csrf_exempt
def toggle_task(r,task_id):
 if r.method!="POST":return JsonResponse({"error":"POST only"},status=405)
 t=Task.objects.filter(pk=task_id,active=True).first()
 if not t:return JsonResponse({"error":"Quest not found"},status=404)
 today,p=timezone.localdate(),profile();c,_=Completion.objects.get_or_create(task=t,date=today)
 if not c.completed and c.points_awarded<0:return JsonResponse({"error":"This quest was ignored for today and cannot be completed."},status=400)
 if c.completed:add_xp(p,-c.points_awarded,f"Undid completion: {t.title}");c.completed=False;c.points_awarded=0;c.completed_at=None
 else:
  multi=2 if active_boost("double_xp") else 1;earned=XP[t.priority]*multi;c.completed=True;c.points_awarded=earned;c.completed_at=timezone.now();add_xp(p,earned,f"Completed {t.title}"+(" (Double XP)" if multi==2 else ""))
 c.save();return JsonResponse({"task":serialize_task(t,today),"profile":level_data(p.lifetime_xp,p.points)})
@csrf_exempt
def task_token(r,task_id):
 """Spend one earned mission token on an immediate task choice or a single-day skip."""
 if r.method!="POST":return JsonResponse({"error":"POST only"},status=405)
 t=Task.objects.filter(pk=task_id,active=True).first()
 if not t:return JsonResponse({"error":"Quest not found"},status=404)
 today,p=timezone.localdate(),profile();action=body(r).get("action")
 if p.tokens<1:return JsonResponse({"error":"Complete a mission to earn a token first."},status=400)
 if action=="choose":
  if task_is_complete(t,today):return JsonResponse({"error":"That quest is already complete."},status=400)
  Task.objects.filter(token_selected_on=today).update(token_selected_on=None)
  t.token_selected_on=today;t.save(update_fields=["token_selected_on"])
  add_tokens(p,-1,f"Chose {t.title} as the next quest")
  return JsonResponse({"ok":True,"task":serialize_task(t,today),"tokens":p.tokens})
 if action=="skip":
  if not (t.is_daily or t.due_date==today):return JsonResponse({"error":"Only a quest scheduled for today can be ignored."},status=400)
  c,created=Completion.objects.get_or_create(task=t,date=today)
  if c.completed:return JsonResponse({"error":"That quest is already complete."},status=400)
  if not created or c.points_awarded<0:return JsonResponse({"error":"That quest has already been ignored today."},status=400)
  penalty=max(1,XP[t.priority]//2);c.points_awarded=-penalty;c.save(update_fields=["points_awarded"])
  add_xp(p,-penalty,f"Ignored {t.title} for today")
  add_tokens(p,-1,f"Used a token to ignore {t.title}")
  return JsonResponse({"ok":True,"task":serialize_task(t,today),"tokens":p.tokens,"penalty":penalty})
 return JsonResponse({"error":"Unknown token action."},status=400)
@csrf_exempt
def missions(r):
 if r.method!="GET":return JsonResponse({"error":"GET only"},status=405)
 today,p=timezone.localdate(),profile();level=level_data(p.lifetime_xp,p.points)["level"]
 catalog=[]
 for offset in range(100):
  day=today+timedelta(days=offset);plan=mission_plan(day,level)
  stored=DailyMission.objects.filter(date=day).first()
  catalog.append({"number":day.toordinal()%100+1,"date":day.isoformat(),"title":plan["title"],"flavor":plan["flavor"],"studyMinutes":stored.study_minutes if stored else plan["study_minutes"],"easyTarget":stored.easy_target if stored else plan["easy_target"],"legendaryTarget":stored.legendary_target if stored else plan["legendary_target"],"reward":stored.reward_xp if stored else plan["reward_xp"],"tokens":stored.reward_tokens if stored else plan["reward_tokens"],"penalty":stored.penalty_xp if stored else plan["penalty_xp"],"completed":bool(stored and stored.completed)})
 return JsonResponse({"tokens":p.tokens,"missions":catalog})
@csrf_exempt
def profile_settings(r):
 p=profile()
 if r.method=="GET":return JsonResponse({"name":p.name})
 if r.method=="PATCH":
  x=body(r);p.name=x.get("name",p.name).strip()[:60] or p.name
  if isinstance(x.get("dailyGoal"),int) and 15<=x["dailyGoal"]<=600:p.daily_focus_goal=x["dailyGoal"]
  p.save();return JsonResponse({"name":p.name,"dailyGoal":p.daily_focus_goal})
 return JsonResponse({"error":"Method not allowed"},status=405)
@csrf_exempt
def timer(r):
 if r.method=="GET":return JsonResponse(timer_data())
 action,s=body(r).get("action"),active_timer()
 if action=="start" and not s:
  task=Task.objects.filter(pk=body(r).get("taskId"),active=True).first();StudySession.objects.create(started_at=timezone.now(),task=task);return JsonResponse(timer_data())
 if action=="stop" and s:
  seconds=max(1,int((timezone.now()-s.started_at).total_seconds()));multi=2 if active_boost("double_xp") or active_boost("timer_double") else 1;earned=(seconds//300)*5*multi;s.ended_at=timezone.now();s.duration_seconds=seconds;s.points_awarded=earned;s.reflection=body(r).get("reflection","").strip()[:280];s.save();add_xp(profile(),earned,f"Focus session: {round(seconds/60)} minutes"+(" (Double XP)" if multi==2 else ""));return JsonResponse({"timer":timer_data(),"earned":earned,"duration":seconds})
 return JsonResponse({"error":"Timer is already in that state"},status=400)
@csrf_exempt
def shop(r):
 p=profile()
 if r.method=="GET":
  items=[]
  for x in SHOP:
   owned=InventoryItem.objects.filter(key=x["key"]).first();items.append({**x,"quantity":owned.quantity if owned else 0,"activeUntil":owned.active_until.isoformat() if owned and owned.active_until else None})
  return JsonResponse({"items":items})
 if r.method=="POST":
  x=next((z for z in SHOP if z["key"]==body(r).get("key")),None)
  if not x:return JsonResponse({"error":"Item not found"},status=404)
  if p.points<x["cost"]:return JsonResponse({"error":"Not enough XP"},status=400)
  p.points-=x["cost"];p.save(update_fields=["points","updated_at"]);item,created=InventoryItem.objects.get_or_create(key=x["key"],defaults=x)
  if not created:item.quantity+=1;item.name=x["name"];item.icon=x["icon"];item.description=x["description"];item.cost=x["cost"];item.effect=x["effect"];item.duration_minutes=x["duration_minutes"];item.save()
  log(-x["cost"],f"Bought {x['name']}","purchase");return JsonResponse({"item":x,"points":p.points})
 if r.method=="PATCH":
  item=InventoryItem.objects.filter(key=body(r).get("key"),quantity__gt=0).first()
  if not item:return JsonResponse({"error":"You do not have this item ready to use."},status=400)
  definition=next((x for x in SHOP if x["key"]==item.key),None)
  if definition and not item.effect:item.effect=definition["effect"];item.duration_minutes=definition["duration_minutes"];item.save(update_fields=["effect","duration_minutes"])
  if item.effect=="cosmetic":return JsonResponse({"error":"This is a permanent collectible."},status=400)
  item.quantity-=1;item.active_until=timezone.now()+timedelta(minutes=item.duration_minutes) if item.duration_minutes else None;item.save(update_fields=["quantity","active_until"]);log(0,f"Activated {item.name}","boost");return JsonResponse({"ok":True,"activeUntil":item.active_until.isoformat() if item.active_until else None})
 return JsonResponse({"error":"Method not allowed"},status=405)
@csrf_exempt
def distractions(r):
 if r.method=="GET":return JsonResponse({"items":[{"id":x.id,"text":x.text,"at":x.created_at.strftime("%b %d, %H:%M")} for x in Distraction.objects.filter(resolved=False).order_by("-created_at")]})
 if r.method=="POST":
  text=body(r).get("text","").strip()[:180]
  if not text:return JsonResponse({"error":"Write something first"},status=400)
  x=Distraction.objects.create(text=text);return JsonResponse({"id":x.id,"text":x.text},status=201)
 if r.method=="PATCH":Distraction.objects.filter(pk=body(r).get("id")).update(resolved=True);return JsonResponse({"ok":True})
 return JsonResponse({"error":"Method not allowed"},status=405)
@csrf_exempt
def recall(r):
 today=timezone.localdate()
 if r.method=="GET":
  topics=RecallTopic.objects.filter(active=True).order_by("next_review_on","created_at")
  due=[serialize_recall(t,today) for t in topics.filter(next_review_on__lte=today)]
  upcoming=[serialize_recall(t,today) for t in topics.filter(next_review_on__gt=today)[:12]]
  history=[]
  for offset in range(6,-1,-1):
   day=today-timedelta(days=offset);reviews=RecallReview.objects.filter(reviewed_on=day)
   count=reviews.count();average=round(reviews.aggregate(x=Sum("score"))["x"]/count) if count else 0
   history.append({"date":day.strftime("%a"),"score":average,"reviews":count})
  all_reviews=RecallReview.objects.all();count=all_reviews.count();average=round(all_reviews.aggregate(x=Sum("score"))["x"]/count) if count else 0
  return JsonResponse({"due":due,"upcoming":upcoming,"history":history,"stats":{"topics":topics.count(),"due":len(due),"reviews":count,"average":average}})
 if r.method=="POST":
  x=body(r);title=x.get("title","").strip()
  if not title:return JsonResponse({"error":"Write what you learned first."},status=400)
  topic=RecallTopic.objects.create(title=title[:280],category=x.get("category","").strip()[:80],learned_on=today,next_review_on=today+timedelta(days=1))
  return JsonResponse({"topic":serialize_recall(topic,today)},status=201)
 return JsonResponse({"error":"Method not allowed"},status=405)
@csrf_exempt
def review_recall(r,topic_id):
 if r.method!="POST":return JsonResponse({"error":"POST only"},status=405)
 topic=RecallTopic.objects.filter(pk=topic_id,active=True).first()
 if not topic:return JsonResponse({"error":"Recall topic not found"},status=404)
 score=body(r).get("score")
 if not isinstance(score,int) or not 0<=score<=100:return JsonResponse({"error":"Score must be a whole number from 0 to 100."},status=400)
 today=timezone.localdate();days,label=recall_interval(score);next_day=today+timedelta(days=days)
 RecallReview.objects.create(topic=topic,reviewed_on=today,score=score,next_review_on=next_day)
 topic.last_score=score;topic.review_count+=1;topic.next_review_on=next_day;topic.save(update_fields=["last_score","review_count","next_review_on"])
 return JsonResponse({"topic":serialize_recall(topic,today),"suggestion":f"Great — review this again {label}."})
@csrf_exempt
def study_plan(r):
 today=timezone.localdate();plan,_=DailyStudyPlan.objects.get_or_create(date=today)
 if r.method=="GET":
  seconds=StudySession.objects.filter(started_at__date=today,ended_at__isnull=False).aggregate(x=Sum("duration_seconds"))["x"] or 0
  due=RecallTopic.objects.filter(active=True,next_review_on__lte=today).count()
  quests=Task.objects.filter(active=True).filter(Q(is_daily=True)|Q(due_date=today)).count()
  return JsonResponse({"date":today.isoformat(),"intention":plan.intention,"plannedMinutes":plan.planned_minutes,"energy":plan.energy,"reflection":plan.reflection,"studiedMinutes":round(seconds/60),"dueRecall":due,"todayQuests":quests})
 if r.method=="PATCH":
  x=body(r)
  if "intention" in x:plan.intention=str(x["intention"]).strip()[:220]
  if "reflection" in x:plan.reflection=str(x["reflection"]).strip()[:420]
  if isinstance(x.get("plannedMinutes"),int):plan.planned_minutes=max(15,min(600,x["plannedMinutes"]))
  if isinstance(x.get("energy"),int):plan.energy=max(1,min(5,x["energy"]))
  plan.save();return JsonResponse({"ok":True})
 return JsonResponse({"error":"Method not allowed"},status=405)
def week_start(day):return day-timedelta(days=day.weekday())
@csrf_exempt
def study_tools(r):
 today=timezone.localdate();settings,_=StudySettings.objects.get_or_create(pk=1);wellbeing,_=DailyWellbeing.objects.get_or_create(date=today);reflection,_=WeeklyReflection.objects.get_or_create(week_start=week_start(today))
 if r.method=="GET":
  start=week_start(today);seconds=StudySession.objects.filter(started_at__date__gte=start,ended_at__isnull=False).aggregate(x=Sum("duration_seconds"))["x"] or 0
  days_left=(settings.exam_date-today).days if settings.exam_date else None
  return JsonResponse({"settings":{"examName":settings.exam_name,"examDate":settings.exam_date.isoformat() if settings.exam_date else "","weeklyGoal":settings.weekly_goal_minutes,"daysLeft":days_left},"weekMinutes":round(seconds/60),"wellbeing":{"sleepHours":float(wellbeing.sleep_hours),"waterCups":wellbeing.water_cups,"movementMinutes":wellbeing.movement_minutes,"mood":wellbeing.mood},"reflection":{"win":reflection.win,"blocker":reflection.blocker,"nextFocus":reflection.next_focus},"resources":[{"id":x.id,"title":x.title,"url":x.url,"category":x.category} for x in StudyResource.objects.order_by("-created_at")],"distractions":[{"id":x.id,"text":x.text,"at":x.created_at.strftime("%b %d, %H:%M")} for x in Distraction.objects.filter(resolved=False).order_by("-created_at")]})
 x=body(r)
 if r.method=="PATCH":
  section=x.get("section")
  if section=="settings":
   settings.exam_name=str(x.get("examName",settings.exam_name)).strip()[:100]
   try:settings.exam_date=date.fromisoformat(x["examDate"]) if x.get("examDate") else None
   except (TypeError,ValueError):pass
   if isinstance(x.get("weeklyGoal"),int):settings.weekly_goal_minutes=max(30,min(3000,x["weeklyGoal"]))
   settings.save()
  elif section=="wellbeing":
   for key,field,low,high in [("waterCups","water_cups",0,30),("movementMinutes","movement_minutes",0,600),("mood","mood",1,5)]:
    if isinstance(x.get(key),int):setattr(wellbeing,field,max(low,min(high,x[key])))
   if isinstance(x.get("sleepHours"),(int,float)):wellbeing.sleep_hours=max(0,min(16,x["sleepHours"]))
   wellbeing.save()
  elif section=="reflection":
   reflection.win=str(x.get("win",reflection.win)).strip()[:320];reflection.blocker=str(x.get("blocker",reflection.blocker)).strip()[:320];reflection.next_focus=str(x.get("nextFocus",reflection.next_focus)).strip()[:320];reflection.save()
  elif section=="distraction":Distraction.objects.filter(pk=x.get("id")).update(resolved=True)
  else:return JsonResponse({"error":"Unknown tool section"},status=400)
  return JsonResponse({"ok":True})
 if r.method=="POST":
  title=str(x.get("title","")).strip()
  if not title:return JsonResponse({"error":"A resource title is required."},status=400)
  resource=StudyResource.objects.create(title=title[:160],url=str(x.get("url","")).strip()[:200],category=str(x.get("category","")).strip()[:80]);return JsonResponse({"resource":{"id":resource.id,"title":resource.title}},status=201)
 return JsonResponse({"error":"Method not allowed"},status=405)
@csrf_exempt
def resource_detail(r,resource_id):
 if r.method!="DELETE":return JsonResponse({"error":"DELETE only"},status=405)
 StudyResource.objects.filter(pk=resource_id).delete();return JsonResponse({"ok":True})
