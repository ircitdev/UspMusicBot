import json
from typing import Optional, Dict
from loguru import logger

PACKAGES = {
    "starter": {"name": "Стартовый", "credits": 10, "price": 299.00, "currency": "RUB"},
    "popular": {"name": "Популярный", "credits": 30, "price": 799.00, "currency": "RUB"},
    "pro": {"name": "Профессионал", "credits": 100, "price": 1999.00, "currency": "RUB"},
}


class PaymentService:
    def __init__(
        self,
        yookassa_shop_id: str = "",
        yookassa_secret_key: str = "",
        cryptobot_token: str = "",
        return_url: str = "https://t.me/UspMusicBot",
    ):
        self.return_url = return_url
        self._yookassa_enabled = bool(yookassa_shop_id and yookassa_secret_key)
        self._cryptobot_enabled = bool(cryptobot_token)

        if self._yookassa_enabled:
            try:
                from yookassa import Configuration
                Configuration.account_id = yookassa_shop_id
                Configuration.secret_key = yookassa_secret_key
                logger.info("YooKassa payment configured")
            except ImportError:
                logger.warning("yookassa package not installed")
                self._yookassa_enabled = False

    def get_packages(self) -> Dict[str, dict]:
        return PACKAGES

    def get_package(self, package_id: str) -> Optional[dict]:
        return PACKAGES.get(package_id)

    async def create_yookassa_payment(
        self,
        user_id: int,
        package_id: str,
    ) -> Optional[Dict]:
        if not self._yookassa_enabled:
            logger.warning("YooKassa not configured")
            return None

        package = self.get_package(package_id)
        if not package:
            return None

        try:
            from yookassa import Payment
            payment = Payment.create({
                "amount": {
                    "value": f"{package['price']:.2f}",
                    "currency": package["currency"],
                },
                "confirmation": {
                    "type": "redirect",
                    "return_url": self.return_url,
                },
                "capture": True,
                "description": f"Пакет '{package['name']}' — {package['credits']} треков",
                "metadata": {
                    "user_id": str(user_id),
                    "package_id": package_id,
                    "credits": str(package["credits"]),
                },
            })
            return {
                "payment_id": payment.id,
                "confirmation_url": payment.confirmation.confirmation_url,
                "amount": package["price"],
                "credits": package["credits"],
            }
        except Exception as e:
            logger.error(f"YooKassa payment creation failed: {e}")
            return None

    async def verify_yookassa_webhook(self, payload: dict) -> Optional[Dict]:
        try:
            from yookassa.domain.notification import WebhookNotification
            notification = WebhookNotification(payload)
            payment = notification.object

            if payment.status == "succeeded":
                metadata = payment.metadata or {}
                return {
                    "payment_id": payment.id,
                    "user_id": int(metadata.get("user_id", 0)),
                    "credits": int(metadata.get("credits", 0)),
                    "amount": float(payment.amount.value),
                    "currency": payment.amount.currency,
                    "status": "succeeded",
                }
        except Exception as e:
            logger.error(f"YooKassa webhook verification failed: {e}")
        return None

    async def create_cryptobot_payment(self, user_id: int, package_id: str) -> Optional[Dict]:
        logger.warning("CryptoBot payments not yet implemented")
        return None

    def format_package_text(self, package_id: str, package: dict) -> str:
        cost_per_track = package["price"] / package["credits"]
        return (
            f"📦 *{package['name']}*\n"
            f"🎵 {package['credits']} треков\n"
            f"💰 {package['price']:.0f}₽ (~{cost_per_track:.0f}₽/трек)"
        )
