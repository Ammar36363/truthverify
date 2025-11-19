from django.db import models

class NewsCheck(models.Model):
    news_text = models.TextField()
    is_fake = models.BooleanField(null=True, blank=True)
    confidence_score = models.FloatField(null=True, blank=True)
    fact_check_details = models.JSONField(default=dict)
    sources_checked = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"News Check {self.id} - {'Fake' if self.is_fake else 'Real'}"