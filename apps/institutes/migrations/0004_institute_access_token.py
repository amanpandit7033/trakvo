import uuid
from django.db import migrations, models

def gen_uuid(apps, schema_editor):
    Institute = apps.get_model('institutes', 'Institute')
    for inst in Institute.objects.all():
        inst.access_token = uuid.uuid4()
        inst.save(update_fields=['access_token'])

class Migration(migrations.Migration):

    dependencies = [
        ('institutes', '0003_institute_is_suspended_institute_trial_ends_on'),
    ]

    operations = [
        migrations.AddField(
            model_name='institute',
            name='access_token',
            field=models.UUIDField(default=uuid.uuid4, null=True),
        ),
        migrations.RunPython(gen_uuid, reverse_code=migrations.RunPython.noop),
        migrations.AlterField(
            model_name='institute',
            name='access_token',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
