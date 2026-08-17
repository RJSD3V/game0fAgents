from .simulation import NeuroSymbolicSimulation


def main() -> None:
    simulation = NeuroSymbolicSimulation.default()
    for _ in range(3):
        snapshot = simulation.step()
        print(snapshot.to_dict())


if __name__ == "__main__":
    main()
