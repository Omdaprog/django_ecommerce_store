from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, View
from .models import Item, Order, OrderItem, Adress, Payment, Coupon, Refund
from django.utils import timezone
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CheckoutForm, CouponForm, RefundForm, SendMail
import random
import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))


def is_valid_form(value):
    valid = True
    for field in value:
        if field == '':
            valid = False
    return valid


class CheckoutView(View):
    def get(self, *args, **kwargs):
        try:
            print(self.request.user)
            order = Order.objects.get(user=self.request.user, ordered = False)
            # form
            form = CheckoutForm()  
            context = {
            'form': form ,
            'order':order,
            'couponform':CouponForm(),
            'DISPLAY_COUPON_FORM': False
            }
            shippin_address_qd = Adress.objects.filter(
                user=self.request.user,
                adress_type='S',
                default = True
            )

            if shippin_address_qd.exists():
                context.update({'default_shipping_adress': shippin_address_qd[0]})

            billing_address_qd = Adress.objects.filter(
                user=self.request.user,
                adress_type='B',
                default = True
            )

            if billing_address_qd.exists():
                context.update({'default_billing_adress': billing_address_qd[0]})

            return render(self.request, "checkout-page.html", context)
        except ObjectDoesNotExist:
            messages.info(self.request, "You do not have an active order")
            return redirect("core:checkout")
        
        

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():

                use_default_shipping = form.cleaned_data.get(
                    'use_default_shipping')
                if use_default_shipping:
                    print("Using the defualt shipping adress")
                    adress_qs = Adress.objects.filter(
                        user=self.request.user,
                        adress_type = 'S',
                        default=True,
                    )
                    if adress_qs.exists():
                        shipping_adress = adress_qs[0]
                        order.shipping_adress = shipping_adress
                        order.save()
                    else:
                        messages.info(self.request, "No default shipping address available")
                        return redirect('core:checkout')
                else:
                    print("User is entering a new shipping address")

                    shipping_adress1 = form.cleaned_data.get('shipping_adress')
                    shipping_adress2 = form.cleaned_data.get('shipping_adress2')
                    shipping_country = form.cleaned_data.get('shipping_country')
                    shipping_zip = form.cleaned_data.get('shipping_zip')

                    if is_valid_form([shipping_adress1, shipping_adress2, shipping_country, shipping_zip]):

                        shipping_adress = Adress(
                            user=self.request.user,
                            street_adress=shipping_adress1,
                            apartment_adress=shipping_adress2,
                            country=shipping_country,
                            zip=shipping_zip,
                            adress_type = 'S'
                        )
                        shipping_adress.save()

                        order.shipping_adress = shipping_adress
                        order.save()
                        set_default_shipping = form.cleaned_data.get('set_default_shipping')
                        if set_default_shipping:
                            shipping_adress.default = True
                            shipping_adress.save()
                    else:
                        messages.info(self.request, "Please fill in the required shipping adress fields")




                use_default_billing = form.cleaned_data.get(
                    'use_default_billing')

                same_billing_adress = form.cleaned_data.get(
                    'same_billing_adress')
                
                if same_billing_adress:
                    billing_adress = shipping_adress
                    billing_adress.pk = None  # To Clone billing_adress from  shipping_adress
                    billing_adress.save()     #
                    billing_adress.adress_type = 'B'
                    billing_adress.save()
                    order.billing_adress = billing_adress
                    order.save()

                elif use_default_billing:
                    print("Using the defualt billing adress")
                    adress_qs = Adress.objects.filter(
                        user=self.request.user,
                        adress_type = 'B',
                        default=True,
                    )
                    if adress_qs.exists():
                        billing_adress = adress_qs[0]
                        order.billing_adress = billing_adress
                        order.save()
                    else:
                        messages.info(self.request, "No default billing address available")
                        return redirect('core:checkout')
                else:
                    print("User is entering a new shipping address")

                    billing_adress1 = form.cleaned_data.get('billing_adress')
                    billing_adress2 = form.cleaned_data.get('billing_adress2')
                    billing_country = form.cleaned_data.get('billing_country')
                    billing_zip = form.cleaned_data.get('shipping_zip')

                    if is_valid_form([billing_adress1, billing_adress2, billing_country, billing_zip]):

                        billing_adress = Adress(
                            user=self.request.user,
                            street_adress=billing_adress1,
                            apartment_adress=billing_adress2,
                            country=billing_country,
                            zip=billing_zip,
                            adress_type = 'B'
                        )
                        billing_adress.save()

                        order.billing_adress = billing_adress
                        order.save()
                        set_default_billing = form.cleaned_data.get('set_default_billing')

                        if set_default_billing:
                            billing_adress.default = True
                            billing_adress.save()
                    else:
                        messages.info(self.request, "Please fill in the required billing adress fields")
                
                payment_option = form.cleaned_data.get('payment_option')
                if payment_option == 'S':
                    return redirect('core:payment', payment_option = 'stripe')
                elif payment_option == 'P':
                    return redirect('core:payment', payment_option = 'paypal')
                else:
                    messages.warning(
                        self.request, "Invalid payment option selected")
                    return redirect('core:checkout')

        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("core:order-summary")


class ItemDetailView(DetailView):
    model = Item
    template_name = "product-page.html"


class PaymentView(View):
    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        if order.billing_adress:
            context = {
                'order':order,
                'DISPLAY_COUPON_FORM': False
            }
            return render(self.request, "payment.html", context)
        else:
            messages.warning(self.request, "you have not added a billing adress")
            return redirect("core:checkout")

    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        token = self.request.POST.get('stripeToken')
        amount = int(order.get_total() * 100)  # cents

        try:
            charge = stripe.Charge.create(
                amount=amount,
                currency="usd",
                source=token,
            )
            # Create the payment
            payment = Payment()
            # TODO: assigned code 
            order.ref_code = create_ref_code()
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = order.get_total()
            payment.save()
            

            # assign the payment to the order
            order_item = order.items.all()
            order_item.update(ordered=True)
            for item in order_item:
                item.save()
            
            order.ordered = True
            order.payment = payment
            order.save()
            messages.success(self.request, "Your order was successful!")
            return redirect("/")
        except stripe.error.CardError as e:
            # Since it's a decline, stripe.error.CardError will be caught
            body = e.jason_body
            err = body.get('error', {})
            messages.warning(self.request, f"{err.get('message')}") 
            return redirect("/")
        except stripe.error.RateLimitError as e:
                # Too many requests made to the API too quickly
            messages.warning(self.request, "Rate limit error") 
            return redirect("/")
        except stripe.error.InvalidRequestError as e:
                # Invalid parameters were supplied to Stripe's API
            messages.warning(self.request, "Invalid parametres") 
            return redirect("/")
        except stripe.error.AuthenticationError as e:
                # Authentication with Stripe's API failed
                # (maybe you changed API keys recently)
            messages.warning(self.request, "Not athenticated") 
            return redirect("/")
        except stripe.error.APIConnectionError as e:
                # Network communication with Stripe failed
            messages.warning(self.request, "Network error") 
            return redirect("/")
        except stripe.error.StripeError as e:
                # Display a very generic error to the user, and maybe send
                # yourself an email
            messages.warning(self.request, "Something went wrong. You were ot charged. Please try again.") 
            return redirect("/")
        except Exception as e:
                # send an email to ourselves
            messages.warning(self.request, "A serious error occurred . we have been notifed") 
            return redirect("/")


        

        

class HomeView(ListView):
    model = Item
    paginate_by = 10
    template_name = "home-page.html"

    def get(self, *args, **kwargs):
        form = SendMail()   
        context = {
            'form': form
        }
        return render(self.request,"home-page.html", context)
    def post(self, *args, **kwargs):
        form = SendMail(self.request.POST)   
        if form.is_valid():
            print(form.cleaned_data)
        return redirect("core:home") 

    


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            form = CouponForm()
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order,
                'couponform':form,
                'DISPLAY_COUPON_FORM': True
            }
            return render(self.request, 'order_summary.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("/")


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )

    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item quantity was updated.")
        else:
            order.items.add(order_item)
            messages.info(request, "This item was add to your cart.")
            return redirect("core:order-summary")

    else:
        order_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=order_date
        )
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart.")
        return redirect("core:order-summary")

    return redirect("core:order-summary")


@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            order_item.delete()
            messages.info(request, "This item was removed from your cart")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("core:order-summary")
    else:
        messages.info(request, "You do not have an active order")
        return redirect("core:product", slug=slug)

    return redirect("core:product", slug=slug)


@login_required
def remove_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "This item quantity was updated")
            return redirect("core:order-summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("core:order-summary", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("core:order-summary", slug=slug)

    return redirect("core:order-summary", slug=slug)


def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        messages.info(request, "You do not have an active order")
        return redirect("core:checkout")


class AddCouponView(View):
    def post(self, *args,**kwargs):
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(user=self.request.user, ordered = False)
                order.coupon = get_coupon(self.request, code)
                order.save()
                messages.success(self.request, "Successfully added coupon")
                return redirect("core:checkout")
            except ObjectDoesNotExist:
                messages.info(self.request, "You do not have an active order")
                return redirect("core:checkout")
    
class RequestRefundView(View):
    def get(self, *args, **kwargs):
        form = RefundForm()
        context = {
            'form': form
        }
        return render(self.request,"request_refund.html",context)
    def post(self, *args, **kwargs):
        form = RefundForm(self.request.POST)
        if form.is_valid():
            ref_code = form.cleaned_data.get('ref_code')
            message = form.cleaned_data.get('message')
            email = form.cleaned_data.get('email')
            #edit the order
            try:
                order = Order.objects.get(ref_code=ref_code)
                order.refund_requested = True
                order.save()

                # Store the refund
                refund = Refund()
                refund.order = order
                refund.reason = message
                refund.email = email
                refund.save()
                
                messages.info(self.request, "Your request was receved.")
                return redirect("core:request-refund")

            except ObjectDoesNotExist:
                messages.info(self.request, "This order does not exist.")
                return redirect("core:request-refund")


