import aiohttp
import logging
import io
import qrcode
from config import BINANCE_API_BASE_URL
import database

logger = logging.getLogger(__name__)

class BinancePaymentGateway:
    def __init__(self, base_url: str = BINANCE_API_BASE_URL):
        self.base_url = base_url.rstrip("/")

    async def get_api_key(self) -> str:
        api_key = await database.get_setting("binance_api_key")
        return api_key if api_key else "bg_live_your_merchant_api_key"

    async def _get_headers(self) -> dict:
        api_key = await self.get_api_key()
        return {
            "x-api-key": api_key,
            "Content-Type": "application/json"
        }

    async def create_payment(self, amount: float, user_id: int, goods_name: str = "Wallet Deposit", goods_detail: str = "") -> dict:
        """
        Creates a new payment invoice on Binance Pay & Multi-Chain API.
        """
        import time
        merchant_trade_no = f"DEP_{user_id}_{int(time.time())}"
        payload = {
            "orderAmount": f"{amount:.2f}",
            "currency": "USDT",
            "goodsName": goods_name,
            "goodsDetail": goods_detail or f"Deposit for Telegram User {user_id}",
            "merchantTradeNo": merchant_trade_no
        }

        url = f"{self.base_url}/api/v1/payments/create"
        headers = await self._get_headers()

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=20)) as resp:
                    data = await resp.json()
                    logger.info(f"Binance create payment response: {resp.status} - {data}")
                    
                    if resp.status in (200, 201) and data.get("success"):
                        order_info = data.get("order", {})
                        # Save to database
                        crypto_wallets = order_info.get("cryptoWallets", {})
                        await database.save_deposit(
                            merchant_trade_no=order_info.get("merchantTradeNo", merchant_trade_no),
                            user_id=user_id,
                            order_amount=amount,
                            currency=order_info.get("currency", "USDT"),
                            checkout_url=order_info.get("checkoutUrl", ""),
                            bep20_addr=crypto_wallets.get("bep20", ""),
                            trc20_addr=crypto_wallets.get("trc20", ""),
                            erc20_addr=crypto_wallets.get("erc20", ""),
                            status=order_info.get("status", "INITIAL")
                        )
                        return {
                            "success": True,
                            "order": order_info
                        }
                    else:
                        err_msg = data.get("message") or data.get("error") or f"HTTP {resp.status} error"
                        return {
                            "success": False,
                            "message": err_msg,
                            "data": data
                        }
        except Exception as e:
            logger.error(f"Error calling Binance create payment API: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"Connection error: {str(e)}"
            }

    async def get_payment_status(self, merchant_trade_no: str) -> dict:
        """
        Queries status of an existing order.
        """
        url = f"{self.base_url}/api/v1/payments/{merchant_trade_no}"
        headers = await self._get_headers()

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                    data = await resp.json()
                    logger.info(f"Binance query payment response: {resp.status} - {data}")
                    if resp.status == 200 and data.get("success"):
                        return {
                            "success": True,
                            "order": data.get("order", {})
                        }
                    else:
                        err_msg = data.get("message") or data.get("error") or f"HTTP {resp.status} error"
                        return {
                            "success": False,
                            "message": err_msg,
                            "data": data
                        }
        except Exception as e:
            logger.error(f"Error querying payment status {merchant_trade_no}: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"Connection error: {str(e)}"
            }

    async def submit_tx_hash(self, merchant_trade_no: str, network: str, tx_hash: str) -> dict:
        """
        Submits on-chain txHash verification for BEP20, TRC20, ERC20.
        """
        url = f"{self.base_url}/api/v1/payments/submit-tx"
        headers = await self._get_headers()
        payload = {
            "merchantTradeNo": merchant_trade_no,
            "network": network,
            "txHash": tx_hash.strip()
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=20)) as resp:
                    data = await resp.json()
                    logger.info(f"Binance submit tx hash response: {resp.status} - {data}")
                    if resp.status in (200, 201) and data.get("success"):
                        await database.update_deposit_tx_hash(merchant_trade_no, tx_hash, network)
                        return {
                            "success": True,
                            "message": data.get("message", "TxHash submitted successfully"),
                            "data": data
                        }
                    else:
                        err_msg = data.get("message") or data.get("error") or f"HTTP {resp.status} error"
                        return {
                            "success": False,
                            "message": err_msg,
                            "data": data
                        }
        except Exception as e:
            logger.error(f"Error submitting tx hash for {merchant_trade_no}: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"Connection error: {str(e)}"
            }

def generate_qr_image(text: str) -> io.BytesIO:
    """
    Generates a QR code PNG image in memory for an address or URL.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=3,
    )
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    bio = io.BytesIO()
    img.save(bio, format="PNG")
    bio.seek(0)
    return bio

payment_gateway = BinancePaymentGateway()
