from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import ListView, DetailView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from sender.models import Message, Receiver, MailDeliver, MailAttempt, UserMailingStatistics
from sender.forms import ReceiverForm, MessageForm, MailDeliverForm
from sender.services import get_receivers_from_cache, get_messages_from_cache, get_mailings_from_cache
from django.http import HttpResponseForbidden
from utils.logger import setup_logging

setup_logging()


class ReceiverListView(ListView):
    model = Receiver
    template_name = "sender/receiver_list.html"
    context_object_name = "receivers"


class ReceiverCreateView(CreateView):
    model = Receiver
    form_class = ReceiverForm
    template_name = 'sender/receiver_create.html'
    success_url = reverse_lazy('sender:receiver_list')

    def form_valid(self, form):
        receiver = form.save()
        user = self.request.user
        receiver.owner = user
        receiver.save()
        return super().form_valid(form)

    def get_queryset(self):
        return get_receivers_from_cache()


class ReceiverDetailView(DetailView):
    model = Receiver
    template_name = 'sender/receiver_detail.html'
    context_object_name = 'receivers'


class ReceiverUpdateView(UpdateView):
    model = Receiver
    form_class = ReceiverForm
    template_name = 'sender/receiver_form.html'
    success_url = reverse_lazy('sender:receiver_list')

    def get_form_class(self):
        user = self.request.user
        if user == self.object.owner:
            return ReceiverForm
        raise PermissionDenied


class ReceiverDeleteView(DeleteView):
    model = Receiver
    template_name = 'sender/receive_delete.html'
    success_url = reverse_lazy('sender:receiver_list')


class MessageListView(ListView):
    model = Message
    template_name = "sender/message_list.html"
    context_object_name = "messages"


class MessageDetailView(DetailView):
    model = Message
    template_name = 'sender/message_detail.html'
    context_object_name = 'messages'


class MessageCreateView(CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'sender/message_create.html'
    success_url = reverse_lazy('sender:message_list')


class MessageUpdateView(UpdateView):
    model = Message
    form_class = MessageForm
    template_name = 'sender/message_form.html'
    success_url = reverse_lazy('sender:message_list')

    def get_form_class(self):
        user = self.request.user
        if user == self.object.owner:
            return MessageForm
        raise PermissionDenied


class MessageDeleteView(DeleteView):
    model = Message
    template_name = 'sender/message_delete.html'
    success_url = reverse_lazy('sender:message_list')


class HomePageView(View):
    template_name = "sender/home.html"

    def get(self, request):
        total_mailings = MailDeliver.objects.count()
        active_mailings = MailDeliver.objects.filter(status="Запущена").count()
        unique_recipients = Receiver.objects.distinct().count()

        context = {
            "total_mailings": total_mailings,
            "active_mailings": active_mailings,
            "unique_receivers": unique_recipients,
        }

        return render(request, self.template_name, context)


class MailingListView(LoginRequiredMixin, ListView):
    model = MailDeliver
    form_class = MailDeliverForm
    template_name = "sender/mailing_list.html"
    context_object_name = "mailing_list"

    def get_queryset(self):
        if self.request.user.is_superuser or self.request.user.has_permission(
                "can_view_all_mailings"
        ):
            return get_mailings_from_cache()
        else:
            user = self.request.user
            return MailDeliver.objects.filter(owner=user)


class MailingCreateView(View):
    def get(self, request):
        form = MailDeliverForm()
        return render(request, "sender/mailing_form.html", {"form": form})

    def post(self, request):
        form = MailDeliverForm(request.POST)
        if form.is_valid():
            mailing = form.save(commit=False)
            mailing.owner = request.user
            mailing.save()
            return redirect("sender:mailing_list")
        return render(request, "sender/mailing_form.html", {"form": form})


class MailingUpdateView(UpdateView):
    model = MailDeliver
    form_class = MailDeliverForm
    template_name = "sender/mailing_form.html"
    success_url = reverse_lazy("sender:mailing_list")

    def get_queryset(self):
        return MailDeliver.objects.filter(owner=self.request.user)

    def get_object(self, queryset=None):
        try:
            return super().get_object(queryset)
        except MailDeliver.DoesNotExist:
            raise PermissionDenied("У Вас нет прав для редактирования этого сообщения.")


class MailingDeleteView(LoginRequiredMixin, DeleteView):
    model = MailDeliver
    template_name = "sender/mailing_delete.html"
    success_url = reverse_lazy("sender:mailing_list")

    def test_func(self):
        return (
            self.request.user.is_authenticated
            and self.request.user.has_perm("sender.delete_mailing")
            or self.request.mailing.owner
        )

    def handle_no_permission(self):
        return redirect("sender:mailing_list")

    def get_object(self, queryset=None):
        return get_object_or_404(MailDeliver, pk=self.kwargs["pk"])


class MailingDetailView(DetailView):
    model = MailDeliver
    template_name = "sender/mailing_detail.html"
    context_object_name = "mailing"


class MailingStartView(View):

    def get(self, request, mailing_id):
        mailing = get_object_or_404(MailDeliver, id=mailing_id)
        return render(request, "sender/mailing_start.html", {"object": mailing})

    def post(self, request, mailing_id):
        mailing = get_object_or_404(MailDeliver, id=mailing_id)
        mailing.send_mailing()
        return redirect("sender:mailing_attempt_list")


class MailingAttemptListView(ListView):
    model = MailAttempt
    template_name = "sender/mailing_attempt_list.html"
    context_object_name = "mailing_attempt_list"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["mailings"] = MailDeliver.objects.all()
        return context


class MailingClearAttemptsView(View):

    def post(self, request):
        MailAttempt.objects.all().delete()
        return redirect("mail:mailing_attempt_list")


class UserMailingStatisticsView(View):
    def get(self, request):
        user_stats, created = UserMailingStatistics.objects.get_or_create(
            user=request.user
        )

        return render(request, "sender/user_statistics.html", {"user_stats": user_stats})


class BlockMailingView(LoginRequiredMixin, View):

    def get(self, request, mailing_id):
        mailing = get_object_or_404(MailDeliver, id=mailing_id)
        return render(request, "sender/mailing_block.html", {"mailing": mailing})

    def post(self, request, mailing_id):
        mailing = get_object_or_404(MailDeliver, id=mailing_id)

        if not request.user.has_perm("mail.can_disable_mailings"):
            return HttpResponseForbidden("У Вас нет прав для блокировки рассылки.")

        is_blocked = request.POST.get("is_blocked")
        mailing.is_blocked = is_blocked == "on"
        mailing.save()
        return redirect("mail:mailing_list")
