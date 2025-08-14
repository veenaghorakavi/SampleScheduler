from dataclasses import dataclass, field

@dataclass(frozen=True)
class Task:
    name : str
    duration: float
    dependencies: [str]

def main():
    return

if __name__ == "__main__":
    main()