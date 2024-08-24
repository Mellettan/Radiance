from django.core.management.base import BaseCommand
from crontab import CronTab


class Command(BaseCommand):
    help = 'Removes the CRON job for scheduling daily posts'

    def handle(self, *args, **kwargs):
        user_cron = CronTab(user=True)

        user_cron.remove_all(comment='Django Bot Posts')

        user_cron.write()

        self.stdout.write(self.style.SUCCESS('Successfully removed CRON job for scheduling daily posts'))
