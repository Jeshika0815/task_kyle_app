# forms.py
from django import forms

# Prompt form for user input
class PromptForm(forms.Form):
    prompt = forms.CharField()

#class edit_schedule(forms.Form):
