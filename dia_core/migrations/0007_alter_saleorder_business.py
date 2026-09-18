from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("dia_core", "0006_holderdirectorder_holderdirectreceipt"),
    ]

    operations = [
        migrations.AlterField(
            model_name="saleorder",
            name="business",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="sale_orders",
                to="dia_core.business",
            ),
        ),
    ]
