from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .forms import NewsCheckForm
from .services import FakeNewsDetector
from .models import NewsCheck
import json

def index(request):
    if request.method == 'POST':
        form = NewsCheckForm(request.POST)
        if form.is_valid():
            news_text = form.cleaned_data['news_text']
            include_web_search = form.cleaned_data['include_web_search']
            
            # Initialize detector and check news
            detector = FakeNewsDetector()
            result = detector.check_news(news_text, include_web_search)
            
            # Save to database
            news_check = NewsCheck(
                news_text=news_text,
                is_fake=result['analysis'].get('is_fake'),
                confidence_score=result['analysis'].get('confidence_score', 0),
                fact_check_details=result['analysis'],
                sources_checked=result['sources_checked']
            )
            news_check.save()
            
            return render(request, 'detector/result.html', {
                'result': result,
                'news_check_id': news_check.id,
                'form': form
            })
    else:
        form = NewsCheckForm()
    
    return render(request, 'detector/index.html', {'form': form})

def result(request, check_id):
    try:
        news_check = NewsCheck.objects.get(id=check_id)
        result = {
            'analysis': news_check.fact_check_details,
            'sources_checked': news_check.sources_checked,
            'news_preview': news_check.news_text[:200] + '...' if len(news_check.news_text) > 200 else news_check.news_text
        }
        return render(request, 'detector/result.html', {'result': result, 'news_check_id': check_id})
    except NewsCheck.DoesNotExist:
        return redirect('index')

def about(request):
    return render(request, 'detector/about.html')

@csrf_exempt
def api_check_news(request):
    """API endpoint for external integrations"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            news_text = data.get('news_text', '')
            include_web_search = data.get('include_web_search', True)
            
            detector = FakeNewsDetector()
            result = detector.check_news(news_text, include_web_search)
            
            return JsonResponse({
                'status': 'success',
                'result': result
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Only POST method allowed'}, status=405)

def debug_info(request):
    """Debug page to check API key status"""
    from django.conf import settings
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    debug_info = {
        'settings_gemini_key': getattr(settings, 'GEMINI_API_KEY', 'Not found'),
        'env_gemini_key': os.getenv('GEMINI_API_KEY', 'Not found'),
        'settings_secret_key': getattr(settings, 'SECRET_KEY', 'Not found')[:20] + '...',
        'env_secret_key': os.getenv('DJANGO_SECRET_KEY', 'Not found')[:20] + '...',
    }
    
    # Test the detector
    from .services import FakeNewsDetector
    detector = FakeNewsDetector()
    
    return render(request, 'detector/debug.html', {
        'debug_info': debug_info,
        'detector_has_key': bool(detector.gemini_api_key),
        'detector_key_preview': detector.gemini_api_key[:20] + '...' if detector.gemini_api_key else 'None'
    })