from django.http import JsonResponse, HttpResponseNotAllowed, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
import json
from .news_summarizer_model import run_summary

@csrf_exempt
def summarize(request):
    # POST以外は 405 を返す
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"], "Use POST method instead")
    
    # JSONを取り出し、text と mode を取得

    try:
        data = json.loads(request.body)
    except  json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON body")
    
    text = data.get("text")
    mode = data.get("mode")
    
    if not text:
        return HttpResponseBadRequest("Missing 'text'")

    allowed = {"short", "medium", "long"}
    if mode not in allowed:
        return HttpResponseBadRequest("Invalid 'mode' (use: short|medium|long)")

    summary = run_summary(text, mode)
    
    return JsonResponse({"summary": summary})

