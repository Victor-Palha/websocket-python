import uuid
import qrcode


class Pix:
    def __init__(self):
        pass

    @staticmethod
    def create_payment(base_dir=""):
        bank_payment_id = str(uuid.uuid4())
        hash_payment = f"hash_payment_{bank_payment_id}"

        img = qrcode.make(hash_payment)
        qr_code_path = f"qr_code_{bank_payment_id}.png"
        img.save(f"{base_dir}static/img/{qr_code_path}")
        return {
            "bank_payment_id": bank_payment_id,
            "qr_code_path": qr_code_path
        }
