import sys
from simulation import Simulation

def main():
    if len(sys.argv) < 4:
        print("Ispravan format komande: python main.py N m tip_izvora")
        print("tip_izvora: 1 ili good | 0 ili bad")
        sys.exit(1)

    N = int(sys.argv[1])
    m = int(sys.argv[2])
    source_type = sys.argv[3]

    sim = Simulation(N, m, source_type)
    sim.run()

if __name__ == "__main__":
    main()