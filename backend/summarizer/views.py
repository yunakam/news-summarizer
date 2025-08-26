from django.http import JsonResponse, HttpResponseNotAllowed, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
import json
from .news_summarizer_model import run_summary
from newspaper import Article

@csrf_exempt
def extract_article(request):
    """
    ユーザーから受け取ったURLをもとに記事本文を抽出して返すAPI
    """
    if request.method == "POST":
        data = json.loads(request.body)
        url = data.get("url")

        if not url:
            return JsonResponse({"error": "URLが指定されていません"}, status=400)

        try:
            article = Article(url)
            article.download()
            article.parse()
            
            # 抽出本文をサーバーターミナルに出力
            print("\n=== Extracted Article Text ===")
            print(article.text[:30], "...", article.text[-30:])
            print("=== End of Article ===\n")

            return JsonResponse({"article": article.text})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"error": "POSTメソッドで呼び出してください"}, status=405)
    

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

