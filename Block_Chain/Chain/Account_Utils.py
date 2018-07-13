from Crypto import Random
from Crypto.Hash import SHA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_v1_5
from Crypto.Signature import PKCS1_v1_5 as Sign_v1_5
from Crypto.PublicKey import RSA
import base64
import os
import json

UserConfig = {}


# verify user valid
def verify_user(public_key, private_key):
    message = 'verify user'
    encrypt_text = encrypt_message(public_key, message)
    decrypt_text = decrypt_message(private_key, encrypt_text)
    return message == decrypt_text


# init environment , add path
def init_environment(dir_path=os.path.abspath('./account'), register=False):
    UserConfig['dir'] = dir_path
    UserConfig['local_file'] = os.path.join(UserConfig.get('dir'), 'account_local.chain')
    if os.path.exists(dir_path) and os.path.isdir(dir_path):
        if register:
            if os.path.exists(UserConfig['local_file']):
                return 'Error: your path is not exist or this path have used!!'
        return 'Success: your path is useful!!'
    return 'Error: your path is not exist or this path have used!!'


# save message to local file
def save_account(user_address, private_keys):
    user_info = {
        'user_address': user_address,
        'private_keys': private_keys,
    }
    with open(UserConfig.get('local_file'), 'w') as local_file:
        json.dump(obj=user_info, fp=local_file)


# load local file
def load_account():
    if not os.path.exists(UserConfig.get('local_file')):
        return None, None
    with open(UserConfig.get('local_file'), 'r') as local_file:
        user_info = json.load(fp=local_file)
    return user_info.get('user_address'), user_info.get('private_keys')


# generate key files
def generate_keys():
    random_master = Random.new().read
    rsa_master = RSA.generate(1024, random_master)
    private_pem = rsa_master.exportKey()
    public_pem = rsa_master.publickey().exportKey()
    return private_pem.decode(), public_pem.decode()


# encrypt a message use ghost public
def encrypt_message(encrypt_key, message):
    encrypt_rsa_key = RSA.importKey(encrypt_key.encode())
    encrypt_cipher = Cipher_v1_5.new(encrypt_rsa_key)
    return base64.b64encode(encrypt_cipher.encrypt(message.encode()))


# decrypt message from ghost_private
def decrypt_message(decrypt_key, decrypt_text):
    random_generator = Random.new().read
    decrypt_rsa_key = RSA.importKey(decrypt_key.encode())
    decrypt_cipher = Cipher_v1_5.new(decrypt_rsa_key)
    return decrypt_cipher.decrypt(base64.b64decode(decrypt_text), random_generator).decode()


# sign message from master private
def signature_message(signature_key, message):
    signature_rsa_key = RSA.importKey(signature_key.encode())
    signature_signer = Sign_v1_5.new(signature_rsa_key)
    signature_digest = SHA.new()
    signature_digest.update(message.encode())
    signature_sign = signature_signer.sign(signature_digest)
    return base64.b64encode(signature_sign)


# verify message from master public
def verify_signature(verify_key, signature_text, signature):
    verify_rsa_key = RSA.importKey(verify_key.encode())
    verify_verifier = Sign_v1_5.new(verify_rsa_key)
    digest = SHA.new()
    digest.update(signature_text.encode())
    return verify_verifier.verify(digest, base64.b64decode(signature))
