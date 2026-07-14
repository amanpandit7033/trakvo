from django.core.management.base import BaseCommand
from apps.accounts.models import CustomUser

class Command(BaseCommand):
    help = 'Create a super admin user for the Trakvo platform'

    def add_arguments(self, parser):
        parser.add_argument('--phone', type=str, required=True, help='Phone number for the super admin')
        parser.add_argument('--password', type=str, required=True, help='Password for the super admin')

    def handle(self, *args, **options):
        phone = options['phone']
        password = options['password']

        if CustomUser.objects.filter(phone_number=phone).exists():
            self.stdout.write(self.style.ERROR(f'User with phone {phone} already exists.'))
            return

        user = CustomUser.objects.create_user(
            phone_number=phone,
            password=password,
            role='super_admin'
        )
        # Ensure institute is null (which is default, but just to be sure)
        user.institute = None
        user.is_staff = True
        user.is_superuser = True
        user.save()

        self.stdout.write(self.style.SUCCESS(f'Successfully created super admin {phone}'))
