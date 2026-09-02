import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.menu.models import Category, MenuItem

print("Creating categories...")

# Create categories
pizza, created = Category.objects.get_or_create(name='Pizza', defaults={'icon': '🍕', 'is_active': True})
burger, created = Category.objects.get_or_create(name='Burgers', defaults={'icon': '🍔', 'is_active': True})
drinks, created = Category.objects.get_or_create(name='Drinks', defaults={'icon': '🥤', 'is_active': True})
print("✅ Categories created")

print("Creating menu items...")

# Create menu items
items_data = [
    {'name': 'Margherita Pizza', 'price': 12.99, 'category': pizza, 'emoji': '🍕'},
    {'name': 'Pepperoni Pizza', 'price': 14.99, 'category': pizza, 'emoji': '🍕'},
    {'name': 'BBQ Chicken Pizza', 'price': 16.99, 'category': pizza, 'emoji': '🍕'},
    {'name': 'Classic Burger', 'price': 10.99, 'category': burger, 'emoji': '🍔'},
    {'name': 'Cheese Burger', 'price': 11.99, 'category': burger, 'emoji': '🍔'},
    {'name': 'Cola', 'price': 2.99, 'category': drinks, 'emoji': '🥤'},
    {'name': 'Lemonade', 'price': 3.49, 'category': drinks, 'emoji': '🍋'},
]

for item_data in items_data:
    obj, created = MenuItem.objects.get_or_create(
        name=item_data['name'],
        category=item_data['category'],
        defaults={
            'price': item_data['price'],
            'emoji': item_data['emoji'],
            'is_available': True
        }
    )
    if created:
        print(f"✅ Created: {item_data['name']}")
    else:
        print(f"ℹ️ Already exists: {item_data['name']}")

print("\n📋 Available menu items:")
for item in MenuItem.objects.filter(is_available=True):
    print(f"  - {item.id}: {item.emoji} {item.name} (${item.price})")
