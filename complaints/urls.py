from django.urls import path
from . import views

urlpatterns = [

    path('', views.user_login, name="login"),   # ✅ LOGIN FIRST

    path('dashboard/', views.dashboard, name="dashboard"),
    path('submit/', views.submit_complaint, name="submit_complaint"),
    path('delete/<int:id>/', views.delete_complaint, name="delete_complaint"),
    path('update/<int:id>/', views.update_status, name="update_status"),
    path('track/', views.track_complaint, name="track_complaint"),

    path('login/', views.user_login, name="login"),
    path('register/', views.register, name="register"),
    path('logout/', views.user_logout, name="logout"),

    path('download/<int:id>/', views.download_report, name="download_report"),

    path("pending/", views.pending_list, name="pending"),
    path("progress/", views.progress_list, name="progress"),
    path("resolved/", views.resolved_list, name="resolved"),
]