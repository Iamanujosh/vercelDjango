from django.db import models
from django.contrib.auth.models import User

class WardrobeItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='wardrobe/')
    CATEGORY_CHOICES = [
        ('Shirt', 'Shirt'),
        ('Jacket', 'Jacket'),
        ('Dress', 'Dress'),
        ('Pants', 'Pants'),
        ('Skirt', 'Skirt'),
        ('Shoes', 'Shoes'),
        ('Bag', 'Bag'),
        ('Accessory', 'Accessory'),
        # Add more categories as needed
    ]
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)  # e.g., Shirt, Jacket
    last_worn = models.DateField(null=True, blank=True)
    color = models.CharField(max_length=50,default='NA')  # Add a field for color
    fav = models.CharField(max_length=50,default='NA')

    def __str__(self):
        return f'{self.name} ({self.category})'

class UserInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Links to the User model
    photo = models.ImageField(upload_to='user_photos/', null=True, blank=True)
    
    BODY_TYPE_CHOICES = [
        ('Apple', 'Apple'),
        ('Pear', 'Pear'),
        ('Hourglass', 'Hourglass'),
        ('Rectangle', 'Rectangle'),
        ('Curvy', 'Curvy'),
        ('Plus Size', 'Plus Size'),
    ]
    SKIN_TONE_CHOICES = [
        ('Fair', 'Fair'),
        ('Medium', 'Medium'),
        ('Olive', 'Olive'),
        ('Dark', 'Dark'),
    ]
    AGE_GROUP_CHOICES = [
        ('Teens', 'Teens (13-19)'),
        ('20s', '20s'),
        ('30s', '30s'),
        ('40s', '40s and above'),
    ]
    GENDER_CHOICE = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]
    TYPES_OF_CLOTHES = [
        ('Casual', 'Casual'),
        ('Workwear', 'Workwear'),
        ('Social Occasions', 'Social Occasions'),
        ('Maternity', 'Maternity'),
    ]
    SLEEVES_CHOICE = [
        ('Too short', 'Too short'),
        ('Just right', 'Just right'),
        ('Too long', 'Too long'),
    ]

    body_type = models.CharField(max_length=20, choices=BODY_TYPE_CHOICES)
    skin_tone = models.CharField(max_length=20, choices=SKIN_TONE_CHOICES)
    height = models.IntegerField(null=True, blank=True,default='NA')  # Height in cm
    weight = models.IntegerField(null=True, blank=True,default='NA')  # Weight in kg
    location = models.CharField(max_length=100, null=True, blank=True,default='NA')  # User's location/climate
    age_group = models.CharField(max_length=20, choices=AGE_GROUP_CHOICES)
    gender = models.CharField(max_length=100, choices=GENDER_CHOICE)
    types_of_clothes = models.CharField(max_length=100, choices=TYPES_OF_CLOTHES,default='NA')
    sleeves = models.CharField(max_length=20, choices=SLEEVES_CHOICE)

    def __str__(self):
        return f'{self.user.username} Profile'
