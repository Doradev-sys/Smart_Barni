from django.core.management.base import BaseCommand
from apps.menu.models import Category, MenuItem, Ingredient
from apps.orders.models import Table


class Command(BaseCommand):
    help = 'Seed database with Barni Coffee menu data and tables'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database...')

        categories_data = [
            {'name': 'Food', 'icon': '🍽️', 'sort_order': 1},
            {'name': 'Drinks', 'icon': '☕', 'sort_order': 2},
            {'name': 'Sides', 'icon': '🧂', 'sort_order': 3},
        ]

        cat_objects = {}
        for cd in categories_data:
            cat, _ = Category.objects.update_or_create(
                name=cd['name'],
                defaults=cd,
            )
            cat_objects[cd['name']] = cat

        foods_data = [
            {'name': 'French Fries', 'price': 50, 'emoji': '🍟', 'item_type': 'food', 'category': 'Food',
             'ingredients': [('Potato', '300g', True), ('Cooking Oil', '50ml', False), ('Salt', '5g', False)]},
            {'name': 'Burger', 'price': 200, 'emoji': '🍔', 'item_type': 'food', 'category': 'Food',
             'ingredients': [('Beef Patty', '150g', True), ('Bun', '1 pc', True), ('Cheese Slice', '1 pc', False), ('Ketchup', '10ml', False)]},
            {'name': 'Grilled Chicken', 'price': 250, 'emoji': '🍗', 'item_type': 'food', 'category': 'Food',
             'ingredients': [('Chicken Thigh', '250g', True), ('Spice Mix', '8g', False), ('Butter', '10g', False)]},
            {'name': 'Pasta Alfredo', 'price': 180, 'emoji': '🍝', 'item_type': 'food', 'category': 'Food',
             'ingredients': [('Pasta', '180g', True), ('Cream Sauce', '80ml', False), ('Parmesan', '15g', False)]},
            {'name': 'Club Sandwich', 'price': 140, 'emoji': '🥪', 'item_type': 'food', 'category': 'Food',
             'ingredients': [('Bread Slice', '3 pc', True), ('Chicken Breast', '100g', True), ('Mayonnaise', '12ml', False)]},
            {'name': 'Caesar Salad', 'price': 110, 'emoji': '🥗', 'item_type': 'food', 'category': 'Food',
             'ingredients': [('Lettuce', '120g', True), ('Caesar Dressing', '25ml', False), ('Croutons', '20g', False)]},
            {'name': 'Margherita Pizza', 'price': 220, 'emoji': '🍕', 'item_type': 'food', 'category': 'Food',
             'ingredients': [('Pizza Dough', '220g', True), ('Tomato', '80g', True), ('Mozzarella', '90g', False)]},
            {'name': 'Beef Steak', 'price': 320, 'emoji': '🥩', 'item_type': 'food', 'category': 'Food',
             'ingredients': [('Beef Steak Cut', '280g', True), ('Black Pepper Sauce', '40ml', False)]},
            {'name': 'Sushi Roll', 'price': 260, 'emoji': '🍣', 'item_type': 'food', 'category': 'Food',
             'ingredients': [('Rice', '150g', True), ('Nori Sheet', '2 pc', True), ('Soy Sauce', '10ml', False)]},
            {'name': 'Veggie Wrap', 'price': 100, 'emoji': '🌯', 'item_type': 'food', 'category': 'Food',
             'ingredients': [('Tortilla Wrap', '1 pc', True), ('Mixed Veg', '120g', True), ('Hummus', '20g', False)]},
        ]

        drinks_data = [
            {'name': 'Espresso', 'price': 60, 'emoji': '☕', 'item_type': 'drink', 'category': 'Drinks',
             'ingredients': [('Coffee Beans', '18g', True), ('Water', '30ml', False)]},
            {'name': 'Cappuccino', 'price': 80, 'emoji': '🥛', 'item_type': 'drink', 'category': 'Drinks',
             'ingredients': [('Coffee Beans', '18g', True), ('Steamed Milk', '150ml', False)]},
            {'name': 'Fresh Juice', 'price': 90, 'emoji': '🥤', 'item_type': 'drink', 'category': 'Drinks',
             'ingredients': [('Fresh Fruit', '250g', True), ('Sugar Syrup', '10ml', False)]},
            {'name': 'Mojito', 'price': 120, 'emoji': '🍹', 'item_type': 'drink', 'category': 'Drinks',
             'ingredients': [('Mint Leaves', '6 pc', True), ('Lime', '1 pc', True), ('Soda Water', '120ml', False)]},
            {'name': 'Iced Tea', 'price': 70, 'emoji': '🧋', 'item_type': 'drink', 'category': 'Drinks',
             'ingredients': [('Tea Leaves', '5g', True), ('Ice', '100g', False), ('Sugar Syrup', '10ml', False)]},
            {'name': 'Hot Chocolate', 'price': 85, 'emoji': '🍫', 'item_type': 'drink', 'category': 'Drinks',
             'ingredients': [('Cocoa Powder', '20g', True), ('Steamed Milk', '180ml', False)]},
        ]

        all_items = foods_data + drinks_data
        for item_data in all_items:
            cat_name = item_data.pop('category')
            ingredients = item_data.pop('ingredients')
            item, _ = MenuItem.objects.update_or_create(
                name=item_data['name'],
                defaults={**item_data, 'category': cat_objects[cat_name]},
            )
            item.ingredients.all().delete()
            for ing_name, ing_qty, is_raw in ingredients:
                Ingredient.objects.create(
                    menu_item=item,
                    name=ing_name,
                    quantity=ing_qty,
                    is_raw=is_raw,
                )

        sides_cat, _ = Category.objects.update_or_create(
            name='Sides',
            defaults={'icon': '🧂', 'sort_order': 3},
        )
        for side_name in ['With Egg', 'Without Egg', 'Plain']:
            MenuItem.objects.update_or_create(
                name=side_name,
                defaults={'price': 0, 'emoji': '🧂', 'item_type': 'side', 'category': sides_cat},
            )

        for i in range(1, 16):
            Table.objects.update_or_create(number=i, defaults={'is_active': True})

        self.stdout.write(self.style.SUCCESS(
            f'Seeded {len(all_items)} menu items, 3 sides, {len(categories_data)} categories, 15 tables'
        ))
