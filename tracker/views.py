import json
from datetime import timedelta, date
from django.db.models import Sum
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from .models import Profile, Task, Completion, StudySession, InventoryItem, Distraction, DailyMission

XP={"low":10,"normal":25,"high":50,"legendary":100}
SHOP=[
{"key":"focus_orb","name":"Focus Orb","icon":"🔮","description":"A reminder to stay present.","cost":120},
{"key":"study_cat","name":"Study Cat","icon":"🐈","description":"Your quiet desk companion.","cost":260},
{"key":"forest_theme","name":"Forest Theme","icon":"🌲","description":"A calm, green study realm.","cost":320},
{"key":"coffee_boost","name":"Coffee Boost","icon":"☕","description":"A badge for early focus.","cost":380},
{"key":"golden_crown","name":"Golden Crown","icon":"👑","description":"For serious consistency.","cost":500},
{"key":"dragon_egg","name":"Dragon Egg","icon":"🥚","description":"It grows with your discipline.","cost":650},
{"key":"nebula_theme","name":"Nebula Theme","icon":"🌌","description":"A cosmic dashboard reward.","cost":800},
{"key":"timekeeper","name":"Timekeeper","icon":"⌛","description":"Honors 10 hours of deep work.","cost":950},
{"key":"phoenix","name":"Phoenix Badge","icon":"🔥","description":"Rise after every missed day.","cost":1200},
{"key":"master_sword","name":"Master Focus","icon":"⚔️","description":"Proof of legendary commitment.","cost":1600},
{"key":"crystal_castle","name":"Crystal Castle","icon":"🏰","description":"Your ultimate study sanctuary.","cost":2200},
{"key":"celestial_hero","name":"Celestial Hero","icon":"🦸","description":"The final rank of persistence.","cost":3000}]
def body(r):
    try:return json.loads(r.body or "{}")
    except json.JSONDecodeError:return {}
def profile():return Profile.objects.get_or_create(pk=1)[0]
def level_data(total_xp, wallet=None):
    """Level costs grow: 200 XP for level 2, then +150 XP for every level."""
    remaining=max(0,total_xp);level=1;needed=200
    while remaining>=needed:
        remaining-=needed;level+=1;needed=200+(level-1)*150
    return {"level":level,"currentXp":round(remaining/needed*250),"nextXp":250,"requiredXp":needed,"points":wallet if wallet is not None else total_xp,"lifetimeXp":total_xp}
def rank_title(level):
    ranks=[(1,"Curious Recruit"),(3,"Habit Scout"),(6,"Focus Ranger"),(10,"Quest Knight"),(15,"Study Mage"),(25,"Discipline Legend")]
    return next(title for minimum,title in reversed(ranks) if level>=minimum)
def serialize_task(t,d):return {"id":t.id,"title":t.title,"description":t.description,"priority":t.priority,"daily":t.is_daily,"dueDate":t.due_date.isoformat(),"completed":Completion.objects.filter(task=t,date=d,completed=True).exists(),"xp":XP[t.priority]}
def active_timer():return StudySession.objects.filter(ended_at__isnull=True).order_by("-started_at").first()
def timer_data():
    s=active_timer();return {"running":bool(s),"startedAt":s.started_at.isoformat() if s else None}
