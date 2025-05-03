from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from .models import TICKET


class UserForm(forms.ModelForm):
    password = forms.CharField(
        label='Contraseña',
        required=False,
        widget=forms.PasswordInput()
    )
    
    password_confirmation = forms.CharField(
        label='Confirmar Contraseña',
        required=False,
        widget=forms.PasswordInput()
    )
    
    cargo = forms.ChoiceField(
        
        choices=[('', 'Seleccione un cargo'),('Administrador', 'Administrador'), ('Analista', 'Analista'), ('Usuario', 'Usuario')],
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        labels = {
            'username': 'Nombre de usuario',
            'email': 'Correo electrónico',
            'first_name': 'Nombre',
            'last_name': 'cargo',
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirmation = cleaned_data.get('password_confirmation')

        if password or password_confirmation:
            if password != password_confirmation:
                self.add_error('password_confirmation', 'Las contraseñas no coinciden.')

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password")
        if password:
            user.set_password(password)
        user.last_name = self.cleaned_data.get("cargo", user.last_name)

        if commit:
            user.save()
        return user
    
class TicketForm(forms.ModelForm):
    id_usuario_asignado = forms.ModelChoiceField(
        queryset=User.objects.all(),
        label="Asignar a",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    id_usuario_solicitante = forms.ModelChoiceField(
        queryset=User.objects.all(),
        label="Solicitante",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = TICKET
        fields = ['titulo', 'descripcion', 'prioridad', 'estado', 'id_usuario_solicitante', 'id_usuario_asignado']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control'}),
            'prioridad': forms.Select(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
        }

