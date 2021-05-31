# For Rendering
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy, reverse

# For Authentication
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages

# For Forms and Models
from django.views.generic import View, TemplateView, CreateView, FormView, ListView, UpdateView
from django.db.models import Max, Min, Count
from .models import *
from .forms import *

# For Password Reset
from .utils import password_reset_token
from django.core.mail import send_mail
from django.conf import settings

# For Payment
from django.views.decorators.csrf import csrf_exempt
import razorpay

# REST FRAMEWORK TESTING
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from .main_serializer import ProductSerializer

''' ''' ''' REST FRAMEWORK ''' ''' '''

# Displaying data using REST Framework
class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)

def product_rest_list(request):
    if request.method == 'GET':
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return JSONResponse(serializer.data)


''' ''' ''' MIXIN VIEWS ''' ''' '''

# Mixin for customer authentication
class EcomMixin(object):
    def dispatch(self, request, *args, **kwargs):
        cart_id = request.session.get("cart_id")
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            if request.user.is_authenticated and request.user.customer:
                cart_obj.customer = request.user.customer
                cart_obj.save()
        return super().dispatch(request, *args, **kwargs)

# Mixin for Admin authentication
class AdminRequiredMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_superuser:
            pass
        else:
            return redirect("/login/")
        return super().dispatch(request, *args, **kwargs)


''' ''' ''' FRONTEND VIEWS ''' ''' '''

# Customer Home
def home(request):
    banners = Banner.objects.all().order_by('-id')
    data = Product.objects.filter(is_featured=True).order_by('-id')
    return render(request, 'index.html', {'data': data, 'banners': banners})

# Category View
def category_list(request):
    data = Category.objects.all().order_by('-id')
    return render(request, 'category_list.html', {'data': data})

# Brand View
def brand_list(request):
    brands = Brand.objects.all().order_by('-id')
    return render(request, 'brand_list.html', {'brands': brands})

# Product List View
def product_list(request):
    data = Product.objects.all().order_by('-id')
    return render(request, 'product_list.html', 
                {
                    'data': data,
                })

# Category Based product views
def category_product_list(request, cat_id):
    category = Category.objects.get(id=cat_id)
    data = Product.objects.filter(category=category).order_by('-id')
    return render(request, 'category_product_list.html', {
            'data': data, 
            })

# Brand based product Views
def brand_product_list(request, brand_id):
    brand = Brand.objects.get(id=brand_id)
    data = Product.objects.filter(brand=brand).order_by('-id')
    return render(request, 'category_product_list.html', {
            'data': data,
            })

# Product Detail View
def product_detail(request, slug, id):
    product = Product.objects.get(id=id)
    related_products = Product.objects.filter(category=product.category).exclude(id=id)[:3]
    return render(request, 'product_detail.html', {'data': product, 'related': related_products})

# Search View
def search(request):
    q = request.GET['q']
    data = Product.objects.filter(title__icontains=q).order_by('-id')
    return render(request, 'search.html', {'data': data})

# Filtering Data
def filter_data(request):
    colors = request.GET.getlist('color[]')
    categories = request.GET.getlist('category[]')
    brands = request.GET.getlist('brand[]')
    sizes = request.GET.getlist('size[]')
    allProducts=Product.objects.all().order_by('-id').distinct()
    
    if len(colors) > 0:
        allProducts = allProducts.filter(productattribute__color__id__in=colors).distinct()

    if len(categories) > 0:
        allProducts = allProducts.filter(category__id__in=categories).distinct()

    if len(brands) > 0:
        allProducts = allProducts.filter(brand__id__in=brands).distinct()

    if len(sizes) > 0:
        allProducts = allProducts.filter(productattribute__size__id__in=sizes).distinct()

    t = render_to_string('ajax/product-list.html', {'data': allProducts})
    
    return JsonResponse({'data': t})


''' ''' ''' CART VIEWS  ''' ''' '''

