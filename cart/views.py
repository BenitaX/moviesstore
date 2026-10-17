from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from movies.models import Movie
from .utils import calculate_cart_total
from .models import Order, Item, User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum
from django.contrib import admin

admin_required = user_passes_test(lambda u: 
                                  u.is_authenticated and u.is_superuser)

def index(request):
    cart_total = 0
    movies_in_cart = []
    cart = request.session.get('cart', {})
    movie_ids = list(cart.keys())
    if (movie_ids != []):
        movies_in_cart = Movie.objects.filter(id__in=movie_ids)
        cart_total = calculate_cart_total(cart, movies_in_cart)

    template_data = {}
    template_data['title'] = 'Cart'
    template_data['movies_in_cart'] = movies_in_cart
    template_data['cart_total'] = cart_total
    return render(request, 'cart/index.html', {'template_data': template_data})

def add(request, id):
    get_object_or_404(Movie, id=id)
    cart = request.session.get('cart', {})
    cart[id] = request.POST['quantity']
    request.session['cart'] = cart
    return redirect('cart.index')

def clear(request):
    request.session['cart'] = {}
    return redirect('cart.index')

@login_required
def purchase(request):
    cart = request.session.get('cart', {})
    movie_ids = list(cart.keys())

    if (movie_ids == []):
        return redirect('cart.index')
    
    movies_in_cart = Movie.objects.filter(id__in=movie_ids)
    cart_total = calculate_cart_total(cart, movies_in_cart)

    order = Order()
    order.user = request.user
    order.total = cart_total
    order.save()

    for movie in movies_in_cart:
        item = Item()
        item.movie = movie
        item.price = movie.price
        item.order = order
        item.quantity = cart[str(movie.id)]
        item.save()

    request.session['cart'] = {}
    template_data = {}
    template_data['title'] = 'Purchase confirmation'
    template_data['order_id'] = order.id
    return render(request, 'cart/purchase.html', 
                  {'template_data': template_data})

@admin_required
def topcustomer(request):
    customer = (User.objects
                    .annotate(total_items=Sum("order__item__quantity"))
                    .order_by("-total_items")
                    .first()
                )

    template_data = {}
    template_data['customer_name'] = customer.username
    template_data['item_count'] = customer.total_items
    template_data['user'] = customer

    context = {
        **admin.site.each_context(request), 
        'template_data': template_data,
    }

    return render(request, 'cart/admin_topcustomer.html',
                  context)

# from django.contrib.auth import get_user_model

# User = get_user_model()  # works with custom user models too

# # All field objects
# for field in User._meta.get_fields():
#     print(field.name, type(field).__name__)