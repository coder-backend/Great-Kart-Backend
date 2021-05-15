from django.shortcuts import get_object_or_404, render, redirect, get_list_or_404
from .form import RegistrationForm, UserForm, UserProfileForm
from .models import Account, UserProfile
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.utils.encoding import force_text
from orders.models import OrderProduct, Order
from carts.models import Cart, CartItem
from carts.views import _cart_item
import requests

from django.core.exceptions import ObjectDoesNotExist
# Create your views here.


def register(request):

    if request.method=="POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split("@")[0]
            user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username, password=password)
            user.save()

            #USER ACTIVATION
            current_site = get_current_site(request)
            mail_subject = 'Please activate your account'
            message = render_to_string('accounts/account_verification_email.html', {
                'user':user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            # messages.success(request, 'Please check you email and verify it')
            return redirect('/accounts/login/?command=verification&email='+email)

    else:
        form = RegistrationForm()
    context={
        'form':form,
    }
    return render(request, 'accounts/register.html', context)


def login(request):
    if request.method =='POST':
        email = request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(email=email, password=password)
  
        if user is not None:

            try:
                cart = Cart.objects.get(cart_id=_cart_item(request))
                is_cart_Item = CartItem.objects.filter(cart=cart).exists()
                if is_cart_Item:
                    cart_item = CartItem.objects.filter(cart=cart)
                    product_variation=[]

                    for item in cart_item:
                        variation = item.variation.all()
                        product_variation.append(list(variation))
                    
                    cart_item = CartItem.objects.filter(user=user)
                    ex_var_list =[]
                    id=[]
                    for item in cart_item:
                        existing_variation = item.variation.all()
                        ex_var_list.append(list(existing_variation))
                        id.append(item.id)
                    
                    for pr in product_variation:
                        if pr in ex_var_list:
                            index = ex_var_list.index(pr)
                            item_id= id[index]
                            item =CartItem.objects.get(id=item_id)
                            item.quantity+=1
                            item.user=user
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user = user
                                item.save()
            except:
                pass

            
            auth.login(request, user)
            messages.success(request, 'You are now looged in')
            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                params =dict(x.split('=') for x in query.split('&'))

                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)
            except:
                return redirect('dashboard')
        else:
            messages.error(request, 'Invalid Login')
            return redirect('login')

    return render(request, 'accounts/login.html')


@login_required(login_url = 'login')
def logout(request):
    auth.logout(request)
    messages.success(request, "You are sucessfully logout")
    return redirect('login')



def activate(request,uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user=None
    
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations! your account is activated')
        return redirect('login')
    else:
        messages.error(request, "Invalid activation link")
        return redirect('register')
         



@login_required(login_url = 'login')
def dashboard(request):
    try:
        orders = Order.objects.order_by('-created_at').filter(user_id = request.user.id, is_ordered= True)
        orders_count = orders.count()
    except ObjectDoesNotExist:
        orders_count = 0
    userprofileExist = UserProfile.objects.filter(user_id= request.user.id).exists()
    if userprofileExist:
        userprofile = UserProfile.objects.get(user_id= request.user.id)
        imgurl = userprofile.profile_picture.url
    
    else:
        imgurl = "https://www.w3schools.com/howto/img_avatar.png"
    context={
            'orders_count': orders_count,
            "imgurl":imgurl,
        }
    return render(request, 'accounts/dashboard.html', context)


def forgetPassword(request):
    if request.method=="POST":
        print("Insite GEt")
        email =  request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)
            current_site = get_current_site(request)
            mail_subject = 'Reset Password'
            message = render_to_string('accounts/reset_password_email.html', {
                'user':user,
                'domain': current_site,
                'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            messages.success(request, "Password reset emial has been sent to your email address.")
            return redirect('login')
        else:
            messages.error(request, "Account Does not exist!")
            return redirect('forgetPassword')


    return render(request, 'accounts/forgetPassword.html')


def resetpassword_validate(request, uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user=None
    
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, "Please reset your password")
        return redirect('resetPassword')
    else:
        messages.error(request, 'This link has been expired!')
        return redirect('login')
    

def resetPassword(request):
    if request.method == "POST":
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password==confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset sucessfully')
            return redirect('login')
        else:
            messages.error(request, 'Password do not match!')
            return redirect('resetPassword')
    else:
        return render(request, 'accounts/resetPassword.html')

@login_required(login_url='login')
def my_orders(request):
    orders = Order.objects.filter(user = request.user, is_ordered = True).order_by('-created_at')
    context = {
        'orders':orders,

    }
    return render(request, 'accounts/my_orders.html', context)



@login_required(login_url='login')
def edit_profile(request):
    userprofile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance = request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance = userprofile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your Profile has been updated. ')
            return redirect('edit_profile')
    else:
        user_form = UserForm(instance = request.user)
        profile_form = UserProfileForm(instance =userprofile)
    
    context={
        'user_form':user_form,
        'profile_form': profile_form,
        'userprofile':userprofile,
    }
    return render(request, 'accounts/edit_profile.html', context)



@login_required(login_url='login')
def change_password(request):
    if request.method == "POST":
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        if confirm_password == new_password:
            user = Account.objects.get(username__exact = request.user.username)
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                messages.success(request, "Your Password is updated Successfully")
                return redirect('change_password')
            else:
                messages.error(request, "Please Provide correct Password")
                return redirect('change_password')
        else:
            messages.error(request,"Password Doesnot match")
            return redirect('change_password')

    return render(request, 'accounts/change_password.html')


@login_required(login_url='login')
def order_detail(request, order_id):
    order_detail = OrderProduct.objects.filter(order__order_number = order_id)
    order = Order.objects.filter(order_number = order_id)
    subtotal = 0
    for i in order_detail:
        subtotal += i.product_price * i.quantity
    context =  {
        'order_detail': order_detail,
        'order':order,
        'subtotal':subtotal,
    }

    return render(request, 'accounts/order_detail.html', context)