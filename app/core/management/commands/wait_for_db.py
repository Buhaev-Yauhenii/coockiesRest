"""
    Command for waiting base
"""
import time
from psycopg2 import OperationalError as Psycopg2Error
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        """Entrypoint for command."""
        self.stdout.write('wating for database.')
        db_up = False
        while not db_up:
            try:
                self.check(databases=['default'])
                db_up = True
            except (Psycopg2Error, OperationalError):
                self.stdout.write('database unavailable, please wait 1 second')
                time.sleep(1)
        self.stdout.write(self.style.SUCCESS('database available'))
