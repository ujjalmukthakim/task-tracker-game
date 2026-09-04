import json
from datetime import timedelta
from django.test import TestCase
from django.utils import timezone
from .models import Profile, Task


class QuestApiTests(TestCase):
    def test_create_complete_and_dashboard(self):
        created = self.client.post('/api/tasks/', data=json.dumps({
            'title': 'Ship the first quest', 'priority': 'high', 'daily': True,
        }), content_type='application/json')
        self.assertEqual(created.status_code, 201)
        task_id = created.json()['task']['id']
        complete = self.client.post(f'/api/tasks/{task_id}/toggle/')
        self.assertEqual(complete.status_code, 200)
        self.assertTrue(complete.json()['task']['completed'])
        dashboard = self.client.get('/api/dashboard/').json()
        self.assertEqual(dashboard['summary']['completed'], 1)
        self.assertEqual(dashboard['profile']['points'], 50)

    def test_one_time_task_is_shown_today(self):
        Task.objects.create(title='Today only', priority='normal', due_date=timezone.localdate())
        dashboard = self.client.get('/api/dashboard/').json()
        self.assertEqual(dashboard['tasks'][0]['title'], 'Today only')
        self.assertEqual(dashboard['completionWeek'][-1]['percent'], 0)

    def test_recommendation_uses_importance_and_moves_after_completion(self):
        lower = Task.objects.create(title='Later task', importance=60, due_date=timezone.localdate())
        higher = Task.objects.create(title='Critical task', importance=95, due_date=timezone.localdate() + timedelta(days=3))
        dashboard = self.client.get('/api/dashboard/').json()
        self.assertEqual(dashboard['recommendation']['id'], higher.id)
        self.assertEqual(dashboard['recommendedTasks'][0]['importance'], 95)
        self.client.post(f'/api/tasks/{higher.id}/toggle/')
        dashboard = self.client.get('/api/dashboard/').json()
        self.assertEqual(dashboard['recommendation']['id'], lower.id)

    def test_recall_topic_is_due_tomorrow_and_score_sets_next_interval(self):
        created = self.client.post('/api/recall/', data=json.dumps({
            'title': 'The phases of mitosis', 'category': 'Biology',
        }), content_type='application/json')
        self.assertEqual(created.status_code, 201)
        topic_id = created.json()['topic']['id']
        response = self.client.post(f'/api/recall/{topic_id}/review/', data=json.dumps({'score': 72}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['topic']['nextReviewOn'], (timezone.localdate() + timedelta(days=7)).isoformat())

    def test_daily_study_plan_can_be_saved(self):
        saved = self.client.patch('/api/study-plan/', data=json.dumps({
            'intention': 'Finish algebra practice', 'plannedMinutes': 90, 'energy': 4,
            'reflection': 'Start with the difficult questions.',
        }), content_type='application/json')
        self.assertEqual(saved.status_code, 200)
        plan = self.client.get('/api/study-plan/').json()
        self.assertEqual(plan['intention'], 'Finish algebra practice')
        self.assertEqual(plan['plannedMinutes'], 90)

    def test_token_can_choose_or_ignore_a_todays_quest(self):
        profile = Profile.objects.create(pk=1, tokens=2)
        task = Task.objects.create(title='Optional today', priority='high', due_date=timezone.localdate())
        chosen = self.client.post(f'/api/tasks/{task.id}/token/', data=json.dumps({'action': 'choose'}), content_type='application/json')
        self.assertEqual(chosen.status_code, 200)
        self.assertTrue(chosen.json()['task']['tokenSelected'])
        skipped = self.client.post(f'/api/tasks/{task.id}/token/', data=json.dumps({'action': 'skip'}), content_type='application/json')
        self.assertEqual(skipped.status_code, 200)
        self.assertTrue(skipped.json()['task']['skipped'])
        profile.refresh_from_db()
        self.assertEqual(profile.tokens, 0)

    def test_mission_catalog_has_one_hundred_token_rewards(self):
        response = self.client.get('/api/missions/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['missions']), 100)
        self.assertGreaterEqual(response.json()['missions'][0]['tokens'], 1)
