from django.shortcuts import render
from .models import Item



def item_list(request):
    context = {
        'items' : Item.objects.all()
    }
    print(Item.objects.all())
    return render(request, "home-page.html", context)
