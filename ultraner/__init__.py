"""
Ultraner Python SDK
One API for payments across Africa: mobile money, cards, PayPal, wallets.
Docs: https://ultraner.com/docs  ·  Spec: https://ultraner.com/openapi.json
"""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Optional

__version__ = "0.1.0"
__all__ = ["Ultraner", "UltranerError"]


class UltranerError(Exception):
    def __init__(self, message: str, code: str = "ERROR", status: int = 0):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status = status


class _Resource:
    def __init__(self, client: "Ultraner"):
        self._c = client


class _Payments(_Resource):
    def create_mobile_money(self, **body: Any) -> dict:
        return self._c.request("POST", "/v1/payments/express/mno", body)

    def get_status(self, reference: str) -> dict:
        return self._c.request("GET", f"/v1/payments/express/status/{urllib.parse.quote(reference)}")


class _Disbursements(_Resource):
    def create(self, **body: Any) -> dict:
        return self._c.request("POST", "/v1/disbursements", body)


class _Wallet(_Resource):
    def get(self) -> dict:
        return self._c.request("GET", "/v1/wallet")

    def transfer(self, **body: Any) -> dict:
        return self._c.request("POST", "/v1/transfer", body)


class _Transactions(_Resource):
    def list(self, page: Optional[int] = None, limit: Optional[int] = None) -> dict:
        params = {k: v for k, v in {"page": page, "limit": limit}.items() if v is not None}
        qs = ("?" + urllib.parse.urlencode(params)) if params else ""
        return self._c.request("GET", f"/v1/transactions{qs}")


class _Escrow(_Resource):
    def create(self, **body: Any) -> dict:
        return self._c.request("POST", "/v1/escrow", body)

    def release(self, escrow_code: str) -> dict:
        return self._c.request("POST", f"/v1/escrow/{urllib.parse.quote(escrow_code)}/release")

    def list(self) -> dict:
        return self._c.request("GET", "/v1/escrow")


class _PayPal(_Resource):
    def create_order(self, **body: Any) -> dict:
        return self._c.request("POST", "/paypal/orders", body)

    def capture_order(self, order_id: str) -> dict:
        return self._c.request("POST", f"/paypal/orders/{urllib.parse.quote(order_id)}/capture")


class _Stripe(_Resource):
    def create_session(self, **body: Any) -> dict:
        return self._c.request("POST", "/stripe/sessions", body)


class Ultraner:
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.ultraner.com",
        timeout: float = 30.0,
    ):
        if not api_key:
            raise ValueError("Ultraner: an API key is required.")
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.payments = _Payments(self)
        self.disbursements = _Disbursements(self)
        self.wallet = _Wallet(self)
        self.transactions = _Transactions(self)
        self.escrow = _Escrow(self)
        self.paypal = _PayPal(self)
        self.stripe = _Stripe(self)

    def request(self, method: str, path: str, body: Optional[dict] = None) -> Any:
        data = json.dumps(body).encode("utf-8") if body is not None else None
        req = urllib.request.Request(
            f"{self.base_url}{path}",
            data=data,
            method=method,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                text = resp.read().decode("utf-8")
                payload = json.loads(text) if text else {}
                return payload.get("data", payload)
        except urllib.error.HTTPError as e:
            text = e.read().decode("utf-8") if e.fp else ""
            payload = json.loads(text) if text else {}
            raise UltranerError(
                payload.get("message", "Request failed"),
                payload.get("code", "ERROR"),
                e.code,
            ) from None
