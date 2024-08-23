from django.contrib import admin
from .models import Post, Comment


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """
    Конфигурация админки для модели Post.

    Этот класс определяет, как объекты модели Post будут отображаться и управляться в админ-панели Django.

    Attributes:
        list_display (tuple): Поля модели Post, которые будут отображаться в списке объектов.
        search_fields (tuple): Поля, по которым можно выполнять поиск в админ-панели.
        list_filter (tuple): Поля, по которым можно фильтровать объекты в админ-панели.
        readonly_fields (tuple): Поля, доступные только для чтения в форме редактирования объекта.
        filter_horizontal (tuple): Поля, для которых будет использоваться горизонтальный фильтр.
    """

    list_display = ('id', 'user', 'created_at', 'content_excerpt', 'liked_by_users')
    search_fields = ('content',)
    list_filter = ('created_at', 'user')
    readonly_fields = ('created_at',)
    filter_horizontal = ('liked_by',)

    def liked_by_users(self, obj: Post) -> str:
        """
        Возвращает строку с именами пользователей, которые отметили пост как понравившийся.

        Args:
            obj (Post): Экземпляр модели Post, для которого возвращаются имена пользователей.

        Returns:
            str: Строка с именами пользователей, которые отметили пост как понравившийся.
        """
        return ", ".join([user.username for user in obj.liked_by.all()])[:50]

    liked_by_users.short_description = 'Liked By'

    def content_excerpt(self, obj: Post) -> str:
        """
        Возвращает обрезанный фрагмент содержания поста.

        Args:
            obj (Post): Экземпляр модели Post, для которого возвращается фрагмент содержания.

        Returns:
            str: Обрезанный фрагмент содержания поста.
        """
        return f"{obj.content[:47]}..."

    content_excerpt.short_description = 'Content Excerpt'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """
    Конфигурация админки для модели Comment.

    Этот класс определяет, как объекты модели Comment будут отображаться и управляться в админ-панели Django.

    Attributes:
        list_display (tuple): Поля модели Comment, которые будут отображаться в списке объектов.
        search_fields (tuple): Поля, по которым можно выполнять поиск в админ-панели.
        list_filter (tuple): Поля, по которым можно фильтровать объекты в админ-панели.
        readonly_fields (tuple): Поля, доступные только для чтения в форме редактирования объекта.
    """

    list_display = ('id', 'post', 'user', 'created_at', 'content_excerpt')
    search_fields = ('content',)
    list_filter = ('created_at', 'post', 'user')
    readonly_fields = ('created_at',)

    def content_excerpt(self, obj):
        """
        Возвращает обрезанный фрагмент содержания комментария.

        Args:
            obj (Comment): Экземпляр модели Comment, для которого возвращается фрагмент содержания.

        Returns:
            str: Обрезанный фрагмент содержания комментария.
        """
        return f"{obj.content[:47]}..."

    content_excerpt.short_description = 'Content Excerpt'
