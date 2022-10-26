from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, reverse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, View
from django.views.generic.edit import FormView

from config import settings

from .forms import AskQuestionForm
from .mixins import CustomPaginator, RatingViewMixin
from .models import Answer, Question, UserAnswerRating, UserQuestionRating


class Index(CustomPaginator, TemplateView):
    template_name = "hasker/index.html"
    per_page = settings.QUESTIONS_PER_PAGE

    def get_paginator_objects(self):
        return Question.objects_with_join.all()


class Ask(LoginRequiredMixin, FormView):
    login_url = reverse_lazy('users:login')
    template_name = 'hasker/ask.html'
    form_class = AskQuestionForm
    success_url = reverse_lazy('hasker:index_url')

    def form_valid(self, form):
        question = form.save(commit=False)
        question.author = self.request.user
        question_tags = form.cleaned_data['question_tags']
        form.save()
        question.create_tags(question_tags)
        return super().form_valid(form)


class Search(CustomPaginator, TemplateView):
    template_name = "hasker/search.html"
    per_page = settings.QUESTIONS_PER_PAGE

    def get_paginator_objects(self, *args, **kwargs):
        q = self.request.GET.get('q', '')
        if 'tag:' in q:
            tag = q.split(':')[1].strip()
            questions = Question.objects_with_join.filter(question_tags__tag__name=tag)
        else:
            questions = Question.objects_with_join.filter(Q(title__icontains=q) | Q(text__icontains=q))

        return questions.order_by('-rating', '-created_date')


class Answers(CustomPaginator, TemplateView):
    template_name = "hasker/answer.html"
    per_page = settings.ANSWERS_PER_PAGE

    def get_paginator_objects(self, *args, **kwargs):
        id = kwargs.get('id')
        question = get_object_or_404(Question.objects_with_join.prefetch_related('answers'), id=id)
        self.question = question
        return question.answers.select_related('author').all().order_by('-rating', '-created_date')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context.update({'question': self.question})
        return context

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
