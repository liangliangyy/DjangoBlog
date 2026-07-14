from django.contrib.auth.forms import forms
from django.forms import widgets


class RequireEmailForm(forms.Form):
    email = forms.EmailField(label='电子邮箱', required=True)

    def __init__(self, *args, **kwargs):
        super(RequireEmailForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget = widgets.EmailInput(
            attrs={'placeholder': "email", "class": "form-control"})
