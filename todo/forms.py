from django import forms


class TodoForm(forms.Form):
    text = forms.CharField(max_length=60, widget=forms.TextInput(
        attrs={'class': 'form-control',
               'placeholder': 'Co jest zo zrobienia...?', 'aria-label': 'Todo',
               'aria-describedby': 'add-btn'}))
