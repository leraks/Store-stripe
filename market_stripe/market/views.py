from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import Item, Customer
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY
domain = "http://127.0.0.1:8000"


# Страница со всеми товарами
def all_products(request):
    item = Item.objects.all()
    context = {"item": item}
    return render(request, "market/page_products.html", context)


# Карточка продукта с описаниеме и картинкой
def card_product(request, pk):
    item = Item.objects.get(id=pk)
    context = {"item": item}
    return render(request, "market/card_product.html", context)


# Страница с пояснением о моей не доробоке )) связанная с корзиной
def order_info(request):
    context = {}
    return render(request, "market/order_info.html", context)


# Функция для добавление товара
@login_required(login_url='order_info')
def order_add(request, pk):
    if request.user is not None:
        item = Item.objects.get(id=pk)
        customer = Customer.objects.get(user=request.user)
        customer.order.items.add(item)
    return redirect('products')


# Функция для удаления товара
@login_required(login_url='order_info')
def order_remove(request, pk):
    if request.user is not None:
        item = Item.objects.get(id=pk)
        customer = Customer.objects.get(user=request.user)
        customer.order.items.remove(item)
    return redirect(domain)


# Карзина
@login_required(login_url='order_info')
def order(request):
    try:
        customer = Customer.objects.get(user=request.user)
        orders = customer.order.items.all()
        final_sum = 0
        for s in orders:
            final_sum += s.price / 100
        context = {'orders': orders, 'final_sum': final_sum}
        return render(request, "market/order.html", context)
    except Exception:
        return redirect('products')


# Страница не удачной покупки
def cancel(request):
    context = {}
    return render(request, "market/cancel.html", context)


# Страница успешной покупки
def success(request, pk):
    try:
        session = stripe.checkout.Session.retrieve(pk)
        try:
            if session.metadata['orders'] == "True":
                customer = Customer.objects.get(user=request.user)
                customer.order.items.clear()
        except Exception as e:
            print(str(e))

        if session.payment_status == "paid":
            context = {}
            return render(request, "market/success.html", context)
        else:
            return redirect('products')

    except Exception:
        return redirect('products')


# Покупка товара из корзины stripe
def create_checkout_session_oders(request):
    domain = str(request.scheme) + "://" + str(request.get_host())
    if request.method == "POST":
        try:
            customer = Customer.objects.get(user=request.user)
            orders = customer.order.items.all()

            items = []
            for ord in orders:
                items.append({'price_data': {'currency': 'usd', 'unit_amount': ord.price,
                                             'product_data': {
                                                 'name': ord.name
                                             }}, 'quantity': 1})

            checkout_session = stripe.checkout.Session.create(

                line_items=items,
                mode='payment',

                metadata={
                    "orders": True
                },

                success_url=domain + '/success/{CHECKOUT_SESSION_ID}',
                cancel_url=domain + '/cancel',
            )
        except Exception as e:
            return str(e)

        return redirect(checkout_session.url, code=303)

    else:
        return redirect('products')


# Покупка товара stripe
def create_checkout_session(request, pk):
    domain = str(request.scheme) + "://" + str(request.get_host())
    if request.method == "POST":
        try:
            item = Item.objects.get(id=pk)

            checkout_session = stripe.checkout.Session.create(
                line_items=[
                    {
                        'price_data': {
                            'currency': 'usd',
                            'unit_amount': item.price,
                            'product_data': {
                                'name': item.name,
                            }
                        },
                        'quantity': 1,

                    },
                ],
                metadata={
                    "product_id": item.id
                },
                mode='payment',
                success_url=domain + '/success/{CHECKOUT_SESSION_ID}',
                cancel_url=domain + '/cancel',
            )
        except Exception as e:
            return str(e)

        return redirect(checkout_session.url, code=303)

    else:
        return redirect('products')


# Вебхук
@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        customer_email = session["customer_details"]["email"]
        payment_intent = session["payment_intent"]
        product_id = session["metadata"]["product_id"]
        order = session["metadata"]["orders"]

    return HttpResponse(status=200)
