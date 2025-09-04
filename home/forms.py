from django import forms
from .models import CropOutcome

class CropOutcomeForm(forms.ModelForm):
    class Meta:
        model = CropOutcome
        fields = ["yield_amount", "notes"]
        widgets = {
            "yield_amount": forms.NumberInput(attrs={"class": "form-control"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }
