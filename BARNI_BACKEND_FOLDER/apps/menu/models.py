from django.db import models
import uuid


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=10, blank=True, default='')
    sort_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    TYPE_CHOICES = (
        ('food', 'Food'),
        ('drink', 'Drink'),
        ('side', 'Side'),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=150)
    emoji = models.CharField(max_length=10, blank=True, default='')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    item_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='food')
    description = models.TextField(blank=True, default='')
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['category__sort_order', 'name']

    def __str__(self):
        return f"{self.emoji} {self.name}"


class Ingredient(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='ingredients')
    name = models.CharField(max_length=100)
    quantity = models.CharField(max_length=50, help_text='e.g. 150g, 10ml')
    is_raw = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.quantity}) for {self.menu_item.name}"
