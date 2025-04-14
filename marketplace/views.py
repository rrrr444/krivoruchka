from django.core.checks import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .models import Product, Cart, Order, OrderItem, Review, User, Notification
from .forms import (ProductForm, ReviewForm, ProfileForm,
                    OrderForm, CustomUserCreationForm, ShippingForm)
from django.contrib import messages
def home(request):
    products = Product.objects.order_by('-rating')
    query = request.GET.get('q')
    if query:
        products = products.filter(name__icontains=query) | products.filter(description__icontains=query)
    return render(request, 'marketplace/home.html', {'products': products})

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'marketplace/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'marketplace/login.html', {'form': form})


@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            return redirect('product_detail', pk=pk)
    else:
        form = ReviewForm()
    return render(request, 'marketplace/product_detail.html', {
        'product': product,
        'form': form
    })

@login_required
def cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    total = sum(item.product.price * item.quantity for item in cart_items)
    return render(request, 'marketplace/cart.html', {
        'cart_items': cart_items,
        'total': total
    })

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={'quantity': 1}
    )
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('cart')

@login_required
def remove_from_cart(request, cart_id):
    cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)
    cart_item.delete()
    return redirect('cart')

@login_required
def checkout(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.total_price = sum(item.product.price * item.quantity for item in request.user.cart_set.all())
            order.save()
            for item in request.user.cart_set.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity
                )
            request.user.cart_set.all().delete()
            return redirect('orders')
    else:
        form = OrderForm()
    return render(request, 'marketplace/checkout.html', {'form': form})

@login_required
def orders(request):
    user_orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'marketplace/orders.html', {'orders': user_orders})

@login_required
def update_cart(request, cart_id, action):
    cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)
    if action == 'increase':
        cart_item.quantity += 1
    elif action == 'decrease' and cart_item.quantity > 1:
        cart_item.quantity -= 1
    cart_item.save()
    return redirect('cart')


from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import ProfileForm


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=request.user)

    return render(request, 'marketplace/edit_profile.html', {'form': form})

@login_required
def complete_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.status == 'shipped':
        order.status = 'completed'
        order.save()
    return redirect('orders')

@login_required
def ship_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    # Проверяем что текущий пользователь - продавец товара в заказе
    if any(item.product.seller == request.user for item in order.items.all()):
        order.status = 'shipped'
        order.save()
    return redirect('seller_orders')

@login_required
def seller_orders(request):
    # Все заказы, где есть товары текущего пользователя
    orders = Order.objects.filter(
        items__product__seller=request.user
    ).distinct().order_by('-created_at')
    return render(request, 'marketplace/seller_orders.html', {'orders': orders})

@login_required
def profile(request):
    user_products = Product.objects.filter(seller=request.user)
    return render(request, 'marketplace/profile.html', {
        'user_products': user_products
    })
from .decorators import profile_complete_required
from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import redirect

def custom_logout(request):
    logout(request)
    messages.success(request, "Вы успешно вышли из системы")
    return redirect('home')

@login_required
@profile_complete_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()
            messages.success(request, 'Товар успешно добавлен!')
            return redirect('profile')
    else:
        form = ProductForm()
    return render(request, 'marketplace/add_product.html', {'form': form})

@login_required
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk, seller=request.user)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Товар успешно обновлен!')
            return redirect('profile')
    else:
        form = ProductForm(instance=product)
    return render(request, 'marketplace/edit_product.html', {'form': form})
@login_required
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk, seller=request.user)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Товар успешно удалён!')
        return redirect('profile')
    return render(request, 'marketplace/delete_product.html', {'product': product})
def base_context(request):
    if request.user.is_authenticated:
        return {'cart_items_count': Cart.objects.filter(user=request.user).count()}
    return {}

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'marketplace/order_history.html', {'orders': orders})


