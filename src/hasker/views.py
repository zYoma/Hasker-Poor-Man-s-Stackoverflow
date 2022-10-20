from typing import Optional, Type, Union

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.utils.decorators import method_decorator
from django.views.generic import View

from config import settings

from .forms import AskQuestionForm
from .models import Answer, Question, UserAnswerRating, UserQuestionRating
from .utils import get_paginator


class Index(View):
    def get(self, request):
        questions = Question.objects_with_join.all()
        is_paginator, prev_url, next_url, parameters, last_page, page = get_paginator(
            request,
            questions,
            settings.QUESTIONS_PER_PAGE
        )
        return render(request, 'hasker/index.html', context={
            'questions': page,
            'is_paginator': is_paginator,
            'prev_url': prev_url,
            'next_url': next_url,
            'parameters': parameters,
            'page_end': last_page,

        })


class Ask(LoginRequiredMixin, View):
    login_url = '/user/login/'

    def get(self, request):
        ask_form = AskQuestionForm()
        return render(request, 'hasker/ask.html', {'ask_form': ask_form})

    def post(self, request):
        ask_form = AskQuestionForm(request.POST)
        if ask_form.is_valid():
            question = ask_form.save(commit=False)
            question.author = request.user
            question_tags = ask_form.cleaned_data['question_tags']
            ask_form.save()
            question.create_tags(question_tags)
            return redirect('index_url')

        return render(request, 'hasker/ask.html', {'ask_form': ask_form})


class Search(View):
    def get(self, request):
        q = request.GET.get('q', '')
        if 'tag:' in q:
            tag = q.split(':')[1].strip()
            questions = Question.objects_with_join.filter(question_tags__tag__name=tag)
        else:
            questions = Question.objects_with_join.filter(Q(title__icontains=q) | Q(text__icontains=q))

        questions = questions.order_by('-rating', '-created_date')
        is_paginator, prev_url, next_url, parameters, last_page, page = get_paginator(
            request,
            questions,
            settings.QUESTIONS_PER_PAGE
        )
        return render(request, 'hasker/search.html', context={
            'questions': page,
            'is_paginator': is_paginator,
            'prev_url': prev_url,
            'next_url': next_url,
            'parameters': parameters,
            'page_end': last_page,
        })


class Answers(View):

    def get(self, request, id):
        question = get_object_or_404(Question.objects_with_join.prefetch_related('answers'), id=id)
        answers = question.answers.select_related('author').all().order_by('-rating', '-created_date')

        is_paginator, prev_url, next_url, parameters, last_page, page = get_paginator(
            request,
            answers,
            settings.ANSWERS_PER_PAGE
        )
        return render(request, 'hasker/answer.html', context={
            'answers': page,
            'is_paginator': is_paginator,
            'prev_url': prev_url,
            'next_url': next_url,
            'parameters': parameters,
            'page_end': last_page,
            'question': question,
        })

    @method_decorator(login_required, name='dispatch')
    def post(self, request, id):
        question = get_object_or_404(Question, id=id)
        if answer := request.POST.get('answer'):
            Answer.objects.create(text=answer, question=question, author=request.user)
        return redirect(reverse('answer_url', kwargs={'id': id}))


class SetCorrectAnswer(LoginRequiredMixin, View):
    login_url = '/user/login/'

    def post(self, request, id):
        answer = get_object_or_404(Answer.objects.select_related('question__author'), id=id)
        if request.user == answer.question.author:
            answer.set_correct_answer()

        return redirect(reverse('answer_url', kwargs={'id': answer.question.id}))


class RatingMixin:
    object_model: Optional[Union[Type[Answer], Type[Question]]] = None
    rating_model: Optional[Union[Type[UserQuestionRating], Type[UserAnswerRating]]] = None
    field_name: Optional[str] = None

    def post(self, request, id):
        obj = get_object_or_404(self.object_model, id=id)
        user = request.user
        like = request.POST.get('like')
        likes = {'poz': True, 'neg': False}
        like = likes[like]

        data_for_get = {self.field_name: obj, 'user': user}
        rating, created = self.rating_model.objects.get_or_create(
            **data_for_get,
            defaults={'is_like': like, **data_for_get},
        )
        if created:
            obj.change_rating(rating.is_like)
        # При изменении оценки
        elif rating.is_like != like:
            # Снимаем предыдущую оценку пользователя
            obj.rollback_rating(rating.is_like)
            # сохраняем новую оценку
            rating.is_like = like
            rating.save()
            obj.change_rating(rating.is_like)

        redirect_obj_id = obj.question.id if self.object_model is Answer else obj.id
        return redirect(reverse('answer_url', kwargs={'id': redirect_obj_id}))


class AnswerRating(RatingMixin, LoginRequiredMixin, View):
    login_url = '/user/login/'
    object_model = Answer
    rating_model = UserAnswerRating
    field_name = 'answer'


class QuestionRating(RatingMixin, LoginRequiredMixin, View):
    login_url = '/user/login/'
    object_model = Question
    rating_model = UserQuestionRating
    field_name = 'question'
