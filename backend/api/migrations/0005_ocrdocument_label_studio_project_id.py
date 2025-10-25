# Generated migration for adding label_studio_project_id field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_ocrdocument_corrected_label_studio_json_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='ocrdocument',
            name='label_studio_project_id',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Label Studio项目ID'),
        ),
    ]
