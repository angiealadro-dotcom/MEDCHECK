import base64
import json
import os
from typing import Dict, Optional

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.backends import default_backend
from pywebpush import webpush, WebPushException

from sqlalchemy.orm import Session
from app.models.notification import WebPushSubscription


VAPID_FILE = os.path.join(os.getcwd(), "vapid_keys.json")


class PushService:
    def __init__(self):
        self._keys = self._load_or_create_vapid_keys()

    def _load_or_create_vapid_keys(self) -> Dict[str, str]:
        # Prefer env vars if provided
        priv_pem_env = os.getenv("VAPID_PRIVATE_KEY_PEM")
        pub_b64_env = os.getenv("VAPID_PUBLIC_KEY_B64")
        if priv_pem_env and pub_b64_env:
            # Derivar DER base64url (sin padding) para compatibilidad con pywebpush
            try:
                private_key = serialization.load_pem_private_key(
                    priv_pem_env.encode("utf-8"), password=None, backend=default_backend()
                )
                der = private_key.private_bytes(
                    encoding=serialization.Encoding.DER,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption(),
                )
                priv_b64 = base64.urlsafe_b64encode(der).decode("utf-8").rstrip("=")
            except Exception:
                priv_b64 = ""
            return {"private_pem": priv_pem_env, "private_b64": priv_b64, "public_b64": pub_b64_env}

        # Load from file if exists
        if os.path.exists(VAPID_FILE):
            try:
                with open(VAPID_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if "private_pem" in data and "public_b64" in data:
                        # Asegurar que exista private_b64
                        if "private_b64" not in data or not data["private_b64"]:
                            try:
                                pk = serialization.load_pem_private_key(
                                    data["private_pem"].encode("utf-8"), password=None, backend=default_backend()
                                )
                                der = pk.private_bytes(
                                    encoding=serialization.Encoding.DER,
                                    format=serialization.PrivateFormat.PKCS8,
                                    encryption_algorithm=serialization.NoEncryption(),
                                )
                                data["private_b64"] = base64.urlsafe_b64encode(der).decode("utf-8").rstrip("=")
                            except Exception:
                                data["private_b64"] = ""
                        return data
            except Exception:
                pass

        # Generate new keys
        private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ).decode("utf-8")

        public_key = private_key.public_key()
        # Encode as uncompressed EC point per VAPID/browser requirement
        numbers = public_key.public_numbers()
        x = numbers.x.to_bytes(32, "big")
        y = numbers.y.to_bytes(32, "big")
        uncompressed = b"\x04" + x + y
        public_b64 = base64.urlsafe_b64encode(uncompressed).decode("utf-8").rstrip("=")

        # También guardar el privado en DER base64url (sin padding) requerido por pywebpush/py_vapid
        private_der = private_key.private_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
        private_b64 = base64.urlsafe_b64encode(private_der).decode("utf-8").rstrip("=")

        keys = {"private_pem": private_pem, "private_b64": private_b64, "public_b64": public_b64}
        try:
            with open(VAPID_FILE, "w", encoding="utf-8") as f:
                json.dump(keys, f)
        except Exception:
            pass
        return keys

    def get_public_key(self) -> str:
        return self._keys["public_b64"]

    def save_subscription(self, db: Session, user_id: int, sub: Dict) -> WebPushSubscription:
        endpoint = sub.get("endpoint")
        keys = sub.get("keys", {})
        p256dh = keys.get("p256dh")
        auth = keys.get("auth")
        if not (endpoint and p256dh and auth):
            raise ValueError("Suscripción inválida")

        existing = db.query(WebPushSubscription).filter(WebPushSubscription.endpoint == endpoint).first()
        if existing:
            existing.user_id = user_id
            existing.p256dh = p256dh
            existing.auth = auth
            db.add(existing)
            db.commit()
            db.refresh(existing)
            return existing

        rec = WebPushSubscription(
            user_id=user_id,
            endpoint=endpoint,
            p256dh=p256dh,
            auth=auth,
        )
        db.add(rec)
        db.commit()
        db.refresh(rec)
        return rec

    def send(self, subscription: WebPushSubscription, payload: Dict) -> Optional[str]:
        def _try_send(vapid_key: str) -> Optional[str]:
            try:
                webpush(
                    subscription_info={
                        "endpoint": subscription.endpoint,
                        "keys": {"p256dh": subscription.p256dh, "auth": subscription.auth},
                    },
                    data=json.dumps(payload),
                    vapid_private_key=vapid_key,
                    vapid_claims={"sub": "mailto:admin@medcheck.local"},
                )
                return None
            except WebPushException as e:
                return str(e)
            except Exception as e:
                return str(e)

        # Prefer b64 DER. If it fails, try SEC1 DER derived from PEM.
        b64_pkcs8 = self._keys.get("private_b64")
        pem = self._keys.get("private_pem")
        try:
            preview = f"b64:{len(b64_pkcs8 or '')} pem:{len(pem or '')}"
            print(f"[PUSH] Using VAPID key ({preview})")
        except Exception:
            pass

        err = None
        if b64_pkcs8:
            err = _try_send(b64_pkcs8)
            if not err:
                return None

        # Fallback: TraditionalOpenSSL (SEC1) DER base64url
        if pem:
            try:
                pk = serialization.load_pem_private_key(pem.encode("utf-8"), password=None, backend=default_backend())
                der_sec1 = pk.private_bytes(
                    encoding=serialization.Encoding.DER,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=serialization.NoEncryption(),
                )
                b64_sec1 = base64.urlsafe_b64encode(der_sec1).decode("utf-8").rstrip("=")
                err2 = _try_send(b64_sec1)
                if not err2:
                    # cache this variant for future sends
                    self._keys["private_b64"] = b64_sec1
                    return None
                return err2
            except Exception as e:
                return str(e)

        # If all failed, return the last error
        return err or "unknown vapid key error"
