from django.db import models

class Holiday(models.Model):
    date = models.DateField(unique=True, verbose_name="Дата")
    is_workday = models.BooleanField(
        default=False,
        verbose_name="Специальный рабочий день",
        help_text="✓ — рабочий, ☐ — нерабочий"
    )

    class Meta:
        ordering = ['date']
        verbose_name = "Праздничный/рабочий день"
        verbose_name_plural = "Календарь"

    def __str__(self):
        return f"{self.date} — {'рабочий' if self.is_workday else 'праздник'}"
