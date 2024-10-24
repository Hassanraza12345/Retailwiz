import requests
import json
from lxml import etree as ET

def login_Service(user_id, password, auth_code):
    # Define the SOAP payload
    payload = f"""<?xml version="1.0" encoding="utf-8"?>
    <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
                   xmlns:xsd="http://www.w3.org/2001/XMLSchema" 
                   xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
        <soap:Body>
            <login xmlns="http://tempuri.org/">
                <user_id>{user_id}</user_id>
                <passwd>{password}</passwd>
                <auth_code>{auth_code}</auth_code>
            </login>
        </soap:Body>
    </soap:Envelope>"""

    headers = {
        'Content-Type': 'text/xml'
    }

    # Send the request to the SOAP API
    address = 'http://5.189.157.38:4000/retailService.asmx'
    response = requests.post(address, headers=headers, data=payload)

    # Check if the response was successful
    if response.status_code == 200:
        # Parse the XML response
        tree = ET.fromstring(response.content)
        
        # Extract the namespace map from the root element (SOAP namespace)
        namespaces = {'soap': 'http://schemas.xmlsoap.org/soap/envelope/', 
                      'tempuri': 'http://tempuri.org/'}

        # Find the loginResult element
        result_element = tree.find('.//tempuri:loginResult', namespaces)

        if result_element is not None:
            # Extract the JSON string from the result
            login_result_str = result_element.text

            # Convert the JSON string into a Python object (list or dict)
            login_result = json.loads(login_result_str)
            
            # Return the parsed JSON result
            return login_result
        else:
            print("loginResult element not found.")
            return None
    else:
        print(f"Failed with status code {response.status_code}")
        return None
    
def Inventory(serve_id):
    payload = f"""<?xml version=\"1.0\" encoding=\"utf-8\"?>\r\n
    <soap:Envelope xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\"
      xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\" 
      xmlns:soap=\"http://schemas.xmlsoap.org/soap/envelope/\">\r\n
          <soap:Body>\r\n    
          <inventory_rep xmlns=\"http://tempuri.org/\">\r\n      
          <serv_id>{serve_id}</serv_id>      \r\n    
          </inventory_rep>\r\n  
          </soap:Body>\r\n</soap:Envelope>"""
    headers = {
        'Content-Type':'text/xml'
    }
    address='http://5.189.157.38:4000/retailService.asmx'
    response= requests.request('POST',address,headers=headers, data=payload)
    if response.status_code ==200:
        tree=ET.fromstring(response.content)
        ns={
            'soap':'http://schemas.xmlsoap.org/soap/envelope/',
            'ns': 'http://tempuri.org/'
        }
    inventory_json_str= tree.find('.//ns:inventory_repResult',namespaces=ns).text
    return json.loads(inventory_json_str)


def Customers(serve_id):
    payload = f"""<?xml version=\"1.0\" encoding=\"utf-8\"?>\r\n
    <soap:Envelope xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\"
      xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\" 
      xmlns:soap=\"http://schemas.xmlsoap.org/soap/envelope/\">\r\n
          <soap:Body>\r\n    
          <customer_list xmlns=\"http://tempuri.org/\">\r\n      
          <serv_id>{serve_id}</serv_id>      \r\n    
          </customer_list>\r\n  
          </soap:Body>\r\n</soap:Envelope>"""
    headers = {
        'Content-Type':'text/xml'
    }
    address='http://5.189.157.38:4000/retailService.asmx'
    response= requests.request('POST',address,headers=headers, data=payload)
    if response.status_code ==200:
        tree=ET.fromstring(response.content)
        ns={
            'soap':'http://schemas.xmlsoap.org/soap/envelope/',
            'ns': 'http://tempuri.org/'
        }
    inventory_json_str= tree.find('.//ns:customer_listResult',namespaces=ns).text
    return json.loads(inventory_json_str)

def Supplier(serve_id):
    payload = f"""<?xml version=\"1.0\" encoding=\"utf-8\"?>\r\n
    <soap:Envelope xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\"
      xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\" 
      xmlns:soap=\"http://schemas.xmlsoap.org/soap/envelope/\">\r\n
          <soap:Body>\r\n    
          <supplier_list xmlns=\"http://tempuri.org/\">\r\n      
          <serv_id>{serve_id}</serv_id>      \r\n    
          </supplier_list>\r\n  
          </soap:Body>\r\n</soap:Envelope>"""
    headers = {
        'Content-Type':'text/xml'
    }
    address='http://5.189.157.38:4000/retailService.asmx'
    response= requests.request('POST',address,headers=headers, data=payload)
    if response.status_code ==200:
        tree=ET.fromstring(response.content)
        ns={
            'soap':'http://schemas.xmlsoap.org/soap/envelope/',
            'ns': 'http://tempuri.org/'
        }
    inventory_json_str= tree.find('.//ns:supplier_listResult',namespaces=ns).text
    return json.loads(inventory_json_str)

