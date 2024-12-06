from django.urls import path
from sender.apps import SenderConfig
from sender.views import (ReceiverListView, ReceiverDetailView, ReceiverCreateView, ReceiverUpdateView,
                          ReceiverDeleteView, MessageListView, MessageDetailView, MessageCreateView,
                          MessageDeleteView, MessageUpdateView, HomePageView, MailingListView)
from django.views.decorators.cache import cache_page

app_name = SenderConfig.name

urlpatterns = [
    path("home/", HomePageView.as_view(), name="home_page"),
    path('receiver_list/', ReceiverListView.as_view(), name='receiver_list'),
    path('receiver/create/', ReceiverCreateView.as_view(), name='receiver_create'),
    path('receiver/<int:pk>/detail/', cache_page(60)(ReceiverDetailView.as_view()), name='receiver_detail'),
    path('receiver/<int:pk>/update/', ReceiverUpdateView.as_view(), name='receiver_update'),
    path('receiver/<int:pk>/delete/', ReceiverDeleteView.as_view(), name='receiver_delete'),
    path("message_list/", MessageListView.as_view(), name="message_list"),
    path("message/<int:pk>/detail/", MessageDetailView.as_view(), name="message_detail"),
    path("message/create/", MessageCreateView.as_view(), name="message_create"),
    path("message/<int:pk>/delete", MessageDeleteView.as_view(), name="message_delete"),
    path("message/<int:pk>/update", MessageUpdateView.as_view(), name="message_update"),
    path("mailing_list", M)
]
