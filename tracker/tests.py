import json
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
