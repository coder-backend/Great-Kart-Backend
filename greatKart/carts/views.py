from django.shortcuts import render, redirect, get_object_or_404

from store.models import Product, Variation
from .models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist

from django.http import HttpResponse



#create a session key

def _cart_item(request):
    cart =  request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


#add_cart functionality
def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    product_variation = []
    if request.method == 'POST': #check wheather the request is POST or not
        for item in request.POST:
            key= item
            value = request.POST[key]

            try:
                # This will check whether the provided variation exist on database or not
                variation = Variation.objects.get(product = product,variation_category__iexact=key, variation_value__iexact=value) 
                product_variation.append(variation)
                
            except:
                pass
    
    try:
        cart = Cart.objects.get(cart_id = _cart_item(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id = _cart_item(request)
        )
    cart.save()
    #return true or flase based on existance
    is_cart_item_exist = CartItem.objects.filter(product=product, cart=cart).exists()

    if is_cart_item_exist:
        cart_item = CartItem.objects.filter(product=product, cart=cart) 
        #if the cartItem already exist for the product we want to add
        # we will filter it out from database
        exist_variation_list = [] # we will store all the variation of color and size for the given products here                                      
        id=[] # to store id of all the CartItem contains
        for item in cart_item:
            exist_variation = item.variation.all() # it will reture all the variation for the given product in the CartItem
            exist_variation_list.append(list(exist_variation)) # Query set to list
            id.append(item.id) #It will append the id of every variation list
        
        if product_variation in exist_variation_list: #if the current variation for the certain product exist already
            index = exist_variation_list.index(product_variation) # It will give me the index where my variation is store
            item_id = id[index] # It will return the id of the CartItem's certain Product having product_variation variation
            item = CartItem.objects.get(product=product, id= item_id) #using this Id I will find the Product I need to upgrade
            item.quantity+=1
            item.save()
        else:
            item = CartItem.objects.create(product=product, quantity=1, cart=cart) # if the product_variation variation doesnotexist already we will create a new one with quantity 1            
            if len(product_variation)>0: 
                item.variation.clear()
                item.variation.add(*product_variation)
            item.save()
    else:
        cart_item= CartItem.objects.create(
            product=product,
            quantity=1,
            cart=cart
        )
        if len(product_variation)>0:
            cart_item.variation.clear()
            cart_item.variation.add(*product_variation)
        cart_item.save() 
    return redirect("cart") 


def remove_cart(request, product_id, cart_item_id):
    cart = Cart.objects.get(cart_id = _cart_item(request))
    product = get_object_or_404(Product, id=product_id)
    try:
        cart_item = CartItem.objects.get(product = product, cart=cart, id=cart_item_id)
        if cart_item.quantity>1:
            cart_item.quantity-=1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart')




def remove_cart_item(request, product_id, cart_item_id):
    cart = Cart.objects.get(cart_id = _cart_item(request))
    product = get_object_or_404(Product, id=product_id)
    try:
        cart_item = CartItem.objects.get(product = product, cart=cart, id=cart_item_id)
        cart_item.delete()
    except:
        pass
    return redirect('cart')


def cart(request, total=0, quantity=0, cart_items=None):
    tax=0
    grand_total=0
    try:
        cart = Cart.objects.get(cart_id= _cart_item(request))
        cart_items = CartItem.objects.filter(cart =cart, is_active=True)

        for cart_item in cart_items:
            total+=(cart_item.product.price * cart_item.quantity)
            quantity+=cart_item.quantity
        tax= (2*total)/100
        grand_total = total+tax
    except ObjectDoesNotExist:
        pass

    context={
        'grand_total':grand_total,
        'tax':tax,
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
    }
    
    return render(request, 'store/cart.html', context)


def checkout(request,total=0, quantity=0, cart_items=None):
    tax=0
    grand_total=0
    try:
        cart = Cart.objects.get(cart_id= _cart_item(request))
        cart_items = CartItem.objects.filter(cart =cart, is_active=True)

        for cart_item in cart_items:
            total+=(cart_item.product.price * cart_item.quantity)
            quantity+=cart_item.quantity
        tax= (2*total)/100
        grand_total = total+tax
    except ObjectDoesNotExist:
        pass

    context={
        'grand_total':grand_total,
        'tax':tax,
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
    }
    return render(request, 'store/checkout.html', context)