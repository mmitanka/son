import logging
from message import Message
from certificate_authority import CertificateAuthority

class Node:
    DEFAULT_VALUE = 0.5

    def __init__(self, name: str, ca: CertificateAuthority, timestamp: str, is_faulty: bool = False):
        self.name = name
        self.private_key, self.public_key = ca.publish_node_keys(name)
        self.ca = ca
        self.is_faulty = is_faulty
        self.received_messages = []
        self.log_file = f"logs/{self.name}_{timestamp}.txt"
        self.network = []  # popunjava Simulation.setup()

    # inicijalno slanje ili prosledjivanje (ujedinjeno)
    def send_message(self, recipients, msg: Message = None, value=None):
        if msg is None:
            # spec slucaj: izvor napravi novu poruku (prazan path; add_signature će upisati self.name)
            msg = Message(value=value, path=[], signatures=[])

        # kopija poruke da ne menjamo original
        forwarded_msg = Message(
            value=msg.value,
            path=list(msg.path),
            signatures=list(msg.signatures)
        )

        # dodajemo potpis i ime cvora
        forwarded_msg.add_signature(self.private_key, self.name)

        # log
        if len(forwarded_msg.path) == 1:
            # pocetna poruka
            targets = [r.name for r in recipients if r.name not in forwarded_msg.path]
            logging.info(f"Cvor {self.name} salje pocetnu poruku {forwarded_msg.value} -> {targets}")
        else:
            targets = [r.name for r in recipients if r.name not in forwarded_msg.path]
            logging.info(f"Cvor {self.name} prosledjuje {forwarded_msg.serialize()} -> {targets}")

        # posalji dalje svima koji nisu vec u putanji
        for r in recipients:
            # prosledi svima samo ne meni opet (ako nisam u putanji)
            if r.name not in forwarded_msg.path:
                r.receive_message(forwarded_msg, self.name)

    def receive_message(self, msg: Message, sender_name):
        # verifikuj lanac potpisa, ako padne dodeli podrazumevanu poruku
        value = msg.verify_and_decrypt(self.ca)
        if value is None:
            value = Node.DEFAULT_VALUE

        # zapamti sta je cvor "verovao" da je primio
        self.received_messages.append((sender_name, value, list(msg.path)))
        logging.info(f"{self.name} primio {msg.serialize()} od {sender_name}")

        # upis u svoj log fajl
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(f"Primljeno od {sender_name}: {msg.serialize()} -> vrednost: {value}\n")

        # nakon sto primi poruku
        if not self.is_faulty:
            # prosledi dalje svima koji nisu u putanji
            recipients = [n for n in self.network if n.name not in msg.path]
            self.send_message(recipients=recipients, msg=msg)
        else:
            # faulty: pokvari poruku tako da verifikacija nuzno padne
            broken_msg = Message(
                value=msg.value,
                path=list(msg.path),
                signatures=list(msg.signatures)
            )
            # dodaj svoje ime u path, ali bez potpisa verify ce pasti (mismatch path/signatures)
            broken_msg.path.append(self.name)

            logging.info(f"Cvor {self.name} (faulty) salje pokvarenu poruku: {broken_msg.serialize()}")
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(f"{self.name} (faulty) poslao: {broken_msg.serialize()}\n")

            for r in self.network:
                if r.name not in broken_msg.path:
                    r.receive_message(broken_msg, self.name)