from django.db import models


class QuestionManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related('author').prefetch_related('question_tags__tag', 'answers')
