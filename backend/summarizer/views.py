from django.http import JsonResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
import json
from .news_summarizer_model import run_summary

@csrf_exempt
def summarize(request):
    if request.method == "POST":
        data = json.loads(request.body)
        text = data.get("text")
        summary = run_summary(text)
        return JsonResponse({"summary": summary})
    else:
        return HttpResponseNotAllowed(["POST"], "Use POST method instead")
