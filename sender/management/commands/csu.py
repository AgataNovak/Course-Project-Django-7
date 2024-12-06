import json

from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = "Создание группы пользователей"

    def add_arguments(self, parser):
        parser.add_argument("group_name", type=str, help="Название группы")

    def handle(self, *args, **kwargs):
        group_name = kwargs["group_name"]

        group, created = Group.objects.get_or_create(name=group_name)

        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Группа "{group_name}" создана')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Группа "{group_name}" существует')
            )
