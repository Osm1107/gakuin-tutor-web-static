# Gakuin Tutor (早大学院生専用オンライン家庭教師)

## プロジェクト概要

「Gakuin Tutor」は、早稲田大学高等学院（早大学院）の生徒を対象とし、特に政治経済学部への内部進学に特化したオンライン家庭教師サービスのランディングページ（LP）およびシステムです。
講師全員が「学院から政経へ進学した現役早大生」であり、特考対策や第二外国語（ドイツ語・フランス語・ロシア語・中国語）の指導、そして評定管理に至るまで、内部進学に直結するサポートを提供します。

## 機能・特徴

- **洗練されたUI/UX**: HTML/CSS（Custom Styling）を使用した、スマートフォンに最適化されたFluid Layoutのランディングページ。
- **SEO・アナリティクス対応**: Google Analytics 4 (GA4) の導入および各種メタタグ（OGP, Twitter Cards）の最適化。
- **料金・比較セクション**: 各プランの体系的な表示と、他サービスとの具体的な差別化要因の比較機能。
- **問い合わせフォーム連携**:
  - Google reCAPTCHA v3/v2（カスタムコンポーネント）によるスパム対策。
  - Google Apps Script (GAS) Webhook エンドポイントを通した、お問い合わせデータの自動スプレッドシート連携。
  - Pythonの`smtplib`を利用したメール送信機能のバックエンド実装。

## 技術スタック

- **フロントエンド / フレームワーク**: Python, [Streamlit](https://streamlit.io/) (1ファイルアーキテクチャ)
- **スタイリング**: カスタムCSSブロック (Google Fonts: Noto Sans/Serif JP 利用, Fluid Typography)
- **外部連携 / API**:
  - `requests` (GASエンドポイントへのPOST通信)
  - `urllib` (reCAPTCHA v3 API 検証)
  - HTML Components (Custom Streamlit Component for reCAPTCHA)

## 環境構築と実行方法

1. **リポジトリの準備**
   ```bash
   cd "Online Teacher"
   ```

2. **依存関係のインストール**
   ```bash
   pip install -r requirements.txt
   ```

3. **シークレットの設定**
   `.streamlit/secrets.toml` ファイルを作成し、以下の情報を設定します（本番環境用）。
   ```toml
   [email]
   address = "your-email@gmail.com"
   password = "your-app-password"

   [recaptcha]
   site_key = "your-site-key"
   secret_key = "your-secret-key"
   ```

4. **アプリケーションの起動**
   ```bash
   streamlit run main.py
   ```

## 全体像の解説（アーキテクチャ）

システムの詳細な処理フローやUIコンポーネントの構造、インフラ構成については [ARCHITECTURE.md](./ARCHITECTURE.md) を参照してください。
