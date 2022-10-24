from django.db.models import Q
from rest_framework import filters, viewsets
from rest_framework.pagination import PageNumberPagination

from config import settings
from hasker.models import Answer, Question

from .serializers import AnswerSerializer, QuestionSerializer, TrendingSerializer


class QuestionSetPagination(PageNumberPagination):
    page_size = settings.QUESTIONS_PER_PAGE
    page_size_query_param = 'page_size'


class AnswerSetPagination(PageNumberPagination):
    page_size = settings.ANSWERS_PER_PAGE
    page_size_query_param = 'page_size'


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects_with_join.all()
    serializer_class = QuestionSerializer
    model = Question
    serializer = QuestionSerializer
    pagination_class = QuestionSetPagination
    http_method_names = ['get']  # По заданию, реализовываем только получение.


class TrendingViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.order_by('-rating')
    serializer_class = TrendingSerializer
    model = Question
    serializer = TrendingSerializer
    pagination_class = QuestionSetPagination
    http_method_names = ['get']


class AnswerViewSet(viewsets.ModelViewSet):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
    model = Answer
    serializer = AnswerSerializer
    pagination_class = AnswerSetPagination
    filter_backends = [filters.OrderingFilter]
    ordering = ['-rating', '-created_date']
    http_method_names = ['get']  # По заданию, реализовываем только получение.

    def get_queryset(self):
        question_id = self.kwargs['question_id']
        return Answer.objects.filter(question=question_id)


class SearchViewSet(viewsets.ModelViewSet):
    queryset = Question.objects_with_join.all()
    serializer_class = QuestionSerializer
    model = Question
    serializer = QuestionSerializer
    http_method_names = ['get']
    filter_backends = [filters.OrderingFilter]
    ordering = ['-rating', '-created_date']

    def get_queryset(self):
        queryset = Question.objects_with_join.all()
        query = self.request.query_params.get('q')
        if query is not None:
            if 'tag:' in query:
                tag = query.split(':')[1].strip()
                queryset = queryset.filter(question_tags__tag__name=tag)
            else:
                queryset = queryset.filter(Q(title__icontains=query) | Q(text__icontains=query))
        return queryset
