from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import View

from accounts.models import CustomUser, Subscription
from posts.forms import CommentForm, PostForm
from posts.models import Post


class HomeView(View):
    """
    Представление для отображения домашней страницы пользователя, включая посты, комментарии и подписки.

    Этот класс обрабатывает отображение и обработку запросов на домашней странице пользователя,
    включая создание постов, комментариев, лайков и подписок.
    """

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Обрабатывает GET-запрос для отображения страницы пользователя.

        Этот метод извлекает информацию о постах пользователя, его подписках и проверяет, подписан ли
        текущий пользователь на данного пользователя. Затем передает эту информацию в контекст и рендерит
        HTML-шаблон для отображения страницы.

        Args:
            request (HttpRequest): Объект запроса, содержащий данные о текущем запросе.
            *args: Дополнительные позиционные аргументы.
            **kwargs: Дополнительные именованные аргументы.

        Returns:
            HttpResponse: Ответ с отрендеренной страницей пользователя.
        """
        user_of_posts = get_object_or_404(CustomUser, pk=kwargs.get("pk"))
        subscriptions = Subscription.objects.filter(
            follower=user_of_posts
        ).select_related("following")
        posts = (
            Post.objects.filter(user=user_of_posts)
            .select_related("user")
            .prefetch_related("comments")
            .prefetch_related("comments__user")
            .prefetch_related("liked_by")
            .order_by("-created_at")
        )
        if request.user.is_authenticated:
            user_of_posts_in_followers = request.user.is_following(user_of_posts)
        else:
            user_of_posts_in_followers = False
        context = {
            "user_of_posts": user_of_posts,
            "posts": posts,
            "subscriptions": subscriptions,
            "user_of_posts_in_followers": user_of_posts_in_followers,
        }
        return render(request, "posts/home.html", context)

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponseRedirect:
        """
        Обрабатывает POST-запросы для создания постов, комментариев, лайков и подписок.

        Этот метод обрабатывает различные действия, отправленные через POST-запросы, такие как:
            - создание нового поста или комментария,
            - добавление или удаление лайков,
            - подписка или отписка от пользователя.

        Args:
            request (HttpRequest): Объект запроса, содержащий данные о текущем запросе.
            *args: Дополнительные позиционные аргументы.
            **kwargs: Дополнительные именованные аргументы.

        Returns:
            HttpResponseRedirect: Перенаправляет на страницу с постами после выполнения действия.
        """
        if "new-post" in request.POST:
            post_form = PostForm(request.POST)
            if post_form.is_valid():
                post = post_form.save(commit=False)
                post.user = request.user
                post.save()
                return redirect(reverse("posts:home", kwargs={"pk": kwargs.get("pk")}))

        if "new-comment" in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                post_pk = request.POST.get("post-pk")
                post = get_object_or_404(Post, pk=post_pk)
                comment = comment_form.save(commit=False)
                comment.post = post
                comment.user = request.user
                comment.save()
                return redirect(reverse("posts:home", kwargs={"pk": kwargs.get("pk")}))

        if "like-post" in request.POST:
            post_pk = request.POST.get("post-pk")
            post = get_object_or_404(Post, pk=post_pk)
            if request.user in post.liked_by.all():
                post.liked_by.remove(request.user)
            else:
                post.liked_by.add(request.user)

        if "subscribe" in request.POST:
            user_of_posts = get_object_or_404(CustomUser, pk=kwargs.get("pk"))
            if request.user.is_following(user_of_posts):
                request.user.unfollow(user_of_posts)
            else:
                request.user.follow(user_of_posts)

        return redirect(reverse("posts:home", kwargs={"pk": kwargs.get("pk")}))
