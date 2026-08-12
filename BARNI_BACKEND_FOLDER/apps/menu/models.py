from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

class Category(models.Model):
    class MealPeriod(models.TextChoices):
        BREAKFAST = "BREAKFAST", "Breakfast"
        LUNCH = "LUNCH", "Lunch"
        DINNER = "DINNER", "Dinner"
        ALL_DAY = "ALL_DAY", "All day"

    category_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=80)
    cuisine_type = models.CharField(max_length=50, blank=True, null=True)
    meal_period = models.CharField(max_length=30, choices=MealPeriod.choices, blank=True, null=True)
    display_order = models.IntegerField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "categories"
        ordering = ["display_order", "name"]

    def __str__(self):
        return self.name

class MenuItem(models.Model):
    item_id = models.BigAutoField(primary_key=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="menu_items", db_column="category_id")
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True, null=True)
    selling_price = models.DecimalField(max_digits=12, decimal_places=2)
    labor_pct = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    rent_pct = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    utility_pct = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    kitchen_station = models.CharField(max_length=40, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    image_url = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "menu_items"
        ordering = ["category_id", "name"]
        constraints = [
            models.CheckConstraint(condition=models.Q(selling_price__gte=0), name="menu_item_selling_price_nonnegative"),
        ]

    def __str__(self):
        return self.name
