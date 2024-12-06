from django.views.generic.edit import CreateView
from django.conf import settings
from django.urls import reverse_lazy
from django.core.mail import send_mail
from django.contrib.auth import login
from .forms import CustomUserCreationForm


class RegisterView(CreateView):
    template_name = 'register.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('sender:receiver_list')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        self.send_welcome_email(user.email)
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)

    def send_welcome_email(self, user_email):
        subject = "Добро пожаловать в приложение для создания рассылок!!"
        message = "Спасибо, что зарегистрировались в приложении!"
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [user_email,]
        send_mail(subject, message, from_email, recipient_list)
