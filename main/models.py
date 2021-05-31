from django.db import models
from django.utils.html import mark_safe
from django.contrib.auth.models import User

# Customer Model
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=200)
    address = models.CharField(max_length=200, null=True, blank=True)
    joined_on = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Customers'

    def __str__(self):
        return self.full_name

# Banner Model
class Banner(models.Model):
    img = models.ImageField(upload_to='banner_imgs/')
    alt_text = models.CharField(max_length=300)

    class Meta:
        verbose_name_plural = '1. Banners'

    def image_tag(self):
        return mark_safe('<img src="%s" width="130" height="50" />' % (self.img.url))

    def __str__(self):
        return self.alt_text

# Category Model
class Category(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to="cat_imgs/")

    class Meta:
        verbose_name_plural = '2. Categories'

    def image_tag(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url))

    def __str__(self):
        return self.title

# Brand Model
class Brand(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to="brand_imgs/")

    class Meta:
        verbose_name_plural = '3. Brands'

    def image_tag(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url))

    def __str__(self):
        return self.title

# Color Model
class Color(models.Model):
    title = models.CharField(max_length=100)
    color_code = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = '4. Colors'

    def color_bg(self):
        return mark_safe('<div style="width:40px; height:20px; background:%s"></div>' % (self.color_code))
    
    def __str__(self):
        return self.title

# Size Model
class Size(models.Model):
    title = models.CharField(max_length=100)
    
    class Meta:
        verbose_name_plural = '5. Sizes'

    def __str__(self):
        return self.title

# Product Model
class Product(models.Model):
    title = models.CharField(max_length=200)
    slug = models.CharField(max_length=400)
    details = models.TextField()
    specs = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    status = models.BooleanField(default=True)
    price = models.PositiveIntegerField(null=True)
    is_featured = models.BooleanField(default=False)
    favorite = models.ManyToManyField(Customer, blank=True)

    class Meta:
        verbose_name_plural = '6. Products'

    def __str__(self):
        return self.title

# Product Attributes Model
class ProductAttribute(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    color = models.ForeignKey(Color, on_delete=models.CASCADE)
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="product_imgs/", null=True)

    class Meta:
        verbose_name_plural = '7. ProductAttributes'

    def image_tag(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url))

    def __str__(self):
        return self.product.title

# Cart Model
class Cart(models.Model):
    customer = models.ForeignKey(
        Customer, on_delete=models.SET_NULL, null=True, blank=True)
    total = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = '8. Cart'

    def __str__(self):
        return "Cart: " + str(self.id)

# Cart Product Model
class CartProduct(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rate = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField()
    subtotal = models.PositiveIntegerField()

    class Meta:
        verbose_name_plural = '9. Cart Products'

    def __str__(self):
        return "Cart: " + str(self.cart.id) + " CartProduct: " + str(self.id)


ORDER_STATUS = (
    ("Order Received", "Order Received"),
    ("Order Processing", "Order Processing"),
    ("On the way", "On the way"),
    ("Order Completed", "Order Completed"),
    ("Order Canceled", "Order Canceled"),
)

METHOD = (
    ("Cash On Delivery", "Cash On Delivery"),
    ("Razorpay", "Razorpay")
)

# Order Model
class Order(models.Model):
    cart = models.OneToOneField(Cart, on_delete=models.CASCADE)
    ordered_by = models.CharField(max_length=200)
    shipping_address = models.CharField(max_length=200)
    mobile = models.CharField(max_length=10)
    email = models.EmailField(null=True, blank=True)
    subtotal = models.PositiveIntegerField()
    discount = models.PositiveIntegerField()
    total = models.PositiveIntegerField()
    order_status = models.CharField(max_length=50, choices=ORDER_STATUS)
    created_at = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=20, choices=METHOD, default="Cash On Delivery")
    payment_completed = models.BooleanField(default=False)

    def __str__(self):
        return "Order: " + str(self.id)

