from django import forms



class SearchForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput({
        'id': 'search-input',
        'name':'username',
        'placeholder':'Поиск пользователей',
    }
    ))
