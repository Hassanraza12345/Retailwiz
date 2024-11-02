import requests

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def get_location(ip_address):
    try:
        response = requests.get(f"https://ipinfo.io/{ip_address}/json?token=00ff3d1024ff3b")
        response.raise_for_status()  # Raises an HTTPError if the response code is 4xx/5xx
        data = response.json()
        location_data = {
            "city": data.get("city"),
            "region": data.get("region"),
            "country": data.get("country"),
            "latitude_longitude": data.get("loc")
        }
        return location_data
    except requests.RequestException as e:
        # Log the error and provide a default location or None
        print(f"Error fetching location: {e}")
        return None

