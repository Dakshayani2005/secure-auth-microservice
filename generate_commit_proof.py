import subprocess
import base64

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend


def get_latest_commit_hash() -> str:
    """Get latest commit hash as 40-character hex string."""
    result = subprocess.run(
        ["git", "log", "-1", "--format=%H"],
        capture_output=True,
        text=True,
        check=True,
    )
    commit_hash = result.stdout.strip()
    if len(commit_hash) != 40:
        raise ValueError(f"Unexpected commit hash length: {commit_hash}")
    return commit_hash


def load_private_key(path: str):
    with open(path, "rb") as f:
        data = f.read()
    return serialization.load_pem_private_key(
        data,
        password=None,
        backend=default_backend()
    )


def load_public_key(path: str):
    with open(path, "rb") as f:
        data = f.read()
    return serialization.load_pem_public_key(
        data,
        backend=default_backend()
    )


def sign_message(message: str, private_key) -> bytes:
    """
    Sign message using RSA-PSS with SHA-256.

    - Sign the ASCII/UTF-8 bytes of the commit hash (string).
    """
    message_bytes = message.encode("utf-8")
    signature = private_key.sign(
        message_bytes,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH,
        ),
        hashes.SHA256(),
    )
    return signature


def encrypt_with_public_key(data: bytes, public_key) -> bytes:
    """
    Encrypt data using RSA/OAEP with SHA-256.
    """
    ciphertext = public_key.encrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )
    return ciphertext


def main():
    # 1. Get current commit hash
    commit_hash = get_latest_commit_hash()

    # 2. Load student private key
    student_private_key = load_private_key("student_private.pem")

    # 3. Sign commit hash (ASCII) with RSA-PSS-SHA256
    signature = sign_message(commit_hash, student_private_key)

    # 4. Load instructor public key
    instructor_public_key = load_public_key("instructor_public.pem")

    # 5. Encrypt signature with instructor public key (RSA/OAEP-SHA256)
    encrypted_signature = encrypt_with_public_key(signature, instructor_public_key)

    # 6. Base64 encode encrypted signature
    encrypted_signature_b64 = base64.b64encode(encrypted_signature).decode("ascii")

    print("Commit Hash:")
    print(commit_hash)
    print("\nEncrypted Signature (Base64):")
    print(encrypted_signature_b64)


if __name__ == "__main__":
    main()
