# Zero Market

PDF 발표 자료의 아이디어를 바탕으로 만든 가상 쇼핑몰 앱입니다.

- 키워드를 입력해 원하는 가상 상품을 생성하고, 함께 보여줄 상품 구성을 새로 만듭니다.
- 상품 데이터는 `data/products.json`에 저장됩니다.
- 기본 상품 이미지는 DummyJSON 공개 상품 API에서 불러오고, 사용자가 입력한 상품은 Openverse 공개 이미지 API에서 불러옵니다.
- 상품 탐색, 상세 페이지, 장바구니, 실제 결제 없는 가상 결제 흐름을 제공합니다.

## 실행

```bash
python3 app.py
```

브라우저에서 `http://127.0.0.1:5000`을 엽니다.

## Render 배포

Render에서 `New +` -> `Web Service`를 선택하고 GitHub 저장소를 연결한 뒤 아래 값으로 배포합니다.

- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn app:app`
- Instance Type: `Free`
