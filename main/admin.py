from django.contrib import admin

# Register your models here.
from .models import Category, Brand, Color, Size, Product, ProductAttribute, Banner

from .models import *

admin.site.register([Customer, Cart, CartProduct, Order])

admin.site.register(Size)

class BannerAdmin(admin.ModelAdmin):
    list_display = ('alt_text', 'image_tag')
admin.site.register(Banner, BannerAdmin)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'image_tag')
admin.site.register(Category, CategoryAdmin)

class BrandAdmin(admin.ModelAdmin):
    list_display = ('title', 'image_tag')
admin.site.register(Brand, BrandAdmin)

class ColorAdmin(admin.ModelAdmin):
    list_display = ('title', 'color_bg')
admin.site.register(Color, ColorAdmin)

class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'brand', 'price', 'status', 'is_featured')
    list_editable = ('status', 'is_featured')
admin.site.register(Product, ProductAdmin)

class ProductAttributeAdmin(admin.ModelAdmin):
    list_display = ('id', 'image_tag', 'product', 'color', 'size')
admin.site.register(ProductAttribute, ProductAttributeAdmin)