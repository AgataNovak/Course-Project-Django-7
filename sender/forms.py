from django import forms
from .models import Receiver, Message, MailDeliver
from django.core.exceptions import ValidationError


class ReceiverForm(forms.ModelForm):
    class Meta:
        model = Receiver
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(ReceiverForm, self).__init__(*args, **kwargs)

        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите email получателя'
        })

        self.fields['full_name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите ФИО получателя'
        })

        self.fields['note'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите комментарий'
        })


class MessageForm(forms.ModelForm):

    class Meta:
        model = Message
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(MessageForm, self).__init__(*args, **kwargs)

        self.fields['title'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите тему письма'
        })

        self.fields['content'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите тело письма'
        })


class MailDeliverForm(forms.ModelForm):
    class Meta:
        model = MailDeliver
        fields = '__all__'
        widget = {
        "start_time": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        "end_time": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }