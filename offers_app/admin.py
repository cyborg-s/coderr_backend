from django.contrib import admin

from .models import Offer, OfferDetail

class OfferDetailInline(admin.TabularInline):
    model = OfferDetail
    extra = 1  # Anzahl leerer Felder zum Hinzufügen
    readonly_fields = ['id']
    show_change_link = True

@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'user', 'calculated_min_price', 'calculated_min_delivery_time', 'created_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['title', 'description', 'user__username']
    inlines = [OfferDetailInline]
    readonly_fields = ['created_at', 'updated_at']

@admin.register(OfferDetail)
class OfferDetailAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'offer', 'offer_type', 'price', 'delivery_time_in_days']
    list_filter = ['offer_type']
    search_fields = ['title', 'offer__title']
