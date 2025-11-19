from django import forms

class NewsCheckForm(forms.Form):
    news_text = forms.CharField(
        label="Paste the news content here",
        widget=forms.Textarea(attrs={
            'rows': 6,
            'placeholder': 'Paste the news article, message, or content you want to verify...',
            'class': 'form-control news-input'
        }),
        max_length=2000
    )
    
    include_web_search = forms.BooleanField(
        label="Include web search for fact-checking",
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )