from django.shortcuts import render, redirect , get_object_or_404
from django.views.generic import ListView, DetailView, View
from .models import Item , Order, OrderItem
from django.utils import timezone
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin



def checkout(request):
    
    return render(request, "checkout-page.html")

class ItemDetailView(DetailView):
    model = Item
    template_name = "product-page.html"


class HomeView(ListView): 
    model = Item
    paginate_by = 10
    template_name = "home-page.html"

class OrderSummaryView(LoginRequiredMixin,View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context={
                'object': order
            }
            return render(self.request, 'order_summary.html',context)
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an active order")
            return redirect("/")

@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item,created = OrderItem.objects.get_or_create(
        item = item ,
        user = request.user,
        ordered = False
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
            messages.info(request,"This item was add to your cart.")
            return redirect("core:order-summary")

    else:
        order_date = timezone.now()
        order = Order.objects.create(
            user=request.user , ordered_date=order_date
        )
        order.items.add(order_item)
        messages.info(request,"This item was added to your cart.")
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
            messages.info(request,"This item was removed from your cart")
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
            if order_item.quantity > 1 :
                order_item.quantity -= 1
                order_item.save() 
            else:
                order.items.remove(order_item) 
            messages.info(request,"This item quantity was updated")
            return redirect("core:order-summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("core:order-summary", slug=slug)  
    else:
        messages.info(request, "You do not have an active order")
        return redirect("core:order-summary", slug=slug)

    return redirect("core:order-summary", slug=slug)














