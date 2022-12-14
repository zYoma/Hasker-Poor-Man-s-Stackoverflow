from django.urls import path

from .views import AnswerRating, Answers, Ask, Index, QuestionRating, Search, SetCorrectAnswer


app_name = 'hasker'


urlpatterns = [
    path('', Index.as_view(), name='index_url'),
    path('ask/', Ask.as_view(), name='ask_url'),
    path('tag/', Search.as_view(), name='tag_url'),
    path('<int:id>/', Answers.as_view(), name='answer_url'),
    path('set-correct/<int:id>/', SetCorrectAnswer.as_view(), name='set_correct_url'),
    path('answer-rating/<int:id>/', AnswerRating.as_view(), name='answer_rating_url'),
    path('question-rating/<int:id>/', QuestionRating.as_view(), name='question_rating_url'),
]
