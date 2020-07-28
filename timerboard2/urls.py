from django.conf.urls import url

from . import views

app_name = "timerboard2"

urlpatterns = [
    url(r"^add/$", views.AddTimerView.as_view(), name="add"),
    url(r"^remove/(?P<pk>\w+)$", views.RemoveTimerView.as_view(), name="delete"),
    url(r"^edit/(?P<pk>\w+)$", views.EditTimerView.as_view(), name="edit"),
    url(r"^$", views.timer_list, name="timer_list"),
    url(
        r"^list_data/(?P<tab_name>\w+)$", views.timer_list_data, name="timer_list_data"
    ),
    url(r"^get_timer_data/(?P<pk>\w+)$", views.get_timer_data, name="get_timer_data"),
]