def apply_penalties():
    today=timezone.localdate();p=profile();changed=False
    for t in Task.objects.filter(active=True):
        start=max(t.created_at.date(),t.due_date)
        days=([t.due_date] if not t.is_daily and t.due_date<today else [start+timedelta(days=i) for i in range((today-start).days)] if t.is_daily and start<today else [])
        for day in days:
            c,made=Completion.objects.get_or_create(task=t,date=day)
            if made:c.points_awarded=-(XP[t.priority]//2);c.save(update_fields=["points_awarded"]);p.points+=c.points_awarded;p.lifetime_xp+=c.points_awarded;changed=True
    if changed:p.save()
def daily_mission(today, p, total_study_minutes, completion_counts):
    """Mission difficulty rises each 3 levels; missed prior missions have a clear penalty."""
    for mission in DailyMission.objects.filter(date__lt=today, completed=False, punished=False):
        mission.punished=True;mission.save(update_fields=["punished"]);p.points-=mission.penalty_xp;p.lifetime_xp-=mission.penalty_xp
    level=level_data(p.lifetime_xp,p.points)["level"];tier=(level-1)//3
    mission,_=DailyMission.objects.get_or_create(date=today,defaults={"study_minutes":min(180,60+tier*15),"easy_target":1+tier//3,"legendary_target":1 if tier>=1 else 0,"reward_xp":80+tier*20,"penalty_xp":60+tier*25})
    met=total_study_minutes>=mission.study_minutes and completion_counts["low"]>=mission.easy_target and completion_counts["legendary"]>=mission.legendary_target
    if met and not mission.completed:
        mission.completed=True;mission.save(update_fields=["completed"]);p.points+=mission.reward_xp;p.lifetime_xp+=mission.reward_xp
    return mission

@csrf_exempt
def dashboard(r):
    if r.method!="GET":return JsonResponse({"error":"GET only"},status=405)
    apply_penalties();today=timezone.localdate();p=profile();todo=[serialize_task(t,today) for t in Task.objects.filter(active=True) if t.is_daily or t.due_date==today];done=sum(t["completed"] for t in todo)
    week=[];timeweek=[]
    for o in range(6,-1,-1):
        d=today-timedelta(days=o);c=Completion.objects.filter(date=d);secs=StudySession.objects.filter(started_at__date=d,ended_at__isnull=False).aggregate(x=Sum("duration_seconds"))["x"] or 0
        week.append({"date":d.strftime("%a"),"xp":c.aggregate(x=Sum("points_awarded"))["x"] or 0,"done":c.filter(completed=True).count()});timeweek.append({"date":d.strftime("%a"),"minutes":round(secs/60)})
    priorities=[]
    for key in XP:
        qs=Task.objects.filter(active=True,priority=key);priorities.append({"name":key,"total":qs.count(),"done":Completion.objects.filter(task__in=qs,completed=True).count()})
    completed=Completion.objects.filter(completed=True).count();total_tasks=Task.objects.filter(active=True).count();missed=Completion.objects.filter(completed=False,points_awarded__lt=0).count()
    active_days=set(Completion.objects.filter(completed=True).values_list("date",flat=True));streak=0;cursor=today
    while cursor in active_days:streak+=1;cursor-=timedelta(days=1)
    p.longest_streak=max(p.longest_streak,streak);p.save(update_fields=["longest_streak"])
    total_secs=StudySession.objects.filter(ended_at__isnull=False).aggregate(x=Sum("duration_seconds"))["x"] or 0;today_secs=StudySession.objects.filter(started_at__date=today,ended_at__isnull=False).aggregate(x=Sum("duration_seconds"))["x"] or 0
    counts={key:Completion.objects.filter(task__priority=key,completed=True,completed_at__date=today).count() for key in XP}
    mission=daily_mission(today,p,round(today_secs/60),counts);p.save()
    level=level_data(p.lifetime_xp,p.points)
    badges=[
        {"icon":"⚡","name":"First Strike","unlocked":completed>=1,"hint":"Complete your first quest"},
        {"icon":"🔥","name":"On Fire","unlocked":streak>=3,"hint":"Build a 3-day streak"},
        {"icon":"🧠","name":"Deep Thinker","unlocked":total_secs>=3600,"hint":"Study for one total hour"},
        {"icon":"🏆","name":"Quest Closer","unlocked":completed>=10,"hint":"Complete 10 quests"},
        {"icon":"🌟","name":"Rising Star","unlocked":level["level"]>=5,"hint":"Reach level 5"},
    ]
    return JsonResponse({"profile":{**level,"rank":rank_title(level["level"]),"name":p.name,"streak":streak,"bestStreak":p.longest_streak,"dailyGoal":p.daily_focus_goal},"tasks":todo,"summary":{"total":len(todo),"completed":done,"rate":round(done/len(todo)*100) if todo else 0},"week":week,"timeWeek":timeweek,"priority":priorities,"breakdown":{"completed":completed,"pending":max(0,total_tasks-completed),"missed":missed},"study":{"todayMinutes":round(today_secs/60),"totalMinutes":round(total_secs/60)},"timer":timer_data(),"inventory":[x.key for x in InventoryItem.objects.all()],"badges":badges,"distractions":Distraction.objects.filter(resolved=False).count(),"mission":{"studyMinutes":mission.study_minutes,"easyTarget":mission.easy_target,"legendaryTarget":mission.legendary_target,"easyDone":counts["low"],"legendaryDone":counts["legendary"],"reward":mission.reward_xp,"penalty":mission.penalty_xp,"completed":mission.completed}})

@csrf_exempt
def tasks(r):
    if r.method=="GET":return JsonResponse({"tasks":[serialize_task(t,timezone.localdate()) for t in Task.objects.filter(active=True).order_by("-created_at")]})
    if r.method=="POST":
        x=body(r);title=x.get("title","").strip()
        if not title:return JsonResponse({"error":"A quest name is required."},status=400)
        priority=x.get("priority","normal") if x.get("priority") in XP else "normal";due=timezone.localdate() if x.get("daily") else x.get("dueDate",timezone.localdate().isoformat())
        try:due=date.fromisoformat(due) if isinstance(due,str) else due
        except ValueError:due=timezone.localdate()
        t=Task.objects.create(title=title,description=x.get("description","").strip(),priority=priority,is_daily=bool(x.get("daily")),due_date=due);return JsonResponse({"task":serialize_task(t,timezone.localdate())},status=201)
    return JsonResponse({"error":"Method not allowed"},status=405)

@csrf_exempt
def toggle_task(r,task_id):
    if r.method!="POST":return JsonResponse({"error":"POST only"},status=405)
    try:t=Task.objects.get(pk=task_id,active=True)
    except Task.DoesNotExist:return JsonResponse({"error":"Quest not found"},status=404)
    today=timezone.localdate();c,_=Completion.objects.get_or_create(task=t,date=today);p=profile()
    if c.completed:p.points-=c.points_awarded;p.lifetime_xp-=c.points_awarded;c.completed=False;c.points_awarded=0;c.completed_at=None
    else:c.completed=True;c.points_awarded=XP[t.priority];c.completed_at=timezone.now();p.points+=c.points_awarded;p.lifetime_xp+=c.points_awarded
    c.save();p.save();return JsonResponse({"task":serialize_task(t,today),"profile":level_data(p.lifetime_xp,p.points)})
@csrf_exempt
def task_detail(r,task_id):
    if r.method!="DELETE":return JsonResponse({"error":"DELETE only"},status=405)
    Task.objects.filter(pk=task_id).update(active=False);return JsonResponse({"ok":True})
@csrf_exempt
def profile_settings(r):
    p=profile()
    if r.method=="GET":return JsonResponse({"name":p.name})
    if r.method=="PATCH":
        name=body(r).get("name","").strip()[:60]
        if name:p.name=name
        goal=body(r).get("dailyGoal")
        if isinstance(goal,int) and 15<=goal<=600:p.daily_focus_goal=goal
        p.save()
        return JsonResponse({"name":p.name,"dailyGoal":p.daily_focus_goal})
    return JsonResponse({"error":"Method not allowed"},status=405)
@csrf_exempt
def timer(r):
    if r.method=="GET":return JsonResponse(timer_data())
    action=body(r).get("action");s=active_timer()
    if action=="start" and not s:StudySession.objects.create(started_at=timezone.now());return JsonResponse(timer_data())
    if action=="stop" and s:
        seconds=max(1,int((timezone.now()-s.started_at).total_seconds()));earned=(seconds//300)*5;s.ended_at=timezone.now();s.duration_seconds=seconds;s.points_awarded=earned;s.reflection=body(r).get("reflection","").strip()[:280];s.save();p=profile();p.points+=earned;p.lifetime_xp+=earned;p.save();return JsonResponse({"timer":timer_data(),"earned":earned,"duration":seconds})
    return JsonResponse({"error":"Timer is already in that state"},status=400)
@csrf_exempt
def shop(r):
    p=profile()
    if r.method=="GET":return JsonResponse({"items":[{**x,"owned":InventoryItem.objects.filter(key=x["key"]).exists()} for x in SHOP]})
    if r.method=="POST":
        item=next((x for x in SHOP if x["key"]==body(r).get("key")),None)
        if not item:return JsonResponse({"error":"Item not found"},status=404)
        if InventoryItem.objects.filter(key=item["key"]).exists():return JsonResponse({"error":"Already owned"},status=400)
        if p.points<item["cost"]:return JsonResponse({"error":"Not enough XP"},status=400)
        p.points-=item["cost"];p.save();InventoryItem.objects.create(**item);return JsonResponse({"item":item,"points":p.points})
    return JsonResponse({"error":"Method not allowed"},status=405)
@csrf_exempt
def distractions(r):
    if r.method=="GET":return JsonResponse({"items":[{"id":x.id,"text":x.text} for x in Distraction.objects.filter(resolved=False).order_by("-created_at")[:8]]})
    if r.method=="POST":
        text=body(r).get("text","").strip()[:180]
        if not text:return JsonResponse({"error":"Write something first"},status=400)
        item=Distraction.objects.create(text=text);return JsonResponse({"id":item.id,"text":item.text},status=201)
    if r.method=="PATCH":
        Distraction.objects.filter(pk=body(r).get("id")).update(resolved=True);return JsonResponse({"ok":True})
    return JsonResponse({"error":"Method not allowed"},status=405)
