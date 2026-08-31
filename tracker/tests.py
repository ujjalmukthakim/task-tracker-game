import json
from datetime import timedelta
from django.test import TestCase
from django.utils import timezone
from .models import Task


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