# Add to Cart View
@method_decorator(login_required(login_url="/login/"), name='dispatch')
class AddToCartView(EcomMixin, TemplateView):
    template_name = "cart/addtocart.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # get product id from requested url
        product_id = self.kwargs['pro_id']
        # get product
        product_obj = Product.objects.get(id=product_id)
        # print(product_obj.price)
        # check if cart exists
        cart_id = self.request.session.get("cart_id", None)
        print(cart_id)
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            this_product_in_cart = cart_obj.cartproduct_set.filter(
                product=product_obj)

            # item already exists in cart
            if this_product_in_cart.exists():
                cartproduct = this_product_in_cart.last()
                cartproduct.quantity += 1
                cartproduct.subtotal += product_obj.price
                cartproduct.save()
                cart_obj.total += product_obj.price
                cart_obj.save()
                messages.success(self.request, 'Product Added to cart successfully!')
            # new item is added in cart
            else:
                cartproduct = CartProduct.objects.create(
                    cart=cart_obj, product=product_obj, rate=product_obj.price, quantity=1, subtotal=product_obj.price)
                cart_obj.total += product_obj.price
                cart_obj.save()
                messages.success(self.request, 'Product Added to cart successfully!')

        else:
            cart_obj = Cart.objects.create(total=0)
            self.request.session['cart_id'] = cart_obj.id
            cartproduct = CartProduct.objects.create(
                cart=cart_obj, product=product_obj, rate=product_obj.price, quantity=1, subtotal=product_obj.price)
            cart_obj.total += product_obj.price
            cart_obj.save()
            messages.success(self.request, 'Product Added to cart successfully!')

        return context


# Cart View
class MyCartView(EcomMixin, TemplateView):
    template_name = "cart/mycart.html"

    # @login_required(login_url='/login')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_id = self.request.session.get("cart_id", None)
        if cart_id:
            cart = Cart.objects.get(id=cart_id)
        else:
            cart = None
        context['cart'] = cart
        return context

# Manage Cart View
class ManageCartView(EcomMixin, View):
    def get(self, request, *args, **kwargs):
        print("This is Manage Cart Section")
        cp_id = self.kwargs["cp_id"]
        action = request.GET.get("action")
        cp_obj = CartProduct.objects.get(id=cp_id)
        cart_obj = cp_obj.cart

        if action == 'inc':
            cp_obj.quantity += 1
            cp_obj.subtotal += cp_obj.rate
            cp_obj.save()
            cart_obj.total += cp_obj.rate
            cart_obj.save()
        elif action == 'dcr':
            cp_obj.quantity -= 1
            cp_obj.subtotal -= cp_obj.rate
            cp_obj.save()
            cart_obj.total -= cp_obj.rate
            cart_obj.save()
            if cp_obj.quantity == 0:
                cp_obj.delete()
        elif action == 'rmv':
            cart_obj.total -= cp_obj.subtotal
            cart_obj.save()
            cp_obj.delete()
        else:
            pass

        return redirect("mycart")

# Empty Cart View
class EmptyCartView(EcomMixin, View):
    def get(self, request, *args, **kwargs):
        cart_id = request.session.get("cart_id", None)
        if cart_id:
            cart = Cart.objects.get(id=cart_id)
            cart.cartproduct_set.all().delete()
            cart.total = 0
            cart.save()
        return redirect("mycart")

# Cart Checkout View
class CheckoutView(EcomMixin, CreateView):
    template_name = "cart/checkout.html"
    form_class = CheckoutForm
    success_url = '/'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.customer:
            pass
        else:
            return redirect("/login/?next=/checkout/")
        return super().dispatch(request, *args, **kwargs)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_id = self.request.session.get("cart_id", None)
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
        else:
            cart_obj = None
        
        context['cart'] = cart_obj
        return context

    def form_valid(self, form):
        cart_id = self.request.session.get("cart_id")
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            form.instance.cart = cart_obj
            form.instance.subtotal = cart_obj.total
            form.instance.discount = 0
            form.instance.total = cart_obj.total
            form.instance.order_status = "Order Received"
            del self.request.session['cart_id']
            pm = form.cleaned_data.get("payment_method")
            order = form.save()
            if pm == "Razorpay":
                return redirect(reverse("razorpayrequest") + "?o_id=" + str(order.id))

        else:
            return redirect("home")
        return super().form_valid(form)

