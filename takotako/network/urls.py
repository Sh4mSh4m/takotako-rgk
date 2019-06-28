from django.urls import path, include
from django.contrib import admin
from . import views
from network.views import InventoryView, SnapshotView, ConfigView, ExportView, ReviewView

app_name = 'network'

urlpatterns = [
    # Index ex: /network/
    # path('', views.index, name='index'),
    path('', InventoryView.as_view(), name='index'),
    path('snapshot/', SnapshotView.as_view(), name='snapshot'),
    path('config/', ConfigView.as_view(), name='config'),
    path('testpage/', views.testpage, name='testpage'),
    path('browser/', views.browser, name='browser'),
    path('export/', ExportView.as_view(), name='export'),
    path('poll_state/', views.poll_state, name="poll_state"),
    path('review/', ReviewView.as_view(), name='review'),
]
