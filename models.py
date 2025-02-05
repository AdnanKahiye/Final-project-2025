from django.db import models

class FinancialData(models.Model):
    text_input = models.TextField()
    tirada = models.IntegerField(default=1, null=True, blank=True)  # Default to 1
    qiimaha_soo_iibsiga = models.FloatField(null=True, blank=True)  # Can be empty
    qiimaha_iska_iibinta = models.FloatField(null=True, blank=True)
    kharashaadka = models.FloatField(null=True, blank=True)
    dakhliga = models.FloatField(null=True, blank=True)
    faa_iido = models.FloatField(null=True, blank=True)
    faa_iidada_percent = models.FloatField(null=True, blank=True)
    khasaaro = models.FloatField(null=True, blank=True)
    khasaaro_percent = models.FloatField(null=True, blank=True)
    dakhliga_hadda = models.FloatField(null=True, blank=True)
    is_complete = models.BooleanField(default=False)  # To track incomplete records

    def __str__(self):
        return f"Financial Data (ID: {self.id})"
