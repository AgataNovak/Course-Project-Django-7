from django.core.management.base import BaseCommand
from sender.models import MailDeliver


class SendMailCommand(BaseCommand):
    help = 'Комманда для запуска рассылки из коммандной строки'

    def add_arguments(self, parser):
        parser.add_argument("mail_id", type=id)

    def handle(self, *args, **options):
        mail_id = options["mail_id"]
        try:
            send_message = MailDeliver.objects.get(pk=mail_id)
        except MailDeliver.DoesNotExist:
            self.stderr.write(
                self.style.ERROR(f'Рассылка с id {mail_id} не найдена в базе данных.')
            )
            return
        if send_message.status != "Создана":
            self.stderr.write(
                self.style.ERROR(
                    f'Рассылка с id {mail_id} не создана.'
                )
            )
            return
        send_message.send_mail()
        self.stdout.write(self.style.SUCCESS(f'Рассылка с id {mail_id} успешно запущена.'))
