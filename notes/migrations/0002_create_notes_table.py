# Generated migration with raw SQL
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notes', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            CREATE TABLE IF NOT EXISTS `notes` (
              `id` INT AUTO_INCREMENT PRIMARY KEY,
              `title` varchar(100) NOT NULL,
              `description` text NOT NULL
            );
            """,
            reverse_sql="DROP TABLE IF EXISTS `notes`;",
        ),
    ]
