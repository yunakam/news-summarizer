# ニュース要約デモ

## 要約処理の流れ

1. **page.tsx → route.ts**

   * `page.tsx` 内で `fetch("/api/summarize", { method: "POST", body: JSON.stringify({ text }) })` が呼ばれる。
   * このリクエストは Next.js アプリ内部で `app/api/summarize/route.ts` にルーティングされる。

2. **route.ts → Django**

   * `route.ts` の `POST` 関数で `req.json()` から `text` を取得。
   * それを `http://localhost:8000/summarizer/summarize/` へ転送する（Django 側の API エンドポイント）。
   * この時 `Content-Type: application/json` ヘッダーを付与しているので、Django 側では `views.summarize` が JSON として解釈できる。

3. **Django → route.ts**

   * `views.py` の `summarize` 関数が `run_summary(text)` を実行し、`JsonResponse({"summary": summary})` を返す。

4. **route.ts → page.tsx**

   * Django から返ってきた JSON をそのまま `NextResponse.json({ summary: data.summary })` でフロントへ返す。

5. **page.tsx → UI へ表示**

   * `page.tsx` 側で `setSummary(data.summary)` を実行し、画面に要約が表示される。

### まとめると

* **page.tsx** → `/api/summarize` に POST
* **route.ts** → Django API (`http://localhost:8000/summarizer/summarize/`) に中継
* **views.py** → `run_summary` で要約 → JSON 返却
* **route.ts** → JSON を UI に返却
* **page.tsx** → `summary` を state に格納 → 画面に表示

---

## 社内共有：ngrok

* ローカルで動かしているアプリを一時的にインターネットに公開できる。
* 短時間のデモや簡易的な社内共有に向いている。

### 1. ngrok をインストール

PowerShell で以下を実行：

```powershell
choco install ngrok
```
（Chocolatey が入っていない場合は [公式サイト](https://ngrok.com/download) からバイナリを落として配置する）

### 2. ngrok にログイン（初回のみ）

公式サイトで無料アカウントを作成し、Auth Token を取得。
PowerShell で以下を実行：

```powershell
ngrok config add-authtoken <取得したトークン>
```

### 3. Django を公開

Django を通常通り起動（例: ポート8000）：

```powershell
python manage.py runserver 8000
```

別ターミナルで ngrok を実行：

```powershell
ngrok http 8000
```

→ `https://xxxxx.ngrok-free.app` のようなURLが発行される。これを共有すれば社内の別ネットワークからアクセス可能。

### 4. Next.js を公開

Next.js をポート3000で起動：

```powershell
npm run dev
```

別ターミナルで ngrok：

```powershell
ngrok http 3000
```

→ こちらも URL が発行されるので共有すればアクセスできる。

## 🔹 注意点

* 無料プランでは **セッション時間に制限** がある（8時間で切れる）。
* Django と Next.js の両方を見せたいなら、**ngrok を2つ起動**する必要がある（8000と3000でそれぞれ）。
* 本番用途には不向きだが、デモには十分。

👉 もし「Django の API を Next.js が呼んでいる」構成なら、**Next.js 側だけ ngrok 公開すればOK**。
（Next.js が Django へリクエストする際に、`NEXT_PUBLIC_API_URL` を ngrok のDjango URLに変更する必要あり）

---

## 要約モデル

- 日本語モデル：`tsmatz/mt5_summarize_japanese`
- 英語用モデル：`facebook/bart-large-cnn`
