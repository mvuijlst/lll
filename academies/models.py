from django.db import models


class Academy(models.Model):
    name = models.CharField(max_length=100)
    colour = models.CharField(max_length=7, help_text="Hex color code (e.g., #FF5733)")
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Academies"


class Offering(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    academy = models.ForeignKey(Academy, on_delete=models.CASCADE, related_name='offerings')
    
    def __str__(self):
        return f"{self.name} - {self.academy.name}"
