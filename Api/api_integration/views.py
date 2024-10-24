import io,csv,re, os
from django.conf import settings
from django.template.loader import render_to_string
from django.shortcuts import render,redirect
from django.urls import reverse
from lxml import etree as ET 
from django.core.paginator import Paginator
from django.http import HttpResponse
from.import connection as conn
from django.contrib import messages
from functools import wraps
from django.core.cache import cache
from datetime import datetime
from weasyprint import HTML
from django.templatetags.static import static




# Custom login required decorator
def login_required_custom(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Check if the 'serv_id' is present in the session
        if 'serv_id' not in request.session:
            # If not present, redirect to login page
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper

@login_required_custom
def home(request):
    return render(request,'dashboard/dashboard.html')


# Create your views here.
def login_view(request):
    if request.method == 'POST':
        userid = request.POST.get('username')
        password = request.POST.get('password')
        auth_code = request.POST.get('auth_code')

        # Assume conn.login_Service returns a list of dictionaries or None
        raw_data = conn.login_Service(userid, password, auth_code)

        # Check if raw_data is None or not a list
        if raw_data is None or not isinstance(raw_data, list) or len(raw_data) == 0:
            messages.error(request, 'Invalid login response or empty data.')
            return render(request, 'login/login.html')

        # Further check for serv_id in the first dictionary of the list
        serv_id = raw_data[0].get('serv_id')

        if not serv_id:  # Handles cases where serv_id is None or empty
            messages.error(request, 'Invalid username and password')
            return render(request, 'login/login.html')
        else:
            # Store serv_id in session
            request.session['serv_id'] = serv_id
            return redirect(home)
    else:
        return render(request, 'login/login.html')

def logout_view(request):
    if 'serv_id' in request.session:
        request.session.flush()
        messages.success(request,'You have been logged out Successfully')
    return redirect('login')

def register(request):
    if request.method=='POST':
        username=request.POST.get('username')
        email=request.POST.get('email')
        password1=request.POST.get('password1')
        password2=request.POST.get('password2')
        if password1 != password2:
            messages.error(request,'Password do not match')
            return render(request,'Api/register.html')
    else:
        return render(request, 'Api/register.html')

@login_required_custom
def inventory(request):
    serv_id = request.session.get('serv_id')
    if serv_id:

        data = cache.get("inventory_data")
    if not data:
        # Get inventory data via the SOAP API if not in cache
        inventory_data = conn.Inventory(serv_id)
        data = inventory_data
        # Cache the data for 3 minutes (adjust as needed)
        cache.set("inventory_data", data, timeout=180)
    
    # Get the search query from the GET request
    query = request.GET.get('q', '')

    # Filter the data if a query is provided
    if query:
        # Use regular expressions for case-insensitive search in all fields
        regex = re.compile(re.escape(query), re.IGNORECASE)
        filtered_data = [
            item for item in data
            if any(regex.search(str(value)) for value in item.values())
        ]
    else:
        filtered_data = data

    # Paginate the filtered data
    paginator = Paginator(filtered_data, 100)  # Show 100 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Pass the page object and query back to the template
    content = {
        'page_obj': page_obj,
        'query': query
    }

    return render(request, 'inventory/inventory.html', content)

@login_required_custom
def generate_pdf(request, pdf_type):
    if pdf_type == 'customer':
        data = cache.get('customer_data')
        template_name = 'customer/customers_pdf_template.html'
    elif pdf_type == 'inventory':
        data = cache.get('inventory_data')
        template_name = 'inventory/inventory_pdf_template.html'
    elif pdf_type == 'supplier':
        data = cache.get('supplier_data')
        template_name = 'supplier/supplier_pdf_template.html'
    elif pdf_type == 'sale':
        data = cache.get('sales_data')
        template_name = 'Reports/sales/sales_pdf_template.html'
    # elif pdf_type == 'profit_cat':
    #     data = cache.get('profit_cat')
    #     template_name = 'Reports/profit/profit_cat_pdf_template.html'
    # elif pdf_type == 'profit_invoice':
    #     data = cache.get('profit_invoice')
    #     template_name = 'Reports/profit/profit_invoice_pdf_template.html'
    logo=request.build_absolute_uri(static("icons/logo.png"))
    
    date = datetime.now().strftime('%Y-%m-%d')
    context = {"data": data, 'date': date, 'logo': logo}

    # Render the HTML to a string
    html_content = render_to_string(template_name, context)

    # Generate PDF using WeasyPrint with reduced DPI
    pdf = HTML(string=html_content).write_pdf(dpi=150)  # Adjust DPI as needed

    # Create PDF response
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{pdf_type}_report.pdf"'
    
    return response

@login_required_custom
def generate_csv(request, pdf_type):
    # Determine the cache key based on the pdf_type
    data_cache_key_map = {
        'customer': 'customer_data',
        'inventory': 'inventory_data',
        'supplier': 'supplier_data',
        'sale': 'sales_data',
        'profit_cat':'profit_cat',
        'profit_invoice': 'profit_invoice'
    }

    # Fetch the corresponding data from the cache
    data = cache.get(data_cache_key_map.get(pdf_type))

    # Check if data exists in the cache
    if data is None:
        return HttpResponse("No data available.", status=404)

    # Create a CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{pdf_type}_report.csv"'

    # Create a CSV writer
    writer = csv.writer(response)

    # Write the header based on pdf_type
    if pdf_type == 'inventory':
        writer.writerow(["Index", "Item Code", "Item Description", "Rate", "Cost", "Total"])
    elif pdf_type == 'customer':
        writer.writerow(["Index", "Customer Name", "Phone No", "Current Balance", "Customer Type"])
    elif pdf_type == 'supplier':
        writer.writerow(["Index", "Supplier Name", "Customer Code", "Customer Bal", "Customer Status"])
    elif pdf_type == 'sale':
        writer.writerow(['Index', 'Invoice No', 'Total_Amount', 'Date Ref-No'])
    elif pdf_type == 'profit_cat':
        writer.writerow(['Index','Item_desc', 'Qty', 'T_sale_value', 'Cogs_value', 'Dt_date', 'Inv_no', 'Location_id', 'T_value'])
    elif pdf_type == 'profit_invoice':
        writer.writerow(['Index','Item_desc', 'Qty', 'T_sale_value', 'Cogs_value', 'Dt_date', 'Inv_no', 'Location_id', 'T_value'])
    # Write the data rows
    for index, item in enumerate(data, start=1):
        if pdf_type == 'inventory':
            writer.writerow([
                index,
                item.get('item_code', ''),
                item.get('Item_desc', ''),
                item.get('rate', '0'),
                item.get('cost', '0'),
                float(item.get('rate', 0)) + float(item.get('cost', 0))
            ])
        elif pdf_type == 'customer':
            writer.writerow([
                index,
                item.get('cust_name', ''),
                item.get('ph_no', ''),
                item.get('current_bal', '0'),
                item.get('customer_type', '')
            ])
        elif pdf_type == 'supplier':
            writer.writerow([
                index,
                item.get('cust_name', ''),
                item.get('cust_code', ''),
                item.get('cust_bal', ''),
                item.get('active', '0')
            ])
        elif pdf_type == 'sale':
            writer.writerow([
                index,
                item.get('inv_no',''),
                item.get('total_amt',''),
                item.get('inv_date',''),
                item.get('inv_ref','')

            ])
        elif pdf_type == 'profit_cat':
            writer.writerow([
                index,
                item.get('item_desc',''),
                item.get('qty',''),
                item.get('t_sale_value',''),
                item.get('cogs_value',''),
                item.get('dt_date',''),
                item.get('inv_no',''),
                item.get('location_id',''),
                item.get('t_value',''),

            ])
        elif pdf_type == 'profit_invoice':
            writer.writerow([
                index,
                item.get('item_desc',''),
                item.get('qty',''),
                item.get('t_sale_value',''),
                item.get('cogs_value',''),
                item.get('dt_date',''),
                item.get('inv_no',''),
                item.get('location_id',''),
                item.get('t_value',''),

            ])

    return response

@login_required_custom
def customer(request):
    serv_id = request.session.get('serv_id')
    if serv_id:

        data = cache.get("customer_data")
    if not data:
        # Get inventory data via the SOAP API if not in cache
        customer_data = conn.Customers(serv_id)
        data = customer_data
        # Cache the data for 30 minutes (adjust as needed)
        cache.set("customer_data", data, timeout=180)
    
    # Get the search query from the GET request
    query = request.GET.get('q', '')

    # Filter the data if a query is provided
    if query:
        # Use regular expressions for case-insensitive search in all fields
        regex = re.compile(re.escape(query), re.IGNORECASE)
        filtered_data = [
            item for item in data
            if any(regex.search(str(value)) for value in item.values())
        ]
    else:
        filtered_data = data

    # Paginate the filtered data
    paginator = Paginator(filtered_data, 100)  # Show 100 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Pass the page object and query back to the template
    content = {
        'page_obj': page_obj,
        'query': query
    }

    return render(request, 'customer/customer.html', content)

@login_required_custom
def supplier(request):
    serv_id = request.session.get('serv_id')
    if serv_id:

        data = cache.get("supplier_data")
    if not data:
        # Get inventory data via the SOAP API if not in cache
        customer_data = conn.Supplier(serv_id)
        data = customer_data
        # Cache the data for 30 minutes (adjust as needed)
        cache.set("supplier_data", data, timeout=180)
    
    # Get the search query from the GET request
    query = request.GET.get('q', '')

    # Filter the data if a query is provided
    if query:
        # Use regular expressions for case-insensitive search in all fields
        regex = re.compile(re.escape(query), re.IGNORECASE)
        filtered_data = [
            item for item in data
            if any(regex.search(str(value)) for value in item.values())
        ]
    else:
        filtered_data = data

    # Paginate the filtered data
    paginator = Paginator(filtered_data, 100)  # Show 100 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Pass the page object and query back to the template
    content = {
        'page_obj': page_obj,
        'query': query
    }

    return render(request, 'supplier/supplier.html', content)

@login_required_custom
def reports(request):
    return render(request,'Api/reports.html')

@login_required_custom
def sales(request):
    return render(request,'Api/sales.html')

@login_required_custom
def profit(request):
    return render(request,'Api/profit.html')

@login_required_custom
def profit_invoice(request):
    if request.method == 'POST':
        st_date = request.POST.get('st_date')
        ed_date = request.POST.get('ed_date')
        serve_id=request.session.get('serv_id')
        if serve_id:
            data = conn.sales_By_date(st_date, ed_date, serve_id)
            if data:
                cache.set('profit_invoice',data, timeout=180)
                filtered_data = data

                # Paginate the filtered data
                paginator = Paginator(filtered_data, 100)  # Show 100 items per page
                page_number = request.GET.get('page')
                page_obj = paginator.get_page(page_number)

                context={
                    'title':'Profit Invoices',
                    'page_obj': page_obj
                }
                return render(request, 'Reports/profit/profit_invoice.html',context)
            else:
                messages.error(request, 'Enter a valid duration')
                return redirect(request,'base/date.html')
        else:
            messages.error(request, 'Session expired or invalid service ID')
            return redirect('login')
    
    # If the request method is GET or any other method, render the page without data
    return render(request, 'base/date.html')

@login_required_custom
def profit_category(request):
    if request.method == 'POST':
        start_date=request.POST.get('st_date')
        end_date=request.POST.get('ed_date')
        serv_id = request.session.get('serv_id')
        # Ensure serv_id is valid (not None) before making the API call
        if serv_id:
            
            data=conn.sales_By_cate(start_date,end_date,request.session.get('serv_id'))
            if data:
                cache.set('profit_cat',data,timeout=180)
                filtered_data = data
# Paginate the filtered data
                paginator = Paginator(filtered_data, 100)  # Show 100 items per page
                page_number = request.GET.get('page')
                page_obj = paginator.get_page(page_number)
                content = {
                    'page_obj': page_obj,
                    'title':'Profit'
                }

                return render(request,'Reports/profit/profit_by_cat_list.html',content)
            else:
                messages.success(request, 'Enter a valid duration')
                return render(request,'base/date.html')
        else:
            # Handle the case when serv_id is not found in the session
            messages.error(request, 'Session expired or invalid service ID')
            request.session.flush()
            return redirect('login')  # Redirect to login or another appropriate view
    return render(request,'base/date.html')

@login_required_custom
def sales_invoice_list(request):
    if request.method == 'POST':
        st_date = request.POST.get('st_date')
        ed_date = request.POST.get('ed_date')
        # Use a string key to get the session variable
        serv_id = request.session.get('serv_id')
        # Ensure serv_id is valid (not None) before making the API call
        if serv_id:
            data = conn.sales_by_invoice(serv_id, st_date, ed_date)
            if data:
                cache.set('sales_data',data, timeout=180)
                filtered_data = data
# Paginate the filtered data
                paginator = Paginator(filtered_data, 100)  # Show 100 items per page
                page_number = request.GET.get('page')
                page_obj = paginator.get_page(page_number)

                # Pass the page object and query back to the template
                content = {
                    'page_obj': page_obj,
                    'title': 'Sales Invoices'
                }
                return render(request, 'Reports/sales/sales_list.html', content)
            else:
                messages.error(request, 'Enter a valid duration')
                return render(request,'base/date.html')
        else:
            # Handle the case when serv_id is not found in the session
            messages.error(request, 'Session expired or invalid service ID')
            request.session.flush()
            return redirect('login')  # Redirect to login or another appropriate view
    return render(request, 'base/date.html')

@login_required_custom
def sales_invoice_detail(request,ref_str):
    session_id=request.session.get('serv_id')
    data=conn.get_sales_by_invoice_detail(session_id,ref_str)
    total_amount=0
    if data:
        for item in data:
            discount=(item['rate']*item['discount'])/100
            amount=item['rate']-discount
            t_amount=amount*item['qty']
            total_amount+=t_amount
    
    template_name=request.GET.get('template','A4')
    if template_name == 'A5':
        template_name='invoices/A5.html'
    elif template_name == 'Thermal':
        template_name='invoices/thermal.html'
    else:
        template_name='invoices/A4.html'
    return render(request,template_name,{'data':data,'total':total_amount})