def sales_By_date(st_date, ed_date, serv_id):
    # Construct the SOAP payload
    payload = f"""<?xml version="1.0" encoding="utf-8"?>\r\n
    <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      xmlns:xsd="http://www.w3.org/2001/XMLSchema" 
      xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">\r\n
          <soap:Body>\r\n    
          <profit_inv_get xmlns="http://tempuri.org/">\r\n      
          <st_date>{st_date}</st_date>\r\n
          <ed_date>{ed_date}</ed_date>\r\n    
          <serv_id>{serv_id}</serv_id>\r\n
          </profit_inv_get>\r\n  
          </soap:Body>\r\n</soap:Envelope>"""
    
    headers = {
        'Content-Type': 'text/xml'
    }
    address = 'http://5.189.157.38:4000/retailService.asmx'
    
    # Make the POST request
    response = requests.post(address, headers=headers, data=payload)
    
    if response.status_code == 200:
        # Parse the XML response
        tree = ET.fromstring(response.content)
        ns = {
            'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
            'ns': 'http://tempuri.org/'
        }
        # Find the relevant part of the response
        inventory_json_str_element = tree.find('.//ns:profit_inv_getResult', namespaces=ns)
        
        if inventory_json_str_element is not None:
            # Extract the JSON string from the XML element
            inventory_json_str = inventory_json_str_element.text
            
            # Load the JSON string into a Python dictionary
            inventory_data = json.loads(inventory_json_str)
            
            # Return the data as a JSON response
            return inventory_data

def sales_By_cate(st_date, ed_date, serv_id):
    # Construct the SOAP payload
    payload = f"""<?xml version="1.0" encoding="utf-8"?>\r\n
    <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      xmlns:xsd="http://www.w3.org/2001/XMLSchema" 
      xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">\r\n
          <soap:Body>\r\n    
          <profit_inv_cat_get xmlns="http://tempuri.org/">\r\n      
          <st_date>{st_date}</st_date>\r\n
          <ed_date>{ed_date}</ed_date>\r\n    
          <serv_id>{serv_id}</serv_id>\r\n
          </profit_inv_cat_get>\r\n  
          </soap:Body>\r\n</soap:Envelope>"""
    
    headers = {
        'Content-Type': 'text/xml'
    }
    address = 'http://5.189.157.38:4000/retailService.asmx'
    
    # Make the POST request
    response = requests.post(address, headers=headers, data=payload)
    
    if response.status_code == 200:
        # Parse the XML response
        tree = ET.fromstring(response.content)
        ns = {
            'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
            'ns': 'http://tempuri.org/'
        }
        # Find the relevant part of the response
        inventory_json_str_element = tree.find('.//ns:profit_inv_cat_getResult', namespaces=ns)
        
        if inventory_json_str_element is not None:
            # Extract the JSON string from the XML element
            inventory_json_str = inventory_json_str_element.text
            
            # Load the JSON string into a Python dictionary
            inventory_data = json.loads(inventory_json_str)
            
            # Return the data as a JSON response
            return inventory_data

def sales_by_invoice(serv_id,st_date,ed_date):
    payload = f"""<?xml version="1.0" encoding="utf-8"?>\r\n
        <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
          xmlns:xsd="http://www.w3.org/2001/XMLSchema" 
          xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">\r\n
              <soap:Body>\r\n    
              <inv_rep xmlns="http://tempuri.org/">\r\n      
              <serv_id>{serv_id}</serv_id>\r\n
              <st_date>{st_date}</st_date>\r\n
              <ed_date>{ed_date}</ed_date>\r\n    
              </inv_rep>\r\n  
              </soap:Body>\r\n</soap:Envelope>"""

    headers = {
        'Content-Type': 'text/xml'
    }
    address = 'http://5.189.157.38:4000/retailService.asmx'
    response = requests.post(address, headers=headers, data=payload)
    if response.status_code == 200:
        # Parse the XML response
        tree = ET.fromstring(response.content)
        ns = {
            'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
            'ns': 'http://tempuri.org/'
        }
        # Find the relevant part of the response
        inventory_json_str_element = tree.find('.//ns:inv_repResult', namespaces=ns)

        if inventory_json_str_element is not None:
            # Extract the JSON string from the XML element
            inventory_json_str = inventory_json_str_element.text

            # Load the JSON string into a Python dictionary
            inventory_data = json.loads(inventory_json_str)

            # Return the data as a JSON response
            return inventory_data

def get_sales_by_invoice_detail(serv_id, ref_str):
    payload = f"""<?xml version="1.0" encoding="utf-8"?>\r\n
            <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
              xmlns:xsd="http://www.w3.org/2001/XMLSchema" 
              xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">\r\n
                  <soap:Body>\r\n    
                  <invoice_view_ref xmlns="http://tempuri.org/">\r\n      
                  <serv_id>{serv_id}</serv_id>\r\n
                  <refstr>{ref_str}</refstr>\r\n    
                  </invoice_view_ref>\r\n  
                  </soap:Body>\r\n</soap:Envelope>"""

    headers = {
        'Content-Type': 'text/xml'
    }
    address = 'http://5.189.157.38:4000/retailService.asmx'
    response = requests.post(address, headers=headers, data=payload)
    if response.status_code ==200:
        tree=ET.fromstring(response.content)
        ns = {
            'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
            'ns': 'http://tempuri.org/'
        }
        string_element=tree.find('.//ns:invoice_view_refResult', namespaces=ns)
        if string_element is not None:
            string_element=string_element.text
            json_data= json.loads(string_element)
            return  json_data
