from django.db import models


class CreatedModel(models.Model):
    """Абстрактная модель для добавления даты создания."""
    pub_date = models.DateTimeField(
        'Дата создания',
        help_text='Дата создания',
        auto_now_add=True
    )

    class Meta:
        abstract = True
        ordering = ('pub_date',)
