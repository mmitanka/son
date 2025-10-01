import random
import logging
from logging_utils import setup_simulation_logging
import time
import datetime
from certificate_authority import CertificateAuthority
from message import Message
from node import Node

class Simulation:
    def __init__(self, N, m, source_type):
        self.N = N
        self.m = m
        st = str(source_type).strip().lower()
        self.source_type = "good" if st in ("1","good") else "faulty"
        self.ca = CertificateAuthority()
        self.nodes = []

    def setup(self, timestamp: str):
        # generisanje cvorova
        self.nodes = [Node(f"R{i}", self.ca, timestamp, is_faulty=False) for i in range(self.N)]

        # random odluka koliko ce biti faulty cvorova (0 do m)
        faulty_count = random.randint(0, self.m)

        # random odabir koji su cvorovi faulty
        faulty_nodes = random.sample(self.nodes, faulty_count)
        for node in faulty_nodes:
            node.is_faulty = True

        # dodavanje covrova u mrezu
        for node in self.nodes:
            node.network = [n for n in self.nodes if n is not node]

        if self.source_type == "good":
            candidates = [n for n in self.nodes if not n.is_faulty]
        else:
            candidates = [n for n in self.nodes if n.is_faulty]
            if not candidates:
                # ako nema nijednog faulty, obelezimo jedan random kao faulty
                chosen = random.choice(self.nodes)
                chosen.is_faulty = True
                candidates = [n for n in self.nodes if n.is_faulty]

        # izaberi izvor od mogucih kandidata iz prave liste
        self.source = random.choice(candidates)

    def run(self):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"simulation_{timestamp}.log"
        setup_simulation_logging(log_filename)
        logging.info("Simulacija Byzantine Generals problema...")
        self.setup(timestamp)
        logging.info(f"Izvor: {self.source.name} (faulty={self.source.is_faulty})")

        # originalna poruka
        original_value = random.randint(0, 1)
        logging.info(f"Originalna poruka: {original_value}")

        # izvor salje poruku svima
        recipients = [n for n in self.nodes if n != self.source]
        if not self.source.is_faulty:
            self.source.send_message(recipients=recipients, value=original_value)
        else:
            # pokvaren izvor – kvari poruke (doda sebe u path bez potpisa tako sam usvojila)
            for r in recipients:
                broken = Message(value=original_value, path=[], signatures=[])
                # namerno ne zovemo add_signature; verify ce pasti
                broken.path.append(self.source.name)
                logging.info(f"Cvor {self.source.name} (faulty) salje POKVARENU poruku -> {r.name}: {broken.serialize()}")
                r.receive_message(broken, self.source.name)

        # simulacija traje neko vreme dok se poruke prosledjuju (svako svakom treba da posalje)
        time.sleep(2)

        logging.info("=== Rezultati po cvorovima ===")
        for node in self.nodes:
            logging.info(f"Cvor {node.name} primljene poruke:")
            for sender, value, path in node.received_messages:
                # čist prikaz sa putanjom:
                logging.info(f"  od {sender} (putanja {':'.join(path)}): {value}")

        logging.info("=== Konacne odluke cvorova ===")
        for node in self.nodes:
            if node is self.source:
                decision = original_value  # izvor usvaja ono sto je poslao
            else:
                values = {val for (_, val, _) in node.received_messages}
                decision = values.pop() if len(values) == 1 else Node.DEFAULT_VALUE

            logging.info(f"{node.name} usvojio vrednost: {decision}")
            with open(node.log_file, "a", encoding="utf-8") as f:
                f.write(f"Konacna odluka: {decision}\n")