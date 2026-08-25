import django, os, sys, json, urllib.request
sys.stdout.reconfigure(encoding='utf-8')
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.dev'
django.setup()
BASE = 'http://localhost:8000'

def post(path, data, token=None):
    body = json.dumps(data).encode()
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    req = urllib.request.Request(f'{BASE}{path}', data=body, headers=headers, method='POST')
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return json.loads(e.read())

def get(path, token=None):
    headers = {}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    req = urllib.request.Request(f'{BASE}{path}', headers=headers)
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

# 1. Login waiter
r = post('/api/auth/login/', {'username':'lema','password':'1234','role':'waiter'})
wt = r['access']
print('1. Waiter OK')

# 2. Get menu
items = get('/api/menu/items/', wt)
food = [i for i in items.get('results',[]) if i.get('is_available') and i.get('item_type') != 'side']
item = food[0]
print(f'2. Menu item: {item["name"]}')

# 3. Place order
r = post('/api/orders/place/', {'menu_item_id':item['id'],'table_id':1,'side':'Plain','quantity':1,'source':'barni'}, wt)
print(f'3. Order placed: {r["order_id"]} status={r["status"]}')

# 4. Kitchen queue
kq = get('/api/kitchen/queue/', wt)
print(f'4. Kitchen queue: {len(kq)} items')

# 5. Active orders
orders = get('/api/orders/orders/', wt)
active = [o for o in orders.get('results',[]) if o['status'] not in ('served','declined','cancelled')]
print(f'5. Active orders: {len(active)}')
for o in active:
    print(f'   {o["order_id"]} status={o["status"]} source={o["source"]}')

# 6. Customer order
cr = post('/api/auth/login/', {'username':'guest','password':'1234','role':'customer'})
ct = cr['access']
r = post('/api/orders/customer/place/', {'menu_item_id':item['id'],'side':'Plain','quantity':1,'payment_method':'CBE'}, ct)
print(f'6. Customer order: {r["order_id"]} status={r["status"]}')

# 7. Pending customer orders
orders2 = get('/api/orders/orders/', wt)
pending = [o for o in orders2.get('results',[]) if o['source']=='customer' and o['status']=='pending']
print(f'7. Pending customer orders: {len(pending)}')

print('\nALL OK')
