from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import Product, ProductVariation
from decimal import Decimal
from django.utils import timezone
import json
from django.views.decorators.csrf import csrf_exempt
import random
from bson.decimal128 import Decimal128
from django.shortcuts import redirect, render
from .forms import ExcelUploadForm
import openpyxl


# @csrf_exempt
# def create_or_update_product_variation(request):
#     if request.method == 'POST':
#         try:
#             # Parse the incoming data
#             data = json.loads(request.body)
#             product_name = data.get('product-name')  # Adjusted JSON key
#             variation_text = data.get('variation-text')  # Adjusted JSON key
#             stock = data.get('stock')
#             last_updated = timezone.now()

#             if not product_name or not variation_text:
#                 return JsonResponse({'error': 'Product name and variation text are required'}, status=400)

#             print(f"Received data: {data}")  

#            
#             product, created = Product.objects.get_or_create(
#                 product_name=product_name,
#                 defaults={
#                     'product_lowest_price': Decimal(random.randint(5000, 10000)),
#                     'last_updated': last_updated,
#                 }
#             )

#             if created:
#                 print(f"New product created: {product_name} with lowest price {product.product_lowest_price}")
#             else:
#                 print(f"Product found: {product_name}")

#             # Check if the ProductVariation already exists
#             variation_exists = ProductVariation.objects.filter(product=product, variation_text=variation_text).exists()

#             if variation_exists:
#                 return JsonResponse({'error': 'Variation already exists'}, status=400)

#             # Create the ProductVariation since it doesn't exist
#             ProductVariation.objects.create(
#                 product=product,
#                 variation_text=variation_text,
#                 stock=stock,
#                 last_updated=last_updated
#             )
#             print(f"Variation created for product: {product_name}")  # Debugging statement

#             return JsonResponse({'message': 'Product variation created successfully'}, status=201)

#         except json.JSONDecodeError:
#             return JsonResponse({'error': 'Invalid JSON'}, status=400)
#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=500)
#     else:
#         return JsonResponse({'error': 'Only POST method is allowed'}, status=405)



def get_product_lowest_price(product_lowest_price):
    """
    @purpose: Handles Decimal128 type and converts it to a float for JSON serialization.
    @param: product_lowest_price (Decimal128 or float) - The price of the product.
    @return: (float) - The product price as a float.
    """
    if isinstance(product_lowest_price, Decimal128):
        product_lowest_price = product_lowest_price.to_decimal()
    return float(product_lowest_price)





def get_variations(product_id):
    """
    @purpose: Fetch variations associated with a given product ID.
    @param: product_id (int) - The ID of the product.
    @return: (list) - A list of variations for the product.
    """
    return list(ProductVariation.objects.filter(product_id=product_id).values('variation_text', 'stock', 'last_updated'))






def create_product_dict(product):
    """
    @purpose: Create a dictionary for a product, including its details and associated variations.
    @param: product (dict) - The product data.
    @return: (dict) - A dictionary representing the product and its variations.
    """
    product_dict = {
        'id': product['id'],
        'product_name': product['product_name'],
        'last_updated': product['last_updated'],
        'product_lowest_price': get_product_lowest_price(product['product_lowest_price']),
        'variations': get_variations(product['id']),
    }
    return product_dict





def fetch_all_products():
    """
    @purpose: Fetch all products from the database, including their associated variations.
    @return: (list) - A list of dictionaries, each representing a product and its variations.
    """
    products = Product.objects.all().values('id', 'product_name', 'product_lowest_price', 'last_updated')
    return [create_product_dict(product) for product in products]





def product_list(request):
    """
    @purpose: Handle the list of products and paginate the results for display.
    @param: request (HttpRequest) - The request object containing query parameters.
    @return: (JsonResponse) - A paginated list of products in JSON format.
    """
    products_list = fetch_all_products()

    paginator = Paginator(products_list, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return JsonResponse(list(page_obj), safe=False)






def handle_product_creation(product_name):
    """
    @purpose: Get or create a product based on its name, setting default values if created.
    @param: product_name (str) - The name of the product.
    @return: (Product) - The product instance from the database.
    """
    product, created = Product.objects.get_or_create(
        product_name=product_name,
        defaults={
            'product_lowest_price': Decimal(random.randint(5000, 10000)),
            'last_updated': timezone.now(),
        }
    )

    if created:
        print(f"New product created: {product_name} with lowest price {product.product_lowest_price}")
    else:
        print(f"Product found: {product_name}")

    return product





def handle_variation_creation(product, variation_text, stock):
    """
    @purpose: Get or create a product variation, updating its stock if it already exists.
    @param: product (Product) - The product instance.
    @param: variation_text (str) - The variation text or name.
    @param: stock (int) - The stock quantity for the variation.
    @return: None
    """
    variation, variation_created = ProductVariation.objects.get_or_create(
        product=product,
        variation_text=variation_text,
        defaults={
            'stock': stock,
            'last_updated': timezone.now(),
        }
    )

    if variation_created:
        print(f"New variation created: {variation_text} for product {product.product_name}")
    else:
        variation.stock += stock
        variation.last_updated = timezone.now()
        variation.save()
        print(f"Updated stock for variation {variation_text} of product {product.product_name}")






def process_excel_row(row):
    """
    @purpose: Process a single row from the Excel sheet and update or create products and variations.
    @param: row (tuple) - A tuple containing values for product name, variation text, and stock.
    @return: None
    """
    product_name, variation_text, stock = row

    if not product_name or not variation_text :
        return  # Skip rows with missing product_name or variation_text

    try:
        product = handle_product_creation(product_name)
        handle_variation_creation(product, variation_text, stock)
    except Exception as e:
        print(f"Error processing row {row}: {e}")






def upload_products(request):
    """
    @purpose: Handle product upload via an Excel file, processing each row to update the database.
    @param: request (HttpRequest) - The request object containing form data and files.
    @return: (HttpResponse) - Redirects to the product list view or renders the upload form.
    """
    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['excel_file']
            workbook = openpyxl.load_workbook(excel_file)
            sheet = workbook.active

            for row in sheet.iter_rows(min_row=2, values_only=True):
                process_excel_row(row)

            return redirect('product_list_view')
    else:
        form = ExcelUploadForm()

    return render(request, 'upload_products.html', {'form': form})







def product_list_view(request):
    """
    @purpose: Render the product list page for the user interface.
    @param: request (HttpRequest) - The request object.
    @return: (HttpResponse) - Renders the 'product_list.html' template.
    """
    return render(request, 'product_list.html')
