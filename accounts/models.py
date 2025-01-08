from django.db import models
from django.db import models
from django.contrib.auth.models import User
import random
import string
# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    referral_code = models.CharField(max_length=8, unique=True, blank=True, null=True)
    referred_by = models.CharField(max_length=8, blank=True, null=True)
    kyc_document = models.FileField(upload_to='kyc_documents/', blank=True, null=True)
    kyc_document_type = models.CharField(max_length=50, blank=True, null=True)
    pan_card = models.FileField(upload_to='pan_cards/', blank=True, null=True)
    bank_passbook = models.FileField(upload_to='bank_passbooks/', blank=True, null=True)

def save(self, *args, **kwargs):
    # Automatically generate a unique referral code if not already set
    if not self.referral_code:
        self.referral_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username}'s Profile"
class Post(models.Model):
    title=models.CharField(max_length=50)
    img=models.ImageField(upload_to="pics")
    desc=models.CharField(max_length=500 , null=True)
    def __str__(self):
        return self.title
    
    

