from OpenSSL import crypto
import os

# Create a directory for certificates if it doesn't exist
if not os.path.exists("certs"):
    os.makedirs("certs")

# Generate a self-signed certificate
def generate_self_signed_cert(cert_dir="certs"):
    # Create a key pair
    k = crypto.PKey()
    k.generate_key(crypto.TYPE_RSA, 2048)
    
    # Create a self-signed certificate
    cert = crypto.X509()
    cert.get_subject().CN = "localhost"
    cert.set_serial_number(1000)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(10 * 365 * 24 * 60 * 60)  # 10 years validity
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(k)
    cert.sign(k, "sha256")

    # Save the private key and certificate to files
    with open(os.path.join(cert_dir, "server.key"), "wb") as key_file:
        key_file.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k))
    with open(os.path.join(cert_dir, "server.crt"), "wb") as cert_file:
        cert_file.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))

generate_self_signed_cert()
print("Self-signed certificate generated successfully.")
