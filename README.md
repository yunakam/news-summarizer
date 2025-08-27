# ニュース要約デモ

React (Next.js) + Django を用いたニュース記事要約デモアプリ。
ユーザーが入力した記事本文または URL を元に、要約と翻訳を行う。

---

## 機能概要

- **テキスト要約**  
  英語・日本語の記事をそれぞれ専用モデルで要約します。  

- **自動翻訳付き要約**  
  - 韓国語記事は日本語に翻訳してから要約  
  - それ以外の言語記事は英語に翻訳してから要約  
  - 出力言語がユーザー指定と異なる場合は、最終的に DeepL API で翻訳  

- **出力長さの選択**  
  「短め / 普通 / 長め」の 3 モードから要約文の長さを制御可能。  

- **UI 機能**  
  - テキスト入力 or URL入力  
  - 出力言語選択ドロップダウン  
  - 要約結果リスト表示（コピー・削除機能付き）  

---

## 要約処理の流れ

1. **page.tsx → route.ts**

   * ユーザーが本文 or URL を入力し、出力言語を選択して「要約」ボタンを押す。  
   * `page.tsx` 内で  
     ```ts
     fetch("/api/summarize", {
       method: "POST",
       body: JSON.stringify({ text, url, target_lang, length })
     })
     ```  
     が呼ばれる。  
   * このリクエストは Next.js 内部で `app/api/summarize/route.ts` にルーティングされる。  

2. **route.ts → Django**

   * `route.ts` の `POST` 関数で `req.json()` からデータを取得。  
   * それを `http://localhost:8000/summarizer/summarize/` へ転送する。  
   * ヘッダー `Content-Type: application/json` が付与されるため、Django 側で JSON として受け取れる。  

3. **Django内部処理（翻訳ルーティングあり）**

   * `views.py` の `summarize` 関数が呼ばれる。  
   * 以下の処理が行われる：  
     1. **言語検出**（原文の言語を推定）  
     2. **ルーティング**  
        - 原文が ja/en → そのまま対応モデルで要約  
        - 原文が ko → ja に翻訳して要約  
        - その他 → en に翻訳して要約  
     3. **要約実行**（英語モデル or 日本語モデル）  
     4. **最終翻訳**（出力言語が異なる場合は DeepL API で翻訳）  
   * 結果を JSON で返却：  
     ```json
     {
       "summary": "...",
       "detected_lang": "ja",
       "target_lang": "en",
       "pivoted": true
     }
     ```  

4. **route.ts → page.tsx**

   * Django から返ってきた JSON をそのまま `NextResponse.json(data)` でフロントへ返す。  

5. **page.tsx → UI 表示**

   * `summary` を state に格納し、画面に表示する。  
   * 併せて `detected_lang` や `target_lang` などの情報を利用可能。  

---

## まとめ

- **page.tsx** → `/api/summarize` に POST  
- **route.ts** → Django API (`http://localhost:8000/summarizer/summarize/`) に中継  
- **views.py** → 翻訳ルーティング → 要約モデル実行 → 必要なら翻訳 → JSON 返却  
- **route.ts** → JSON をフロントに返却  
- **page.tsx** → state に格納し、UI に表示  

---

## 開発環境

- **フロントエンド**: Next.js (React, TypeScript, TailwindCSS)  
- **バックエンド**: Django + Django REST Framework  
- **要約モデル**:  
  - 日本語: izumi-lab/ja-multi-news  
  - 英語: facebook/bart-large-cnn  
- **翻訳**: DeepL API (Free)  

---

## 今後の改善予定


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
