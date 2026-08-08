from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("catalog", views.list_surveys_catalog, name="list_surveys_catalog"),
    path("results", views.calculate_results, name="calculate_results"),
    path('survey/<str:id>', views.get_survey, name="get_survey"),
    path("history", views.get_history, name="get_history"),
    path("download-csv", views.download_csv, name="download_csv"),
    path('history/<str:response_type>/', views.history_view, name='history_by_type'),
    path('participate/<str:id>', views.get_survey_consent, name="get_survey_consent"),
]