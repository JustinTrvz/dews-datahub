from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = "Create an user"

    def add_arguments(self, parser):
        parser.add_argument("username", type=str, help="User name")
        parser.add_argument("password", type=str, help="Password")
        parser.add_argument("mail", type=str, help="E-Mail")


    def handle(self, *args, **options):
        username = options.get("username").lower()
        password = options.get("password")
        mail = options.get("mail").lower()

        # Check if the user already exists
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(username, mail, password)
            user.save
            self.stdout.write(self.style.SUCCESS(f"User '{username}' ({mail}) created successfully."))
        else:
            self.stdout.write(self.style.WARNING(f"User '{username}' ({mail}) already exists."))
