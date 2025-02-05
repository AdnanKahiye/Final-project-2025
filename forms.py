from django import forms
from .models import FinancialData

class FinancialDataForm(forms.ModelForm):
    class Meta:
        model = FinancialData
        fields = [
            "text_input",
            "tirada",
            "qiimaha_soo_iibsiga",
            "qiimaha_iska_iibinta",
            "kharashaadka",
            "dakhliga",
            "faa_iido",
            "faa_iidada_percent",
            "khasaaro",
            "khasaaro_percent",
            "dakhliga_hadda",
        ]
