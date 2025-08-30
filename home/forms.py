from django import forms
from .models import CropOutcome

class CropOutcomeForm(forms.ModelForm):
    class Meta:
        model = CropOutcome
        fields = ["status", "yield_amount", "notes"]
        widgets = {
            "status": forms.Select(attrs={"class": "form-control"}),
            "yield_amount": forms.NumberInput(attrs={"class": "form-control"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }
