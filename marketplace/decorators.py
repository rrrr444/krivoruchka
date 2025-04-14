from django.conf import settings
from django.shortcuts import redirect

def profile_complete_required(view_func):
    def wrapper(request, *args, **kwargs):
        user = request.user
        if not all(getattr(user, field) for field in settings.PROFILE_REQUIRED_FIELDS):
            from django.contrib import messages
            messages.warning(request, 'Заполните профиль полностью перед добавлением товаров')
            return redirect('edit_profile')
        return view_func(request, *args, **kwargs)
    return wrapper