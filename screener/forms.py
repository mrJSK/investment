from django import forms
from django.forms import inlineformset_factory
from .models import Scan, Condition

class ScanForm(forms.ModelForm):
    class Meta:
        model = Scan
        fields = ['name', 'timeframe', 'segment']
        widgets = {
            'timeframe': forms.Select(attrs={'class': 'form-select'}),
            'segment': forms.Select(attrs={'class': 'form-select'}),
        }

class ConditionForm(forms.ModelForm):
    class Meta:
        model = Condition
        exclude = ['scan']
        widgets = {
            'left_indicator': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Indicator or field'}),
            'operator': forms.Select(attrs={'class': 'form-select'}),
            'right_indicator': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Indicator'}),
            'constant': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'logic': forms.Select(attrs={'class': 'form-select'}),
        }

# Inline formset for dynamic addition of Condition forms
ConditionFormSet = inlineformset_factory(Scan, Condition, form=ConditionForm, extra=1, can_delete=True)
