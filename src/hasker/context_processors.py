from config import settings

from .models import Question


def get_trends(request):
    trends = Question.objects.order_by('-rating').values_list('title', 'rating')[:settings.TRENDING_RESULT_SIZE]
    return {'trends': trends}
