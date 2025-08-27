from django.http import JsonResponse, HttpResponseNotAllowed, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
import json
from .news_summarizer_model import run_summary
from newspaper import Article
from .services.router import route_and_summarize, TranslationError


@csrf_exempt
def summarize(request):
    """
    何をする関数か：
      - text でも url でも受け付ける統合版エンドポイント
      - ko 入力は ja にピボット、それ以外の非英日言語は en にピボット
      - 要約（英/日モデル）→ target_lang に最終翻訳
      - 長さは short|medium|long で指定

    受信JSON例：
      { "text": "...", "target_lang": "ja", "length": "medium" }
      { "url": "https://...", "target_lang": "fr", "length": "short" }
    戻り値：
      {
        "detected_lang": "ko",
        "pivoted": true,
        "summary_src_lang": "ja",
        "target_lang": "ja",
        "length": "medium",
        "summary": "..."
      }
    """
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"], "Use POST method instead")

    try:
        data = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON body")

    target_lang = (data.get("target_lang") or "ja").lower()
    length_mode = (data.get("length") or "medium").lower()

    # 入力の取り出し：url優先、無ければtext
    raw = ""
    if data.get("url"):
        try:
            art = Article(data["url"])
            art.download()
            art.parse()
            raw = (art.text or "").strip()

            # 任意：デバッグ出力（先頭末尾のみ）
            print("\n=== Extracted Article Text ===")
            print(raw[:30], "...", raw[-30:])
            print("=== End of Article ===\n")
        except Exception as e:
            return JsonResponse({"error": f"記事抽出に失敗: {str(e)}"}, status=400)
    else:
        raw = (data.get("text") or "").strip()

    if not raw:
        return HttpResponseBadRequest("Missing 'text' or 'url'")

    try:
        result = route_and_summarize(raw, target_lang=target_lang, length_mode=length_mode)
        return JsonResponse({
            "detected_lang": result["detected"],
            "pivoted": result["pivoted"],
            "summary_src_lang": result["summary_src"],
            "target_lang": target_lang,
            "length": length_mode,
            "summary": result["summary"],
        })
    except TranslationError as te:
        return JsonResponse({"error": f"翻訳失敗: {str(te)}"}, status=502)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)