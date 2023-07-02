from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path

from api import views
from api import mobile_views

# source venv/bin/activate
# sudo lsof -t -i tcp:8000 | xargs kill -9
# pynt setup_backend add_test_data
urlpatterns = [
    re_path("admin/", admin.site.urls),
    path("survey/<str:type>", views.survey, name="survey"),
    path("newsletter/", views.newsletter, name="newsletter"),
    path("test_newsletter/", views.test_newsletter, name="test_newsletter"),
    path("wordpress/", views.wordpress, name="wordpress"),
    path("thank_you", views.thank_you, name="thank_you"),
    url(r"^select2/", include("django_select2.urls")),
]
urlpatterns += [
    path("mobile/login", mobile_views.login, name="m_login"),
    path("mobile/register", mobile_views.register, name="m_register"),
    path("mobile/changepassword", mobile_views.update_password, name="m_changepassword"),
    path("mobile/verify_otp", mobile_views.verify_otp_token, name="m_verify_otp"),
    path("mobile/send_otp", mobile_views.send_otp, name="m_send_otp"),
    path("mobile/forgetpassword", mobile_views.forgot_password, name="m_forgetpassword")


]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
