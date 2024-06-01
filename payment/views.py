from decimal import Decimal
import uuid
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.template.loader import render_to_string
from django.templatetags.static import static
from django.contrib.admin.views.decorators import staff_member_required
import stripe
import weasyprint
from yookassa import Configuration, Payment
from cart.cart import Cart

from .forms import ShippingAddressForm
from .models import Order, OrderItem, ShippingAddress

from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.api_version = settings.STRIPE_API_VERSION

Configuration.account_id = settings.YOOKASSA_SHOP_ID
Configuration.secret_key = settings.YOOKASSA_SECRET_KEY


@login_required(login_url='account:login')
def shipping(request):
    try:
        shipping_address = ShippingAddress.objects.get(user=request.user)
    except ShippingAddress.DoesNotExist:
        shipping_address = None

    form = ShippingAddressForm(instance=shipping_address)

    if request.method == 'POST':
        form = ShippingAddressForm(request.POST, instance=shipping_address)
        if form.is_valid():
            shipping_address = form.save(commit=False)
            shipping_address.user = request.user
            shipping_address.save()
            return redirect('account:dashboard')
    return render(request, 'payment/shipping.html', {'form': form})


def checkout(request):
    if request.user.is_authenticated:
        shipping_address = get_object_or_404(
            ShippingAddress, user=request.user)
        if shipping_address:
            return render(request, 'payment/checkout.html', {'shipping_address': shipping_address})
    return render(request, 'payment/checkout.html')


def complete_order(request):
    if request.method == 'POST':
        payment_type = request.POST.get('stripe-payment', 'yookassa-payment')

        name = request.POST.get('name')
        email = request.POST.get('email')
        street_address = request.POST.get('street_address')
        apartment_address = request.POST.get('apartment_address')
        city = request.POST.get('city')
        country = request.POST.get('country')
        zipcode = request.POST.get('zipcode')
        cart = Cart(request)
        total_price = cart.get_total_price()

        shipping_address, _ = ShippingAddress.objects.get_or_create(
            user=request.user,
            defaults={
                'full_name': name,
                'email': email,
                'street_address': street_address,
                'apartment_address': apartment_address,
                'city': city,
                'country': country,
                'zipcode': zipcode
            }
        )

        match payment_type:
            case 'stripe-payment':

                session_data = {
                    'mode': 'payment',
                    'success_url': request.build_absolute_uri(reverse_lazy('payment:payment-success')),
                    'cancel_url': request.build_absolute_uri(reverse_lazy('payment:payment-failed')),
                    'line_items': [],
                    'shipping': {
                        'name': name,
                        'address': {
                            'line1': street_address,
                            'city': city,
                            'country': country,
                            'postal_code': zipcode
                        }
                    },
                }

                if request.user.is_authenticated:
                    order = Order.objects.create(
                        user=request.user,
                        shipping_address=shipping_address,
                        amount=total_price
                    )
                    for item in cart:
                        OrderItem.objects.create(
                            order=order,
                            product=item['product'],
                            price=item['price'],
                            quantity=item['qty'],
                            user=request.user
                        )

                        session_data['line_items'].append({
                            'price_data': {
                                'currency': 'usd',
                                'unit_amount': int(item['price'] * Decimal(100)),
                                'product_data': {
                                    'name': item['product']
                                }
                            },
                            'quantity': item['qty']
                        })
                    session_data['client_reference_id'] = str(order.id)
                    session = stripe.checkout.Session.create(
                        **session_data)
                    return redirect(session.url, code=303)
                else:
                    order = Order.objects.create(
                        shipping_address=shipping_address,
                        amount=total_price
                    )
                    for item in cart:
                        OrderItem.objects.create(
                            order=order,
                            product=item['product'],
                            price=item['price'],
                            quantity=item['qty'],
                        )

                        session_data['line_items'].append({
                            'price_data': {
                                'currency': 'usd',
                                'unit_amount': int(item['price'] * Decimal(100)),
                                'product_data': {
                                    'name': item['product']
                                }
                            },
                            'quantity': item['qty']
                        })
                    session_data['client_reference_id'] = str(order.id)
                    session = stripe.checkout.Session.create(
                        **session_data)
                    return redirect(session.url, code=303)

            # Yookassa
            case 'yookassa-payment':
                idempotence_key = uuid.uuid4()
                currency = 'RUB'
                description = 'Оплата заказа'
                payment = Payment.create({
                    'amount': {
                        'value': str(total_price * 100),
                        'currency': currency
                    },
                    'confirmation': {
                        'type': 'redirect',
                        'return_url': request.build_absolute_uri(reverse_lazy('payment:payment-success'))
                    },
                    'capture': True,
                    'description': description,
                    'idempotence_key': idempotence_key,
                    'test': True
                })

                confirmation_url = payment.confirmation.confirmation_url

                if request.user.is_authenticated:
                    order = Order.objects.create(
                        user=request.user,
                        shipping_address=shipping_address,
                        amount=total_price
                    )
                    for item in cart:
                        OrderItem.objects.create(
                            order=order,
                            product=item['product'],
                            price=item['price'],
                            quantity=item['qty'],
                            user=request.user
                        )

                    return redirect(confirmation_url)

                else:
                    order = Order.objects.create(
                        shipping_address=shipping_address,
                        amount=total_price
                    )
                    for item in cart:
                        OrderItem.objects.create(
                            order=order,
                            product=item['product'],
                            price=item['price'],
                            quantity=item['qty'],
                        )


def payment_success(request):
    for key in list(request.session.keys()):
        del request.session[key]
    return render(request, 'payment/payment-success.html')


def payment_failed(request):
    return render(request, 'payment/payment-failed.html')


@staff_member_required
def admin_order_pdf(request, order_id):
    try:
        order = Order.objects.select_related(
            'user', 'shipping_address').get(id=order_id)
    except Order.DoesNotExist:
        raise Http404('Order not found')
    html = render_to_string(
        'payment/order/pdf/pdf_invoice.html', {'order': order})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename=order_{order.id}.pdf'
    css_path = static('payment/css/pdf.css').lstrip('/')
    stylesheets = [weasyprint.CSS(css_path)]
    weasyprint.HTML(string=html).write_pdf(response, stylesheets=stylesheets)
    return response
