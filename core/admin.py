from django.contrib import admin

from .models import Item , OrderItem , Order,Payment, Coupon, Refund, Adress




def make_refund_accepted(ModelAdmin, request, queryset):
    queryset.update(refund_requested=False, refund_granted= True)

make_refund_accepted.short_description = 'Update orders to refund granted'



class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'ordered',
        'being_delevering',
        'received',
        'refund_requested',
        'refund_granted',
        'billing_adress',
        'Shipping_adress',
        'payment',
        'coupon',]

    list_display_links = [
        'user',
        'billing_adress',
        'Shipping_adress',
        'payment',
        'coupon',
    ]

    list_filter = [
        'ordered',
        'being_delevering',
        'received',
        'refund_requested',
        'refund_granted',]
    search_fields = [
        'user__username',
        'ref_code',
    ]

    actions = [make_refund_accepted]


class AddressAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'street_adress',
        'apartment_adress',
        'country',
        'zip',
        'adress_type',
        'default',
    ]
    list_filter = ['default','adress_type', 'country']
    search_fields = ['user, ''street_adress','apartment_adress','zip']

admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(Order, OrderAdmin)
admin.site.register(Payment)
admin.site.register(Coupon)
admin.site.register(Refund)
admin.site.register(Adress,AddressAdmin)
