from rapidsms.tests.scripted import TestScript
from rapidsms.message import Message as SmsMessage
from app import App
from models import *
import reporters.app as reporters_app
from reporters.models import Reporter
import datetime
from django.test.client import Client

from django.contrib.auth.models import User

class TestApp (TestScript):
    fixtures = ['user_brian']
    apps = (reporters_app.App, App)

    def testBasic(self):
        script = """
            sample_1 > here is a message
            sample_1 > here is another message!
            sample_2 > here is a third message... 
        """
        self.runScript(script)
        connection = PersistantConnection.objects.all()[0]
        be = self.router.get_backend(connection.backend.slug)
        be.message(connection.identity, "This is an outgoing message!").send()
        self.assertEqual(4, Message.objects.count())
        self.assertEqual(3, Message.objects.filter(is_incoming=True).count())
        self.assertEqual(1, Message.objects.filter(is_incoming=False).count())
        
    def testIndexShouldDisplayAMessage(self):
        self.client.login(username='brian', password='test')
        self.runScript("sample_1 > here is a message")
        response = self.client.get('/logger')
        self.assertEqual(200, response.status_code)
        self.assertContains(response, "here is a message")
        
    def testIndexDoesSearches(self):
        self.client.login(username='brian', password='test')
        self.runScript("""
            sample_1 > this is the expected message
            sample_1 > this is the unexpected message
        """)
        response = self.client.get('/logger', {'search_string': 'the expected'})
        self.assertEqual(200, response.status_code)
        self.assertContains(response, "the expected message")
        self.assertNotContains(response, "the unexpected message")
        
        