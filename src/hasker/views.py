from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import View

from config import settings

from .forms import AskQuestionForm
from .mixins import RatingViewMixin
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
    login_url = reverse_lazy('users:login')

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
            return redirect('hasker:index_url')

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
        return redirect(reverse('hasker:answer_url', kwargs={'id': id}))


class SetCorrectAnswer(LoginRequiredMixin, View):
    login_url = reverse_lazy('users:login')

    def post(self, request, id):
        answer = get_object_or_404(Answer.objects.select_related('question__author'), id=id)
        if request.user == answer.question.author:
            answer.set_correct_answer()

        return redirect(reverse('hasker:answer_url', kwargs={'id': answer.question.id}))


class AnswerRating(RatingViewMixin, LoginRequiredMixin, View):
    login_url = reverse_lazy('users:login')
    object_model = Answer
    rating_model = UserAnswerRating
    field_name = 'answer'


class QuestionRating(RatingViewMixin, LoginRequiredMixin, View):
    login_url = reverse_lazy('users:login')
    object_model = Question
    rating_model = UserQuestionRating
    field_name = 'question'
