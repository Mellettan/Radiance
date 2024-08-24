from django import forms
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError

from accounts.models import CustomUser


class CustomLoginForm(forms.Form):
    """
    Форма для входа пользователей. Состоит из адреса электронной почты и пароля.
    """

    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"placeholder": "Email", "id": "email"}),
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"placeholder": "Password", "id": "password"}),
    )

    def clean(self) -> dict:
        """
        Проверяет данные формы и проверяет, существует ли пользователь.

        Returns:
            dict: Очищенные данные формы.
        """
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")

        if email and password:
            user = authenticate(email=email, password=password)
            if user is None:
                self.add_error(None, "Invalid email or password")
        return cleaned_data

    def get_user(self) -> CustomUser:
        """
        Возвращает пользователя по введенным данным.

        Returns:
            CustomUser: Пользователь.
        """
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")
        return authenticate(email=email, password=password)


class ChangeEmailForm(forms.ModelForm):
    """
    Форма для изменения email.
    """

    class Meta:
        model = CustomUser
        fields = ["email"]


class CustomRegForm(forms.ModelForm):
    """
    Форма для регистрации пользователя.
    Состоит из имени пользователя, адреса электронной почты и пароля.
    """

    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput,
        min_length=8,
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput,
        min_length=8,
    )

    class Meta:
        model = CustomUser
        fields = ["username", "email"]

    def clean_password2(self):
        """
        Проверяет совпадение двух полей пароля и возвращает подтвержденный пароль.

        Returns:
            str: Пароль.
        """
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords do not match")
        return password2

    def save(self, commit: bool = True) -> CustomUser:
        """
        Сохраняет пользователя как сущность.

        Args:
            commit (bool): Определяет нужно ли сохранять пользователя в
                базе данных. По умолчанию True.

        Returns:
            CustomUser: Сохраненный пользователь.
        """
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
