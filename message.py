from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
import base64

class Message:
    def __init__(self, value, path=None, signatures=None):
        self.value = value
        self.path = path or []
        self.signatures = signatures or []  # lista potpisa redom

    def _data_for_node(self, node_name):
        # svaki potpis pokriva vrednost trenutnu putanju i nadovezano novo ime
        path_with_me = self.path + [node_name]
        return f"{self.value}|{':'.join(path_with_me)}".encode()

    def add_signature(self, private_key, node_name):
        data = self._data_for_node(node_name)
        sig = private_key.sign(
            data,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        self.path.append(node_name)
        self.signatures.append(sig)

    def verify_and_decrypt(self, ca):
        
        # za i-ti element u putanji koristi i-ti potpis
        # i string "{value}|{path_do_i-tog}".
        # ako ne uspe dekripcija vrati none
        try:
            if len(self.signatures) != len(self.path):
                return None
            for i, node_name in enumerate(self.path):
                public_key = ca.get_public_key(node_name)
                data = f"{self.value}|{':'.join(self.path[:i+1])}".encode()
                public_key.verify(
                    self.signatures[i],
                    data,
                    padding.PKCS1v15(),
                    hashes.SHA256()
                )
            return self.value  # sve ok, vracamo orig vrednost
        except Exception:
            return None

    def serialize(self):
        # prikazi skraceni poslednji potpis (base64) + @#@ + putanja
        if self.signatures:
            b64 = base64.b64encode(self.signatures[-1]).decode()
            short = (b64[:16] + "…") if len(b64) > 16 else b64
        else:
            short = "-"
        return f"{short}@#@{':'.join(self.path)}"

    def __str__(self):
        return f"{'.'.join(self.path)}.({self.value})"