from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import redirect


@login_required
def custom_login_redirect(request: HttpRequest) -> HttpResponseRedirect:
    """Перенаправляет пользователя на страницу с его постами."""
    user = request.user
    return redirect("posts:home", pk=user.pk)