@login_required
def confirm_receipt(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.status != 'shipped':
        messages.error(request, 'Нельзя подтвердить неотправленный заказ')
        return redirect('order_history')

    if request.method == 'POST':
        order.status = 'completed'
        order.save()
        messages.success(request, 'Заказ успешно подтвержден')
        return redirect('order_history')

    return render(request, 'marketplace/confirm_receipt.html', {'order': order})


from django.db.models import Q


@login_required
def seller_orders(request):
    # Заказы где есть товары текущего пользователя
    orders = Order.objects.filter(
        items__product__seller=request.user
    ).distinct().order_by('-created_at')

    return render(request, 'marketplace/seller_orders.html', {'orders': orders})

from django.db.models import Q


@login_required
def mark_order_shipped(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    # Проверка что пользователь - продавец в этом заказе
    if not order.items.filter(product__seller=request.user).exists():
        raise PermissionDenied

    if request.method == 'POST':
        form = ShippingForm(request.POST, instance=order)
        if form.is_valid():
            order = form.save(commit=False)
            order.status = 'shipped'
            order.save()

            # Уведомление для покупателя
            Notification.objects.create(
                user=order.user,
                message=f"Ваш заказ #{order.id} был отправлен. Трек-номер: {order.tracking_number}",
                order=order
            )

            messages.success(request, 'Заказ успешно помечен как отправленный')
            return redirect('seller_orders')
    else:
        form = ShippingForm(instance=order)

    return render(request, 'marketplace/mark_shipped.html', {
        'order': order,
        'form': form
    })


@login_required
def notifications(request):
    notifications = request.user.notifications.all()
    # Помечаем как прочитанные при просмотре
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return render(request, 'marketplace/notifications.html', {'notifications': notifications})


@login_required
def checkout(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.total_price = sum(item.product.price * item.quantity for item in request.user.cart_set.all())
            order.save()

            # Переносим товары в заказ
            for item in request.user.cart_set.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    seller=item.product.seller
                )

                # Уведомление для продавца
                Notification.objects.create(
                    user=item.product.seller,
                    message=f"Новый заказ #{order.id} на ваш товар {item.product.name}",
                    order=order
                )

            # Очищаем корзину
            request.user.cart_set.all().delete()

            messages.success(request, 'Заказ успешно оформлен!')
            return redirect('order_history')
    else:
        form = OrderForm(initial={'address': request.user.address})

    return render(request, 'marketplace/checkout.html', {'form': form})\

@login_required
def mark_all_notifications_read(request):
    request.user.notifications.filter(is_read=False).update(is_read=True)
    messages.success(request, "Все уведомления помечены как прочитанные")
    return redirect('notifications')


@login_required
def sales_list(request):
    sales = Order.objects.filter(product__seller=request.user)
    return render(request, 'marketplace/sales_list.html', {'sales': sales})
from django.contrib.auth.decorators import login_required
from .models import Order, OrderItem


@login_required
def seller_orders(request):
    # Получаем все OrderItem, где текущий пользователь - продавец
    order_items = OrderItem.objects.filter(
        seller=request.user
    ).select_related('order', 'product')

    # Собираем уникальные заказы
    orders = Order.objects.filter(
        id__in=[item.order_id for item in order_items]
    ).prefetch_related('order_items__product')

    return render(request, 'marketplace/seller_orders.html', {
        'orders': orders,
        'current_user': request.user
    })

@login_required
def buyer_orders(request):
    orders = Order.objects.filter(buyer=request.user)
    return render(request, 'marketplace/buyer_orders.html', {'orders': orders})


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Order


@login_required
def sales_list(request):
    """Список продаж для продавца"""
    sales = Order.objects.filter(product__seller=request.user).select_related('product', 'buyer')
    return render(request, 'marketplace/sales_list.html', {'sales': sales})


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Order


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order.objects.prefetch_related('order_items__product'), id=order_id)
    return render(request, 'marketplace/order_detail.html', {'order': order})


@login_required
def confirm_shipment(request, order_id):
    order = get_object_or_404(Order.objects.prefetch_related('order_items'), id=order_id)

    # Проверяем, является ли пользователь продавцом любого из товаров в заказе
    is_seller = any(request.user == item.seller for item in order.order_items.all())

    if not is_seller:
        messages.error(request, "У вас нет прав для подтверждения отправки этого заказа")
        return redirect('seller_orders')

    if order.status != Order.PENDING:
        messages.error(request, "Заказ уже обработан")
        return redirect('seller_orders')

    if request.method == 'POST':
        order.status = Order.SHIPPED
        order.tracking_number = request.POST.get('tracking_number', '')
        order.save()

        # Здесь можно добавить создание уведомления для покупателя
        messages.success(request, "Заказ успешно помечен как отправленный")
        return redirect('seller_orders')

    return render(request, 'marketplace/confirm_shipment.html', {'order': order})


@login_required
def confirm_delivery(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.status != Order.SHIPPED:
        messages.error(request, "Можно подтвердить только отправленные заказы")
        return redirect('order_detail', order_id=order.id)

    if request.method == 'POST':
        order.status = Order.DELIVERED
        order.save()
        messages.success(request, "Получение заказа подтверждено!")
        return redirect('order_detail', order_id=order.id)

    return render(request, 'marketplace/confirm_delivery.html', {'order': order})