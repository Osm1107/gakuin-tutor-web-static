# 全体像とアーキテクチャ (Architecture Overview)

このドキュメントでは、「Gakuin Tutor (Online Teacher)」のシステム構成、データフロー、およびUIアーキテクチャについて詳細に解説します。

## 1. システムアーキテクチャ構成

本アプリケーションは、Pythonのフレームワークである**Streamlit**をベースに構築されたモノリシックなWebアプリケーションです。単一の `main.py` ファイル内で、ルーティング（SEO用）、UIレンダリング、CSSの注入、およびバックエンド処理（フォーム送信）のすべてを完結させています。

```mermaid
graph TD
    User([ユーザー (生徒・保護者)]) -->|ブラウザ| StreamlitApp(Streamlit App : main.py)
    
    subgraph Streamlit Frontend
        Hero[Hero Section]
        PainPoints[Pain Points / 悩み]
        Features[強み / Features]
        Instructors[講師陣 / Instructors]
        Pricing[料金プラン / Pricing]
        ContactForm[問い合わせフォーム / Contact]
    end
    
    StreamlitApp --> Hero
    StreamlitApp --> PainPoints
    StreamlitApp --> Features
    StreamlitApp --> Instructors
    StreamlitApp --> Pricing
    StreamlitApp --> ContactForm
    
    subgraph External APIs & Services
        reCAPTCHA[Google reCAPTCHA API]
        GAS[Google Apps Script]
        Sheets[(Google SpreadSheets)]
        SMTP[Google SMTP / Gmail]
        GA4[Google Analytics 4]
    end
    
    ContactForm -->|1. トークン生成| reCAPTCHA
    ContactForm -->|2. 検証リクエスト| reCAPTCHA
    ContactForm -->|3. POST Request| GAS
    GAS -->|4. データ保存| Sheets
    ContactForm -.->|バックアップ送信| SMTP
    StreamlitApp -->|トラッキング| GA4
```

## 2. UI / コンポーネント構造 (`main.py`)

UIは関数ベースでセクションごとにコンポーネント化されています。

1. **ページ設定とSEO最適化** (`st.set_page_config`, `_gsv_request`)
   - Google Search Consoleの所有権確認用ルーティングや、GA4のトラッキングコードを最上部に注入しています。
2. **デザインシステム・CSSの注入** (`local_css()`)
   - `<style>` タグを用いて、早稲田カラー（えんじ色: `--waseda-red`）を基調としたCSS変数を定義。
   - レスポンシブ対応として `@media (max-width: 768px)` のブレイクポイントを設定し、PC/モバイルそれぞれに最適化されたFluid Typography（`clamp()` 関数など）を採用しています。
3. **Hero Section** (`hero_section()`)
   - ファーストビュー。キャッチコピーとCTA（各種セクションへのアンカーリンクスクロール）を配置しています。
4. **Pain Points & Features** (`pain_points_section()`, `features_section()`)
   - 保護者の悩みへの共感と、Gakuin Tutorならではの実績（評定85点以上など）を説明するエリア。
5. **Instructors & Comparison** (`instructors_section()`, `comparison_section()`)
   - 現役の講師プロフィールをカード形式で表示し、大手家庭教師センターとの違いをテーブルで比較しています。
6. **Flow, FAQ & Pricing** (`flow_section()`, `faq_section()`, `pricing_section()`)
   - サービスの流れ、よくある質問（アコーディオンUI）、および3段階（スタンダード・プレミアム・プラチナ）の料金プランを提示します。
7. **Contact Section** (`contact_section()`)
   - Streamlitの `st.form` を活用した問い合わせフォーム。

## 3. データフローとフォーム処理

ユーザーが問い合わせフォームから情報を送信する際のフローは以下の通りです：

1. **入力とバリデーション**:
   - 名前、メールアドレス、学年、志望学部、希望科目、希望日時などの必須項目をバリデーション。
2. **bot対策 (reCAPTCHA)**:
   - カスタムコンポーネントを使用してフロントエンドでreCAPTCHAトークンを取得。
   - `urllib.request` を経由してGoogleのAPIサーバでスコアを検証（サーバーサイド検証）。
3. **スプレッドシート連携 (GAS Webhook)**:
   - 検証成功後、`requests.post()` を使って Google Apps Script (GAS) のエンドポイント（Webhook URL）にJSONペイロードを送信。
   - 連携が成功した場合のみ、UI上に「成功メッセージ」を表示します。
4. **メール通知・バックアップ (実装済み/拡張可能)**:
   - 環境によって `smtplib` と `email.mime` モジュールを利用した `send_email` 関数を実行し、システム管理者宛の通知メールをセキュア（STARTTLS）に送信する仕組みが組み込まれています。

## 4. 将来の拡張性とメンテナンス

- **コンテンツの分離**: 現在はすべてのテキストや設定値がコード（`main.py`）にハードコードされていますが、JSONやYAML等の外部ファイル、またはデータベース（Supabase/Firebaseなど）へ分離することで保守性が向上します。
- **Streamlitのステート管理**: パフォーマンスやUX向上のため、`st.session_state` を活用したページネーションや、より複雑な状態管理への移行が可能です。
