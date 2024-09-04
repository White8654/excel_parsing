from djongo import models
from decimal import Decimal
# product model
class Product(models.Model):
    product_name = models.CharField(max_length=100)
    product_lowest_price = models.DecimalField(max_digits=10, decimal_places=2)
    last_updated = models.DateTimeField()

    def __str__(self):
        return self.product_name

# productvariation model
class ProductVariation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation_text = models.CharField(max_length=100)
    stock = models.IntegerField()
    last_updated = models.DateTimeField()

    def __str__(self):
        return f'{self.product.product_name} - {self.variation_text}'
