# harusmile バックエンドリポジトリ

## 使用技術

- Django
- Graphene
- Heroku

## TODO

- 開発環境と本番環境の差異
- 本番環境のための設定変更
  - DB
  - 画像ファイル

## 認証フローのメモ

email, password でユーザー作成後、メールで token つき URL を送信。
クリック後、本人確認の更新をする。
その後もう一度メールアドレスとパスワードで認証？