# Razorpay request view
class RazorpayRequestView(View):
    def get(self, request, *args, **kwargs):
        o_id = request.GET.get("o_id")
        order = Order.objects.get(id=o_id)
        client = razorpay.Client(
            auth=("rzp_test_ejxwUwJ32rcHr9", "NyZiMrNZQSE6yHStcTvTo63a"))

        payment = client.order.create({'amount': order.total, 'currency': 'INR', 'payment_capture': '1'})
        context = {
            "order": order 
        }
        return context

# Customer Payment Success View
@csrf_exempt
def success(request):
    # del request.session['cart_id']
    return render(request, "success.html")


''' ''' ''' CUSTOMER VIEWS ''' ''' '''

# Customer Registration View
class CustomerRegistrationView(EcomMixin, CreateView):
    template_name = "customer/customerregistration.html"
    form_class = CustomerRegistrationForm
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        email = form.cleaned_data.get("email")
        user = User.objects.create_user(username, email, password)
        form.instance.user = user
        login(self.request, user)
        return super().form_valid(form)

    def get_success_url(self):
        if "next" in self.request.GET:
            next_url = self.request.GET.get("next")
            return next_url
        else:
            return self.success_url

# Customer Logout View
class CustomerLogoutView(EcomMixin, View):
    def get(self, request):
        logout(request)
        return redirect("home")

# Customer Login View
class CustomerLoginView(EcomMixin, FormView):
    template_name = "customer/customerlogin.html"
    form_class = CustomerLoginForm
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        uname = form.cleaned_data.get("username")
        pword = form.cleaned_data["password"]
        usr = authenticate(username=uname, password=pword)
        if usr is None:
            return render(self.request, self.template_name, {"form": self.form_class, "error": "Invalid credentials"})
        if usr.is_superuser:
            login(self.request, usr)
            return redirect("adminhome")
        if usr is not None and Customer.objects.filter(user=usr).exists():
            login(self.request, usr)
        else:
            return render(self.request, self.template_name, {"form": self.form_class, "error": "Invalid credentials"})

        return super().form_valid(form)

    def get_success_url(self):
        if "next" in self.request.GET:
            next_url = self.request.GET.get("next")
            return next_url
        else:
            return self.success_url

# Customer Profile View
class CustomerProfileView(TemplateView):
    template_name = "customer/customerprofile.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and Customer.objects.filter(user=request.user).exists():
            pass
        else:
            return redirect("/login/?next=/profile/")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer = self.request.user.customer
        context['customer'] = customer
        orders = Order.objects.filter(cart__customer=customer).order_by("-id")
        context["orders"] = orders
        favorites = Product.objects.filter(favorite=customer)
        context["favorites"] = favorites
        return context

# Add to Favorite View
@login_required(login_url='/login/')
def add_to_favourite(request, id):
    # print(id)
    product = get_object_or_404(Product, id=id)
    if product.favorite.filter(id=request.user.customer.id).exists():
        print(request.user.customer)
        product.favorite.remove(request.user.customer)
    else:
        product.favorite.add(request.user.customer)
    return HttpResponseRedirect(request.META['HTTP_REFERER'])

# Customer Password Forgot View
class PasswordForgotView(FormView):
    template_name = "customer/forgotpassword.html"
    form_class = PasswordForgotForm
    success_url = "/login/"

    def form_valid(self, form):
        # get email from user
        email = form.cleaned_data.get("email")
        # get current host ip/domain
        url = self.request.META['HTTP_HOST']
        # get customer and then user
        customer = Customer.objects.get(user__email=email)
        user = customer.user
        # send mail to the user with email
        text_content = 'Please Click the link below to reset your password. '
        html_content = url + "/password-reset/" + email + \
            "/" + password_reset_token.make_token(user) + "/"
        send_mail(
            'Password Reset Link | Django Ecommerce',
            text_content + html_content,
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )
        return super().form_valid(form)

