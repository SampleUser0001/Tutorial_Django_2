import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import *

# Create your tests here.

class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        """未来日は「最近」じゃない"""
        time = timezone.now() +  datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)
    
    def test_was_published_recently_with_old_question(self):
        """ 「最近」のテスト。1秒超過 """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)
    
    def test_was_published_recently_with_recent_question(self):
        """ 「最近」のテスト。1秒前。"""
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)
        
def create_question(question_text, days):
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)

INDEX = 'polls:index'
QUESTION_LIST_KEY = 'latest_question_list'
NOT_HAVE_QUESTION_MESSAGE = 'No polls are available.'

class QuestionIndexViewTests(TestCase):
    
    def test_no_questions(self):
        """質問がない。何も出ないが、エラーではない。"""
        response = self.client.get(reverse(INDEX))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context[QUESTION_LIST_KEY], [])

    def test_post_question(self):
        """質問1件。公開日が過去日=公開済み。"""
        question = create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse(INDEX))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context[QUESTION_LIST_KEY],
            [question]
        )

    def test_future_question(self):
        """質問1件。公開日が未来日=未公開。"""
        question = create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse(INDEX))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, NOT_HAVE_QUESTION_MESSAGE)
        self.assertQuerysetEqual(response.context[QUESTION_LIST_KEY], [])
        
    def test_future_question_and_past_question(self):
        """質問2件。公開日は未来日と過去日。過去日の質問のみが出力される。"""
        past_question = create_question(question_text="Past question.", days=-30)
        future_question = create_question(question_text="Future question.", days=30)

        response = self.client.get(reverse(INDEX))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context[QUESTION_LIST_KEY],
            [past_question]
        )
    
    def test_two_past_question(self):
        """質問2件。公開日は両方とも過去日。2件とも出力される。"""
        question1 = create_question(question_text="Past question 1.", days=-30)
        question2 = create_question(question_text="Past question 2.", days=-5)

        response = self.client.get(reverse(INDEX))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context[QUESTION_LIST_KEY],
            [question2, question1]
        )

DETAIL = 'polls:detail'
class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        """未来日の質問は出力されない。"""
        future_question = create_question(question_text='Future question.', days=5)
        url = reverse(DETAIL, args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """過去日の質問は出力される。"""
        past_question = create_question(question_text='Past question.', days=-5)
        url = reverse(DETAIL, args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)