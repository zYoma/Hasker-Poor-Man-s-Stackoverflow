import logging
from django.db import models
from django.utils.translation import gettext_lazy as _


logger = logging.getLogger('django')


class Rating:
    def change_rating(self, is_like):
        # Изменяем рейтинг в соответствии с оценкой
        self.rating = self.rating + 1 if is_like else self.rating - 1
        self.save(update_fields=['rating'])

    def rollback_rating(self, is_like):
        # Снимаем предыдущую оценку пользователя
        self.rating = self.rating - 1 if is_like else self.rating + 1
        self.save(update_fields=['rating'])


class QuestionManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related('author').prefetch_related('question_tags__tag', 'answers')


class Question(Rating, models.Model):
    title = models.CharField(max_length=200, verbose_name=_("Заголовок"))
    text = models.TextField(verbose_name=_("Содержание"))
    author = models.ForeignKey("users.Profile", on_delete=models.CASCADE,
                               related_name="questions", verbose_name=_("Автор"))
    created_date = models.DateTimeField(verbose_name=_("Дата создания"), auto_now_add=True)
    rating = models.IntegerField(default=0, verbose_name=_("Рейтинг"))

    objects = models.Manager()
    objects_with_join = QuestionManager()

    class Meta:
        ordering = ["-created_date", "-rating"]
        verbose_name = 'Вопрос'
        verbose_name_plural = "Вопросы"

    def create_tags(self, tags):
        # Собираем список тегов, чистим от дублей
        tag_list = list(set(tags.split(',')))
        for tag in tag_list:
            tag = tag.strip()
            # Если тега нет, создаем, иначе получаем.
            new_tag, _ = Tag.objects.get_or_create(name=tag, defaults={'name': tag})
            # Создаем связь с вопросом
            QuestionTag.objects.create(question=self, tag=new_tag)


class Tag(models.Model):
    name = models.CharField(max_length=10, unique=True, verbose_name=_("Название тега"))

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = "Теги"


# Вместо использования ManyToManyField, создаю табличку явно.
class QuestionTag(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE,
                                 related_name="question_tags", verbose_name=_("Вопрос"))
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE,
                            related_name="question_tags", verbose_name=_("Тег"))


class Answer(Rating, models.Model):
    text = models.TextField(verbose_name=_("Содержание"))
    author = models.ForeignKey("users.Profile", on_delete=models.CASCADE,
                               related_name="answers", verbose_name=_("Автор"))
    created_date = models.DateTimeField(verbose_name=_("Дата"), auto_now_add=True)
    is_correct_answer = models.BooleanField(verbose_name=_("Правильный ответ"), default=False)
    rating = models.IntegerField(default=0, verbose_name=_("Рейтинг"))
    question = models.ForeignKey(Question, on_delete=models.CASCADE,
                                 related_name="answers", verbose_name=_("Вопрос"))

    class Meta:
        verbose_name = 'Ответ'
        verbose_name_plural = "Ответы"

    def set_correct_answer(self):
        question_answers = Answer.objects.filter(question=self.question)
        for answer in question_answers:
            answer.is_correct_answer = answer.id == self.id
            answer.save(update_fields=['is_correct_answer'])


class UserAnswerRating(models.Model):
    user = models.ForeignKey("users.Profile", on_delete=models.CASCADE,
                             related_name="answer_ratings", verbose_name=_("Пользователь"))
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE,
                               related_name="answer_ratings", verbose_name=_("Ответ"))
    is_like = models.BooleanField(verbose_name=_("Лайк/Дизлайк"))

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "answer"], name="unique_user_answer_rating")
        ]


class UserQuestionRating(models.Model):
    user = models.ForeignKey("users.Profile", on_delete=models.CASCADE,
                             related_name="question_ratings", verbose_name=_("Пользователь"))
    question = models.ForeignKey(Question, on_delete=models.CASCADE,
                                 related_name="question_ratings", verbose_name=_("Вопрос"))
    is_like = models.BooleanField(verbose_name=_("Лайк/Дизлайк"))

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "question"], name="unique_user_question_rating")
        ]
