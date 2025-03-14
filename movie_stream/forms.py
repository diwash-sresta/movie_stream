from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
            'placeholder': 'Enter your email'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize field widgets with Tailwind CSS classes
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            })
            # Add placeholders
            if field_name == 'username':
                field.widget.attrs['placeholder'] = 'Choose a username'
            elif field_name == 'password1':
                field.widget.attrs['placeholder'] = 'Create a password'
            elif field_name == 'password2':
                field.widget.attrs['placeholder'] = 'Confirm password'

        # Customize help texts
        self.fields['username'].help_text = 'Letters, digits and @/./+/-/_ only.'
        self.fields['password1'].help_text = 'At least 8 characters. Must include letters and numbers.'
        self.fields['password2'].help_text = 'Enter the same password as before.'

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email