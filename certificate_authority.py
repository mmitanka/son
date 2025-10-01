from cryptography.hazmat.primitives.asymmetric import rsa

class CertificateAuthority:
    def __init__(self):
        self.keys = {}

    def publish_node_keys(self, node_name):
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        public_key = private_key.public_key()
        self.keys[node_name] = (private_key, public_key)
        return private_key, public_key

    def get_public_key(self, node_name):
        return self.keys[node_name][1]