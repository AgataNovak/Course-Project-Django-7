from django.db import models
from users.models import CustomUser
import logging
from django.core.mail import BadHeaderError, send_mail
from django.utils import timezone
from config import settings


class Receiver(models.Model):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=100)
    note = models.TextField(blank=True)
    owner = models.ForeignKey(
        CustomUser,
        verbose_name="Владелец",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = "Получатель"
        verbose_name_plural = "Получатели"
        ordering = ["full_name"]
        permissions = [
            ("can_view_all_receivers", "can view all receivers"),
        ]


class Message(models.Model):
    title = models.CharField(max_length=150)
    content = models.TextField()
    owner = models.ForeignKey(
        CustomUser,
        verbose_name="Владелец",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        ordering = ["title"]
        permissions = [
            ("can_view_all_messages", "can view all messages"),
        ]


class MailDeliver(models.Model):
    STATUS_VARIANTS = [
        ("Создана", "Создана"),
        ("Запущена", "Запущена"),
        ("Завершена", "Завершена"),
    ]

    first_send_time = models.DateTimeField(null=True, blank=True,
                                           help_text="Укажите время начала отправки в формате ГГГН-ММ-ДД ЧЧ:ММ")
    end_send_time = models.DateTimeField(null=True, blank=True,
                                         help_text="Укажите время окончания отправки в формате ГГГГ-ММ-ДД ЧЧ:ММ")
    status = models.CharField(max_length=11, choices=STATUS_VARIANTS, default=STATUS_VARIANTS[0])
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    receivers = models.ManyToManyField(Receiver)
    owner = models.ForeignKey(
        CustomUser,
        verbose_name="Владелец",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    is_blocked = models.BooleanField(default=False)

    def __str__(self):
        return f'Рассылка № {self.pk} - {self.status}'

    def send_mailing(self):
        user_stats, created = UserMailingStatistics.objects.get_or_create(
            user=self.owner
        )
        if self.is_blocked:
            logging.info(f"Рассылка {self.pk} заблокирована.")
            return

        if self.status != "Создана":
            logging.info(f"Начало выполнения задачи: {self.status}")
            return

        if self.status != "Запущена":
            self.status = "Запущена"
            self.start_datetime = timezone.now()
            self.save()

            recipients = self.receivers.all()
            success_count = 0
            for recipient in recipients:
                logging.info(f"Начало выполнения задачи: {recipient.email}")
                try:
                    send_mail(
                        subject=self.message.title,
                        message=self.message.content,
                        from_email=settings.EMAIL_HOST_USER,
                        recipient_list=[recipient.email],
                        fail_silently=False,
                    )

                    MailAttempt.objects.create(
                        mailing=self,
                        status="Успешно",
                        server_response="Письмо отправлено успешно.",
                        attempt_datetime=timezone.now(),
                    )

                    success_count += 1
                    user_stats.update_statistics(success=True)

                except BadHeaderError as e:
                    logging.error(f"Ошибка отправки письма: {e}.")
                    MailAttempt.objects.create(
                        mailing=self,
                        status="Не успешно",
                        server_response=str(e),
                        attempt_datetime=timezone.now(),
                    )
                    user_stats.update_statistics(success=False)

                except Exception as e:
                    logging.error(f"Ошибка отправки письма: {e}.")
                    MailAttempt.objects.create(
                        mailing=self,
                        status="Не успешно",
                        server_response=str(e),
                        attempt_datetime=timezone.now(),
                    )
                    user_stats.update_statistics(success=False)

            if success_count == len(recipients):
                self.status = "Завершена"
            self.save()

    def block_mailing(self):
        self.is_blocked = True
        self.save()
        logging.info(f"Рассылка {self.pk} заблокирована.")

    def unblock_mailing(self):
        self.is_blocked = False
        self.save()
        logging.info(f"Рассылка {self.pk} разблокирована.")


class MailAttempt(models.Model):
    ATTEMPT_STATUS_VARIANTS = [
        ("Успешно", "Успешно"),
        ("Неуспешно", "Неуспешно"),
    ]

    attempt_datetime = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=ATTEMPT_STATUS_VARIANTS)
    server_response = models.TextField(blank=True)
    mailing = models.ForeignKey(MailDeliver, on_delete=models.CASCADE)
    owner = models.ForeignKey(
        CustomUser,
        verbose_name="Владелец",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    def __str__(self):
        return f"Попытка: {self.status} at {self.attempt_datetime}"

    class Meta:
        verbose_name = "Попытка рассылки"
        verbose_name_plural = "Попытки рассылки"
        permissions = [
            ("can_view_all_mail_attempts", "can view all mail attempts"),
        ]


class UserMailingStatistics(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    total_mailings = models.PositiveIntegerField(default=0)
    successful_mailings = models.PositiveIntegerField(default=0)
    failed_mailings = models.PositiveIntegerField(default=0)

    def update_statistics(self, success):
        self.total_mailings += 1
        if success:
            self.successful_mailings += 1
        else:
            self.failed_mailings += 1
        self.save()
