from rest_framework import serializers

from hasker.models import Answer, Question


class QuestionSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    rating = serializers.ReadOnlyField()

    class Meta:
        fields = ('id', 'title', 'text', 'author', 'created_date', 'rating')
        model = Question


class TrendingSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('title', 'rating')
        model = Question


class AnswerSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'text', 'author', 'created_date', 'is_correct_answer', 'rating', 'question')
        model = Answer
