
import json
import hmac
import hashlib
import logging
from base64 import b64decode, b64encode
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric.padding import OAEP, MGF1, hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from global_varibles import APP_SECRET,PRIVATE_KEY_FILE_PASSWORD


logger=logging.getLogger(__name__)



PRIVATE_KEY_FILE = "private1.pem"
private_key_file_password=PRIVATE_KEY_FILE_PASSWORD

class PROCESS_WHATSAPP_DATA:
    def load_private_key(self):
        try:
            logger.debug("loading private key")
            with open(PRIVATE_KEY_FILE, "rb") as key_file:
                private_key = load_pem_private_key(key_file.read(), password=private_key_file_password, backend=default_backend())
            return private_key
        except Exception as e:
            logger.critical(f"Exception during loading of private key:{e}")
            raise e

    def decrypt_request(self, encrypted_flow_data_b64, encrypted_aes_key_b64, initial_vector_b64):
        try:
            logger.debug("decrypting the data")
            flow_data = b64decode(encrypted_flow_data_b64)
            iv = b64decode(initial_vector_b64)
            # Decrypt the AES encryption key
            encrypted_aes_key = b64decode(encrypted_aes_key_b64)
            private_key = self.load_private_key()
            aes_key = private_key.decrypt(encrypted_aes_key, OAEP(
                mgf=MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None))

            # Decrypt the Flow data
            encrypted_flow_data_body = flow_data[:-16]
            encrypted_flow_data_tag = flow_data[-16:]
            decryptor = Cipher(algorithms.AES(aes_key),
                            modes.GCM(iv, encrypted_flow_data_tag)).decryptor()
            decrypted_data_bytes = decryptor.update(
                encrypted_flow_data_body) + decryptor.finalize()
            decrypted_data = json.loads(decrypted_data_bytes.decode("utf-8"))
            return decrypted_data, aes_key, iv
        except Exception as e:
            logger.critical(f"Excption while decrypting the data:{e}")
            raise e

    def decrypt_data(self, encrypted_data, key, iv):
        try:
            backend = default_backend()
            cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=backend)
            decryptor = cipher.decryptor()
            decrypted_data = decryptor.update(encrypted_data[:-16]) + decryptor.finalize_with_tag(encrypted_data[-16:])
            return decrypted_data
        except Exception as e:
            logger.critical(f"Excption during decrypting of data:{e}")
            raise e

    def encrypt_response(self, response, aes_key, iv):
        try:
            logger.debug("encrypting the data")
            flipped_iv = bytearray()
            for byte in iv:
                flipped_iv.append(byte ^ 0xFF)

            # Encrypt the response data
            encryptor = Cipher(algorithms.AES(aes_key),
                            modes.GCM(flipped_iv)).encryptor()
            return b64encode(
                encryptor.update(json.dumps(response).encode("utf-8")) +
                encryptor.finalize() +
                encryptor.tag
            ).decode("utf-8")
        except Exception as e:
            logger.critical("Exception during encrypting of data:{e}")
            raise e

    def validate_signature(self, payload, signature):
        try:
            logger.debug("validating the signature")
            expected_signature = "sha256=" + hmac.new(APP_SECRET.encode(), payload, hashlib.sha256).hexdigest()
            logger.debug("signature verified successfully")
            return hmac.compare_digest(signature, expected_signature)
        except Exception as e:
            logger.error(f"Exception while handling the decrypted data :{e}")
            raise e
    

    