# Customer Password Reset View
class PasswordResetView(FormView):
    template_name = "customer/passwordreset.html"
    form_class = PasswordResetForm
    success_url = "/login/"

    def dispatch(self, request, *args, **kwargs):
        email = self.kwargs.get("email")
        user = User.objects.get(email=email)
        token = self.kwargs.get("token")
        if user is not None and password_reset_token.check_token(user, token):
            pass
        else:
            return redirect(reverse("passwordforgot"))

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        password = form.cleaned_data['new_password']
        email = self.kwargs.get("email")
        user = User.objects.get(email=email)
        user.set_password(password)
        user.save()
        return super().form_valid(form)



''' ''' ''' ADMIN VIEWS ''' ''' '''

# Admin Home View
class AdminHomeView(AdminRequiredMixin, TemplateView):
    template_name = "admin/adminhome2.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['customers'] = Customer.objects.all()
        context['products'] = Product.objects.all()
        context['brands'] = Brand.objects.all()
        context['categorys'] = Category.objects.all()
        context['orders'] = Order.objects.all()
        context["pendingorders"] = Order.objects.filter(order_status="Order Received").order_by("-id")
        return context

# Admin Delete Customer View
class DeleteCustomer(AdminRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        user_id = self.kwargs["cust_id"]
        user_obj = User.objects.get(id=user_id)
        if user_obj:
            user_obj.delete()
        else:
            pass
        return HttpResponseRedirect(request.META['HTTP_REFERER'])

# Admin Delete Product View
class DeleteProduct(AdminRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        prod_id = self.kwargs["prod_id"]
        prod_obj = Product.objects.get(id=prod_id)
        if prod_obj:
            prod_obj.delete()
        else:
            pass
        return HttpResponseRedirect(request.META['HTTP_REFERER'])

# Admin Delete Brand View
class DeleteBrand(AdminRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        brand_id = self.kwargs["brand_id"]
        brand_obj = Brand.objects.get(id=brand_id)
        if brand_obj:
            brand_obj.delete()
        else:
            pass
        return HttpResponseRedirect(request.META['HTTP_REFERER'])

# Admin Delete Category View
class DeleteCategory(AdminRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        cat_id = self.kwargs["cat_id"]
        cat_obj = Category.objects.get(id=cat_id)
        if cat_obj:
            cat_obj.delete()
        else:
            pass
        return HttpResponseRedirect(request.META['HTTP_REFERER'])

# Admin Delete Order View
class DeleteOrder(AdminRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        ord_id = self.kwargs["ord_id"]
        ord_obj = Order.objects.get(id=ord_id)
        if ord_obj:
            ord_obj.delete()
        else:
            pass
        return HttpResponseRedirect(request.META['HTTP_REFERER'])

# Admin Delete Color View
class DeleteColor(AdminRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        col_id = self.kwargs["col_id"]
        col_obj = Color.objects.get(id=col_id)
        if col_obj:
            col_obj.delete()
        else:
            pass
        return HttpResponseRedirect(request.META['HTTP_REFERER'])

# Admin Delete Size View
class DeleteSize(AdminRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        size_id = self.kwargs["size_id"]
        size_obj = Size.objects.get(id=size_id)
        if size_obj:
            size_obj.delete()
        else:
            pass
        return HttpResponseRedirect(request.META['HTTP_REFERER'])


#############  ADMIN ORDER VIEWS #############

# Admin Order Details
class AdminOrderDetails(AdminRequiredMixin, TemplateView):
    template_name = "admin/adminOrderDetails.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_id = self.kwargs["ord_id"]
        order_obj = Order.objects.get(id=order_id)
        context['order'] = order_obj
        context['statuses'] = ORDER_STATUS
        return context

# Admin Order List
class AdminOrderListView(AdminRequiredMixin, ListView):
    template_name = "admin/adminorderlist.html"
    queryset = Order.objects.all().order_by("-id")
    context_object_name = "allorders"
    # paginate_by = 3

# Admin Order Status Change
class AdminOrderStatusChange(AdminRequiredMixin, View):
    
    def post(self, request, *args, **kwargs):
        ord_id = self.kwargs['ord_id']
        ord_obj = Order.objects.get(id=ord_id)
        new_status = request.POST.get('status')
        ord_obj.order_status = new_status
        ord_obj.save()
        return HttpResponseRedirect(request.META['HTTP_REFERER'])



#############  ADMIN PRODUCT VIEWS #############

# Admin Add Product View
class AddProductView(AdminRequiredMixin, FormView):
    template_name = "admin/addProducts.html"
    form_class = ProductAddForm
    success_url = "admin-product-list"

    def form_valid(self, form):
        title = form.cleaned_data.get("title")
        slug = form.cleaned_data.get("slug")
        details = form.cleaned_data.get("details")
        specs = form.cleaned_data.get("specs")
        category = form.cleaned_data.get("category")
        brand = form.cleaned_data.get("brand")
        price = form.cleaned_data.get("price")
        is_featured = form.cleaned_data.get("is_featured")
        
        form.save()
        
        return super().form_valid(form)

# Admin Add Product Attribute View
class AddProductAttributeView(AdminRequiredMixin, FormView):
    template_name = "admin/addProductAttributes.html"
    form_class = ProductAttributeForm
    success_url = "admin-product-list"

    def form_valid(self, form):
        product = form.cleaned_data.get("product")
        color = form.cleaned_data.get("color")
        size = form.cleaned_data.get("size")
        image = form.cleaned_data.get("image")
        p = ProductAttribute.objects.create(product=product, color=color, size=size, image = image)
        p.save
        return super().form_valid(form)

# Admin Product List View
class AdminProductListView(AdminRequiredMixin, ListView):
    template_name = 'admin/adminProductList.html'
    queryset = Product.objects.all().order_by("-id")
    context_object_name = "products"

#Admin Product Update View
class ProductUpdateView(AdminRequiredMixin, UpdateView):
    template_name = "admin/productUpdateForm.html"
    model = Product
    fields = [
        "title", "slug", "details", "specs", "category", "brand", "price", "is_featured"
    ]
    success_url = "admin-product-list"



#############  ADMIN BRAND VIEWS #############

# Admin Brand List View
class AdminBrandListView(AdminRequiredMixin, ListView):
    template_name = 'admin/adminBrandList.html'
    queryset = Brand.objects.all().order_by("-id")
    context_object_name = "brands"

# Admin Brand Update View
class BrandUpdateView(AdminRequiredMixin, UpdateView):
    template_name = "admin/brandUpdateForm.html"
    model = Brand
    fields = [
        "title", "image"
    ]
    success_url = "admin-brand-list"

# Admin Add Brand View
class AddBrandView(AdminRequiredMixin, FormView):
    template_name = "admin/addBrand.html"
    form_class = BrandAddForm
    success_url = "admin-brand-list"

    def form_valid(self, form):
        title = form.cleaned_data.get("title")
        image = form.cleaned_data.get("image")
        form.save()
        return super().form_valid(form)



#############  ADMIN CATEGORY VIEWS #############

# Admin Category List View
class AdminCategoryListView(AdminRequiredMixin, ListView):
    template_name = 'admin/adminCategoryList.html'
    queryset = Category.objects.all().order_by("-id")
    context_object_name = "categorys"

# Admin Add Category View
class AddCategoryView(AdminRequiredMixin, FormView):
    template_name = "admin/addCategory.html"
    form_class = CategoryAddForm
    success_url = "admin-category-list"

    def form_valid(self, form):
        title = form.cleaned_data.get("title")
        image = form.cleaned_data.get("image")
        form.save()
        return super().form_valid(form)

# Admin Category Update View
class CategoryUpdateView(AdminRequiredMixin, UpdateView):
    template_name = "admin/categoryUpdateForm.html"
    model = Category
    fields = [
        "title", "image"
    ]
    success_url = "admin-category-list"



#############  ADMIN USER VIEWS #############

# Admin User List View
class AdminUserListView(AdminRequiredMixin, ListView):
    template_name = 'admin/adminUserList.html'
    queryset = Customer.objects.all().order_by("-id")
    context_object_name = "customers"

# Admin Add Customer View
class AddCustomerView(AdminRequiredMixin, FormView):
    template_name = "admin/addCustomer.html"
    form_class = CustomerRegistrationForm
    success_url = "admin-user-list"

    def form_valid(self, form):
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        email = form.cleaned_data.get("email")
        user = User.objects.create_user(username, email, password)
        form.instance.user = user
        form.save()
        return super().form_valid(form)

# Admin User Update View
class UserUpdateView(AdminRequiredMixin, UpdateView):
    template_name = "admin/userUpdateForm.html"
    model = Customer
    fields = [
        "full_name", "address"
    ]
    success_url = "admin-user-list"


############## ADMIN COLOR VIEWS ##############

# Admin Color List View
class AdminColorListView(AdminRequiredMixin, ListView):
    template_name = 'admin/adminColorList.html'
    queryset = Color.objects.all().order_by("-id")
    context_object_name = "colors"

# Admin Add Color View
class AddColorView(AdminRequiredMixin, FormView):
    template_name = "admin/addColor.html"
    form_class = ColorAddForm
    success_url = "admin-color-list"

    def form_valid(self, form):
        title = form.cleaned_data.get("title")
        color_code = form.cleaned_data.get("color_code")
        form.save()
        return super().form_valid(form)

# Admin Color Update View
class ColorUpdateView(AdminRequiredMixin, UpdateView):
    template_name = "admin/colorUpdateForm.html"
    model = Color
    fields = [
        "title", "color_code"
    ]
    success_url = "admin-color-list"


############## ADMIN SIZE VIEWS ##############

# Admin Size List View
class AdminSizeListView(AdminRequiredMixin, ListView):
    template_name = 'admin/adminSizeList.html'
    queryset = Size.objects.all().order_by("-id")
    context_object_name = "sizes"

# Admin Add Size View
class AddSizeView(AdminRequiredMixin, FormView):
    template_name = "admin/addSize.html"
    form_class = SizeAddForm
    success_url = "admin-size-list"

    def form_valid(self, form):
        title = form.cleaned_data.get("title")
        form.save()
        return super().form_valid(form)

# Admin Size Update View
class SizeUpdateView(AdminRequiredMixin, UpdateView):
    template_name = "admin/sizeUpdateForm.html"
    model = Size
    fields = [
        "title"
    ]
    success_url = "admin-size-list"


############### ADMIN PRODCUT ATTRIBUTES VIEW ##############

class AdminProdcutAttributesView(AdminRequiredMixin, TemplateView):
    template_name = 'admin/productAttributeList.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        prod_id = self.kwargs['prod_id']
        product = Product.objects.get(id=prod_id)
        data = ProductAttribute.objects.filter(product=product).order_by('-id')
        context["prodAttr"] = data
        return context

class DeleteProductAttribute(AdminRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        pattr_id = self.kwargs["pattr_id"]
        pattr_obj = ProductAttribute.objects.get(id=pattr_id)
        if pattr_obj:
            pattr_obj.delete()
        else:
            pass
        return HttpResponseRedirect(request.META['HTTP_REFERER'])

class ProductAttrUpdateView(AdminRequiredMixin, UpdateView):
    template_name = "admin/pattrUpdateForm.html"
    model = ProductAttribute
    fields = [
        "product", "color", "size", "image"
    ]
    success_url = "admin-product-list"