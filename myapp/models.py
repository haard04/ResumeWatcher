from django.db import models

# Create your models here.
class MyModel(models.Model):
    username = models.CharField(max_length=100,default='')
    pdf_file = models.BinaryField()
    view_count = models.PositiveIntegerField(default=0)