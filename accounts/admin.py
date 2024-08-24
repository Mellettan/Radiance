from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, Subscription


class SubscriptionInline(admin.TabularInline):
    """
    Inline панель для модели подписки.

    Attributes:
        model (Subscription): модель, которая будет отображаться.
        extra (int): количество дополнительных встроенных форм.
        fields (List[str]): поля, которые будут отображаться.
        fk_name (str): имя поля внешнего ключа.
    """

    model = Subscription
    extra = 0
    fields = ("follower", "following")
    fk_name = "follower"


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Админ-панель управления пользователями.

    Attributes:
        model: модель, которая будет отображаться.
        list_display: поля, которые будут отображаться в виде списка.
        list_filter: поля, которые будут использоваться для фильтрации в представлении списка.
        search_fields: поля, которые будут использоваться для поиска в представлении списка.
        ordering: поля, которые будут использоваться для упорядочивания в представлении списка.
        fieldsets: наборы полей, которые будут отображаться в формах добавления/изменения.
        add_fieldsets: наборы полей, которые будут отображаться в форме добавления.
        inlines: встроенные панели, которые будут отображаться в формах добавления/изменения.
    """

    def get_following(self, obj: CustomUser) -> str:
        """
        Возвращает разделенную запятыми строку из адресов электронной почты пользователей,
        на которых подписан данный пользователь.

        Args:
            obj: Модель пользователя.

        Returns:
            str: Строка адресов электронной почты, разделенная запятыми.
        """
        return ", ".join(user.email for user in obj.get_following())

    get_following.short_description = "Following"

    def get_followers(self, obj: CustomUser) -> str:
        """
        Возвращает разделенную запятыми строку из адресов электронной почты пользователей,
        которые подписаны на данного пользователя.

        Args:
            obj: Модель пользователя.

        Returns:
            str: Строка адресов электронной почты, разделенная запятыми.
        """
        return ", ".join(user.email for user in obj.get_followers())

    get_followers.short_description = "Followers"

    model = CustomUser
    list_display = (
        "pk",
        "email",
        "username",
        "is_active",
        "is_staff",
        "is_bot",
        "is_superuser",
        "email_verified",
        "date_joined",
        "get_following",
        "get_followers",
    )
    list_filter = ("is_active", "is_staff", "is_bot")
    search_fields = ("email", "username")
    ordering = (
        "pk",
        "email",
    )

    fieldsets = (
        (None, {"fields": ("email", "password", "email_verified")}),
        ("Personal info", {"fields": ("username", "avatar")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "user_permissions",
                    "groups",
                )
            },
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "username", "password1", "password2"),
            },
        ),
    )

    inlines = [SubscriptionInline]
