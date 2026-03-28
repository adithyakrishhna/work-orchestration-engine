from django.urls import path
from .views import (
    AIPriorityScoringView, AIBulkScoringView,
    AITaskRoutingView, AIAutoAssignView,
    NLQueryView,
)

urlpatterns = [
    path('score-priority/', AIPriorityScoringView.as_view(), name='ai-score-priority'),
    path('score-all/', AIBulkScoringView.as_view(), name='ai-score-all'),
    path('recommend-assignee/', AITaskRoutingView.as_view(), name='ai-recommend-assignee'),
    path('auto-assign/', AIAutoAssignView.as_view(), name='ai-auto-assign'),
    path('query/', NLQueryView.as_view(), name='ai-nl-query'),
]