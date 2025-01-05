from django import forms

from celleryworker.models import Message


class SearchForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput({
        'id': 'search-input',
        'name':'username',
        'placeholder':'Поиск пользователей',
    }
    ))

class MessageSendForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['text']
        widgets = {
            'text': forms.TextInput(attrs={
                'type': 'text',
                'placeholder':'Введите сообщение...',
                'id': 'message-input',
                }
            )}
