from django.shortcuts import render, redirect
from django.http import HttpResponse
from carts.models import CartItem
from .forms import OrderForm
from .models import Order, OrderProduct
import datetime
from .models import Payment
from .models import Order
from datetime import datetime as dt
import random
from store.models import Product
from django.template.loader import render_to_string
from django.core.mail import EmailMessage

# Create your views here.



def payment(request):
    return render(request, 'orders/payment.html')

def makePayment(request, order_number):
    
    user =request.user
    order = Order.objects.get(user=user, is_ordered=False, order_number=order_number)
    user_for_id = user.email.split('@')[0]
    now = dt.now()
    current_time1 = now.strftime("%H%M%S")
    current_time2= now.strftime("%S%M%H")
    ran = random.randint(0, 2)
    
    if(ran==1):
        payment_id=current_time1 + user_for_id
    else:
        payment_id=current_time2 + user_for_id

    grand_total= order.order_total
    payment =Payment(
        user=user,
        payment_id=payment_id,
        payment_method="database",
        amount_paid=grand_total,
        status="COMPLETED"
    )
    payment.save()

    order.payment=payment
    order.is_ordered =True
    order.save()


    cart_items = CartItem.objects.filter(user=request.user)
    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.ordered =True
        orderproduct.save()

        cart_item = CartItem.objects.get(id = item.id)
        product_variation = cart_item.variation.all()
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variation.set(product_variation)
        orderproduct.save()

        product = Product.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()
    
    CartItem.objects.filter(user=request.user).delete()
    mail_subject = 'Thank you for your order'
    message = render_to_string('orders/order_recieved_email.html', {
                'user':request.user,
                'order':order
            })
    to_email = request.user.email
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.send()


    payment = Payment.objects.get(user=request.user,payment_id=payment_id)
    order = Order.objects.get(user=request.user, order_number=order_number, is_ordered=True)
    orderproduct = OrderProduct.objects.filter(user=request.user, payment=payment, order=order)
    total =0
    for orderP in orderproduct:
        total+= orderP.quantity * orderP.product_price
        print(total)
    
    yr = int(datetime.date.today().strftime('%Y'))
    dy = int(datetime.date.today().strftime('%d'))
    mt = int(datetime.date.today().strftime('%m'))
    d =datetime.date(yr,mt,dy)
    current_date = d.strftime("%Y%m%d")
    order = Order.objects.filter(user=request.user, order_number=order_number, is_ordered=True)
    
    context={
        'orderproduct':orderproduct,
        'order_number':order_number,
        'payment_id':payment_id,
        'current_date':current_date,
        'order':order,
        'total':total,
    }
    return render(request, 'orders/order_complete.html', context)
    















def place_order(request, total=0, quantity=0):
    current_user = request.user

    cart_items = CartItem.objects.filter(user=current_user)

    cart_count = cart_items.count()

    if cart_count<=0:
        return redirect('store')

    for cart_item in cart_items:
        total+=(cart_item.product.price*cart_item.quantity)
        quantity+=cart_item.quantity
    tax = (2*total)/100
    grand_total = total +tax

    if request.method == "POST":
        form =OrderForm(request.POST)

        if form.is_valid():
            data =Order()
            data.user=current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total =grand_total
            data.tax=tax
            data.ip=request.META.get('REMOTE_ADDR')
            data.save()

            #Generate Order number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d =datetime.date(yr,mt,dt)
            current_date = d.strftime("%Y%m%d")
            order_number = current_date + str(data.id)
            data.order_number =order_number
            data.save()
            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            
            context = {
                'order':order,
                'cart_items':cart_items,
                'total':total,
                'tax':tax,
                'grand_total':grand_total,
            }
            return render(request,'orders/payment.html', context)
        else:
            return redirect('checkout')
            




