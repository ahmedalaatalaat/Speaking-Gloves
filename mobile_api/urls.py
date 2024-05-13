from django.urls import path
from . import views

app_name = "mobile_api"

urlpatterns = [
    path("registration/", views.RegistrationView.as_view(), name="registration"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("reset_password/", views.ResetUserPassword.as_view(), name="reset_password"),
    path("lessons/", views.SignLanguageLessonView.as_view(), name="sign_language_lessons"),
]