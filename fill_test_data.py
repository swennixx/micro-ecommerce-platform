import requests

BASE_URLS = {
    'users': 'http://localhost:8001',
    'products': 'http://localhost:8002',
    'orders': 'http://localhost:8003',
    'payments': 'http://localhost:8004',
}


def create_user():
    data = {
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'testpass123'
    }
    r = requests.post(f"{BASE_URLS['users']}/register", json=data)
    print('User:', r.status_code, r.json())
    # Если пользователь уже есть, просто залогиниться
    if r.status_code == 400 and 'Username already registered' in str(r.json()):
        return login_user()
    if r.status_code == 200:
        return login_user()
    raise Exception(f"User registration failed: {r.text}")

def login_user():
    data = {
        'username': 'testuser',
        'password': 'testpass123'
    }
    r = requests.post(f"{BASE_URLS['users']}/login", data=data)
    print('Login:', r.status_code, r.json())
    if r.status_code == 200:
        return r.json()['access_token']
    raise Exception(f"Login failed: {r.text}")

def create_product():
    data = {
        'name': 'Test Product',
        'description': 'A test product',
        'price': 99.99,
        'stock': 10
    }
    r = requests.post(f"{BASE_URLS['products']}/products", json=data)
    print('Product:', r.status_code, r.json())
    if r.status_code == 201:
        return r.json().get('id')
    if r.status_code == 400 and 'Product already exists' in str(r.json()):
        # Получить id первого продукта
        products = requests.get(f"{BASE_URLS['products']}/products").json()
        if products and isinstance(products, list):
            return products[0]['id']
        raise Exception("No products found, but product already exists?")
    raise Exception(f"Product creation failed: {r.text}")

def create_order(user_id, product_id):
    data = {
        'user_id': user_id,
        'products': [
            {'product_id': product_id, 'quantity': 2}
        ]
    }
    r = requests.post(f"{BASE_URLS['orders']}/orders", json=data)
    try:
        resp_json = r.json()
    except Exception:
        print('Order:', r.status_code, r.text)
        print('Order creation failed, skipping payment')
        return None, None
    print('Order:', r.status_code, resp_json)
    if r.status_code == 201:
        return resp_json.get('id'), resp_json.get('total_price')
    print('Order creation failed, skipping payment')
    return None, None

def create_payment(order_id, amount):
    if order_id is None or amount is None:
        print('Skipping payment: order_id or amount is None')
        return
    data = {
        'order_id': order_id,
        'amount': amount
    }
    r = requests.post(f"{BASE_URLS['payments']}/payments", json=data)
    print('Payment:', r.status_code, r.json())


def get_user_id(token):
    headers = {'Authorization': f'Bearer {token}'}
    r = requests.get(f"{BASE_URLS['users']}/users/me", headers=headers)
    print('Me:', r.status_code, r.json())
    if r.status_code == 200:
        return r.json()['id']
    raise Exception(f"Get user id failed: {r.text}")

def main():
    token = create_user()
    product_id = create_product()
    user_id = get_user_id(token)
    order_id, total_price = create_order(user_id, product_id)
    create_payment(order_id, total_price)

if __name__ == "__main__":
    main()
