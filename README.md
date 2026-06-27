# Ultraner Python SDK

One API for payments across Africa: mobile money, cards, PayPal and wallets. Live in Tanzania and Rwanda, expanding across the continent.

- Docs: https://ultraner.com/docs
- OpenAPI: https://ultraner.com/openapi.json
- For AI: https://ultraner.com/ai

## Install

```bash
pip install ultraner
```

## Usage

```python
from ultraner import Ultraner

client = Ultraner(api_key="sk_live_...")

# Charge a mobile-money wallet
payment = client.payments.create_mobile_money(
    amount=5000,
    currency="TZS",
    provider="Vodacom",
    accountNumber="255700000000",
    externalId="order_1001",
)

# Poll status
status = client.payments.get_status(payment["reference"])

# Wallet, transactions
client.wallet.get()
client.transactions.list(page=1, limit=20)

# Escrow
escrow = client.escrow.create(amount=10000, currency="TZS", recipient="vendor@example.com")
client.escrow.release(escrow["escrowCode"])

# International payers
client.paypal.create_order(amount=25, currency="USD")
client.stripe.create_session(amount=2500, currency="usd")
```

Errors raise `ultraner.UltranerError` with `.status` and `.code`.

## License

MIT
