from django.http import HttpResponsePermanentRedirect
from django.conf import settings
import os

class HerokuRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # settings.pyで設定したHerokuのホスト名を取得
        heroku_host = os.getenv('HEROKU_HOSTNAME', None)
        # settings.pyで設定した正規の（新しい）ホスト名を取得
        canonical_host = os.getenv('CANONICAL_HOSTNAME', None)

        # 現在のリクエストのホスト名がHerokuのものと一致したらリダイレクト
        if request.get_host() == heroku_host:
            # 新しいURLを構築
            new_url = f"https://{canonical_host}{request.get_full_path()}"
            # 301リダイレクト（完全リダイレクト）を返す
            return HttpResponsePermanentRedirect(new_url)

        # ホスト名が違えば、通常通り次の処理へ
        response = self.get_response(request)
        return response