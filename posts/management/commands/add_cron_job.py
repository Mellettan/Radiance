from django.core.management.base import BaseCommand
from crontab import CronTab
import os
from pathlib import Path


class Command(BaseCommand):
    help = 'Adds a CRON job to schedule daily posts for bots'

    def handle(self, *args, **kwargs):
        user_cron = CronTab(user=True)

        project_dir = Path(__file__).resolve().parent.parent.parent.parent
        manage_py = os.path.join(project_dir, 'manage.py')

        job = user_cron.new(command=f'python3 {manage_py} schedule_daily_posts', comment='Django Bot Posts')

        job.setall('0 0 * * *')

        user_cron.write()

        self.stdout.write(self.style.SUCCESS('Successfully added CRON job to schedule daily posts'))
