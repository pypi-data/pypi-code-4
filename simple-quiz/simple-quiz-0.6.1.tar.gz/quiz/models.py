from django.db import models
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse

from datetime import datetime


class Quiz(models.Model):
    title = models.CharField(max_length=1024)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'Quizzes'

    def __unicode__(self):
        return self.title
    def get_absolute_url(self):
        return reverse('quiz-sit', kwargs={'quiz_id': self.id})
    def points(self):
        return self.question_set.annotate(
            points=models.Max('answer__points') # Highest point value question
        ).aggregate(
            total_points=models.Sum('points') # Sum of best answers
        )['total_points']

class Question(models.Model):
    quiz = models.ForeignKey(Quiz)
    text = models.TextField()
    group = models.CharField(max_length=128)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ('quiz', 'group', 'order',)
    def __unicode__(self):
        return self.text
    @property
    def points(self):
        '''Return the most points this question can yield.'''
        return self.answer_set.aggregate(points=models.Max('points'))['points']
    def best_answer(self):
        '''Return the highest scoring answer.'''
        return self.answer_set.order_by('-points')[0]

class Answer(models.Model):
    question = models.ForeignKey(Question)
    text = models.TextField()
    order = models.PositiveIntegerField(default=0)
    points = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ('question', 'order',)
    def __unicode__(self):
        return self.text

# Now, record peoples attempts.
class Sitting(models.Model):
    student = models.ForeignKey('auth.User')
    quiz = models.ForeignKey(Quiz)
    date_sat = models.DateTimeField(default=datetime.now)

    class Meta:
        ordering = ('-date_sat',)

    @models.permalink
    def get_absolute_url(self):
        return 'sitting-detail', (), {'sitting_id': self.pk}

    def score(self):
        return self.response_set.aggregate(
            score=models.Sum('choice__points')
        )['score']

class Response(models.Model):
    sitting = models.ForeignKey(Sitting)
    question = models.ForeignKey(Question)
    choice = models.ForeignKey(Answer)

    class Meta:
        unique_together = (
            ('sitting', 'question',),
        )
        ordering = ('question__group', 'question__order',)
    # We should verify the question and choice are valid
    def clean(self):
        if self.choice.question != self.question:
            raise ValidationError, 'Choice must be for the same Question!'

    def is_best(self):
        return self.choice.points == self.question.points
