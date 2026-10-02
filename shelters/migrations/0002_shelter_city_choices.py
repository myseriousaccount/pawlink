from django.db import migrations, models


def normalize_kyiv(apps, schema_editor):
    Shelter = apps.get_model('shelters', 'Shelter')
    Shelter.objects.filter(city__iexact='Kyiv').update(city='Київ')


class Migration(migrations.Migration):
    dependencies = [
        ('shelters', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(normalize_kyiv, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='shelter',
            name='city',
            field=models.CharField(
                choices=[('Київ', 'Київ')],
                max_length=200,
                verbose_name='Місто',
            ),
        ),
    ]
