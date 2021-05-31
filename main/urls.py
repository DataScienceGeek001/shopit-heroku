from django.urls import path
from . import views

from django.conf.urls import url

from .views import *

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    ###############  FRONTEND URLS ###############

    path('', views.home, name='home'),
    path('search', views.search, name='search'),
    path('category-list', views.category_list, name='category-list'),
    path('brand-list', views.brand_list, name='brand-list'),
    path('product-list', views.product_list, name='product-list'),
    path('category-product-list/<int:cat_id>', views.category_product_list, name='category-product-list'),
    path('brand-product-list/<int:brand_id>', views.brand_product_list, name='brand-product-list'),
    path('product/<str:slug>/<int:id>', views.product_detail, name='product-detail'),
    path("filter-data", views.filter_data, name="filter_data"),
    path("addToFavourite-<int:id>", views.add_to_favourite, name="addToFavourite"),
    
    
    ###############  CART URLS ################
    
    path("add-to-cart-<int:pro_id>/", AddToCartView.as_view(), name="addtocart"),
    path("my-cart/", MyCartView.as_view(), name="mycart"),
    path("manage-cart/<int:cp_id>", ManageCartView.as_view(), name="managecart"),
    path("empty-cart/", EmptyCartView.as_view(), name="emptycart"),
    path("checkout/", CheckoutView.as_view(), name="checkout"),
    path("razorpay-request/", RazorpayRequestView.as_view(), name="razorpayrequest"),
    path('success' , views.success , name='success'),
    

    ################ CUSTOMER URLS ################
    
    path("register/",
         CustomerRegistrationView.as_view(), name="customerregistration"),
    path("logout/", CustomerLogoutView.as_view(), name="customerlogout"),
    path("login/", CustomerLoginView.as_view(), name="customerlogin"),
    path("profile-<int:id>", CustomerProfileView.as_view(), name="customerprofile"),
    path('forgot-password', PasswordForgotView.as_view(), name="passwordforgot"),
    path("password-reset/<email>/<token>/", PasswordResetView.as_view(), name="passwordreset"),


    ################ REST URLS #################

    url(r'^products/$', views.product_rest_list),


    ################ ADMIN URLS #################
    
    ##### ADMIN HOME #####
    path("admin-home/", AdminHomeView.as_view(), name="adminhome"),
    
    ##### ADMIN READ URLS #####    
    path('admin-product-list', AdminProductListView.as_view(), name="adminProductList"),
    path('admin-brand-list', AdminBrandListView.as_view(), name="adminBrandList"),
    path('admin-category-list', AdminCategoryListView.as_view(), name="adminCategoryList"),
    path('admin-user-list', AdminUserListView.as_view(), name="adminUserList"),
    path("admin-order-list", AdminOrderListView.as_view(), name="adminOrderList"),
    path("admin-order-details/<int:ord_id>", AdminOrderDetails.as_view(), name="adminOrderDetails"),
    path("admin-color-list", AdminColorListView.as_view(), name="adminColorList"),
    path("admin-size-list", AdminSizeListView.as_view(), name="adminSizeList"),
    path("admin-pattr-list-<int:prod_id>", AdminProdcutAttributesView.as_view(), name="adminPattr"),

    ##### ADMIN CREATE URLS #####
    path('admin-add-product', AddProductView.as_view(), name='addProduct'),
    path('admin-add-product-attribute', AddProductAttributeView.as_view(), name='addProductAttribute'),
    path('admin-add-brand', AddBrandView.as_view(), name='addBrand'),
    path('admin-add-category', AddCategoryView.as_view(), name='addCategory'),
    path('admin-add-user', AddCustomerView.as_view(), name='addCustomer'),
    path('admin-add-color', AddColorView.as_view(), name='addColor'),
    path('admin-add-size', AddSizeView.as_view(), name="addSize"),

    ##### ADMIN EDIT URLS #####
    path("admin-edit-product-<int:pk>", ProductUpdateView.as_view(), name="productUpdate"),
    path("admin-edit-brand-<int:pk>", BrandUpdateView.as_view(), name="brandUpdate"),
    path("admin-edit-category-<int:pk>", CategoryUpdateView.as_view(), name="categoryUpdate"),
    path("admin-edit-user-<int:pk>", UserUpdateView.as_view(), name="userUpdate"),
    path('admin-order-status-change-<int:ord_id>', AdminOrderStatusChange.as_view(), name='adminOrderStatusChange'),
    path('admin-edit-color-<int:pk>', ColorUpdateView.as_view(), name="colorUpdate"),
    path('admin-edit-size-<int:pk>', SizeUpdateView.as_view(), name="sizeUpdate"),
    path('admin-edit-pattr=<int:pk>', ProductAttrUpdateView.as_view(), name="pattrUpdate"),

    ##### ADMIN DELETE URLS #####
    path("delete-product/<int:prod_id>", DeleteProduct.as_view(), name="deleteproduct"),
    path("delete-brand/<int:brand_id>", DeleteBrand.as_view(), name="deletebrand"),
    path("delete-category/<int:cat_id>", DeleteCategory.as_view(), name="deletecategory"),
    path("delete-customer/<int:cust_id>", DeleteCustomer.as_view(), name="deletecustomer"),
    path("delete-order/<int:ord_id>", DeleteOrder.as_view(), name="deleteorder"),
    path("delete-color/<int:col_id>", DeleteColor.as_view(), name="deletecolor"),
    path("delete-size/<int:size_id>", DeleteSize.as_view(), name="deletesize"),
    path("delete-pattr/<int:pattr_id>", DeleteProductAttribute.as_view(), name="deletepattr"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)