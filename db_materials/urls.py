from django.urls import path

from db_materials.views import MEUsageAPIView, ScaffoldingAPIView

app_name = 'db_materials'

urlpatterns = [
    path("me_usages/", MEUsageAPIView.as_view(), name='me_usages'),
    path("scaffolding/", ScaffoldingAPIView.as_view(), name='scaffolding'),
]
