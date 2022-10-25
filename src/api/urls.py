from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import AnswerViewSet, QuestionViewSet, SearchViewSet, TrendingViewSet


app_name = 'api'


router = DefaultRouter()
router.register('questions', QuestionViewSet, basename='questions')
router.register('trending', TrendingViewSet, basename='trending')
router.register('search', SearchViewSet, basename='search')
router.register(r'questions/(?P<question_id>\d+)/answers', AnswerViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
