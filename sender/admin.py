from django.contrib import admin
from .models import Receiver, Message, MailDeliver, MailAttempt


@admin.register(Receiver)
class ReceiverAdmin(admin.ModelAdmin):
    list_display = ('email', 'full_name', 'note')
    list_filter = ('full_name',)
    search_fields = ('full_name', 'note', 'email',)


@admin.register(Message)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'content')
    search_fields = ('title', 'content',)


@admin.register(MailDeliver)
class MailingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "first_send_time",
        "end_send_time",
        "status",
        "message",
    )
    list_filter = ("status",)
    search_fields = (
        "message",
        "receivers",
    )


@admin.register(MailAttempt)
class MailingAttemptAdmin(admin.ModelAdmin):
    list_display = ("id", "attempt_datetime", "status", "server_response", "mailing")
    list_filter = (
        "status",
        "attempt_datetime",
    )
    search_fields = ("attempt_datetime",)
