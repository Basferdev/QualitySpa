from django import forms
from django.contrib.auth.models import User

class RegistrationForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Ingrese su nombre de usuario'
    }), label="Nombre de Usuario")
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Ingrese su correo electrónico'
    }), label="Correo Electrónico")
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Ingrese su contraseña'
    }), label="Contraseña")
    password_confirm = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Confirme su contraseña'
    }), label="Confirmar Contraseña")
    phone_number = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Ingrese su número de contacto'
    }), label="Número de Teléfono")
    address = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control',
        'placeholder': 'Ingrese su dirección'
    }), label="Dirección")
    postal_code = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Ingrese su código postal'
    }), label="Código Postal")
    first_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Ingrese su nombre'
    }), label="Nombre")
    last_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Ingrese su apellido'
    }), label="Apellido")

    class Meta:
        model = User
        fields = ['username', 'email']
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("El nombre de usuario ya está en uso. Por favor elige otro.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("El correo electrónico ya está en uso. Por favor elige otro.")
        return email

    def clean_password(self):
        password = self.cleaned_data.get("password")

        # Validar que la contraseña tenga exactamente 8 caracteres
        if len(password) != 8:
            raise forms.ValidationError("La contraseña debe tener exactamente 8 caracteres.")

        # Validar que la contraseña contenga al menos una letra mayúscula
        if not any(char.isupper() for char in password):
            raise forms.ValidationError("La contraseña debe contener al menos una letra mayúscula.")

        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        # Validar que las contraseñas coincidan
        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "Las contraseñas no coinciden.")

        # Validar que todos los campos sean obligatorios
        for field_name, field_value in cleaned_data.items():
            if not field_value:
                self.add_error(field_name, f"El campo {self.fields[field_name].label} es obligatorio.")
        return cleaned_data


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Nombre de usuario'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Contraseña'
    }))