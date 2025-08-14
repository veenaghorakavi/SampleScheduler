from dataclasses import dataclass, field
import argparse

@dataclass(frozen=True)
class Task:
    name : str
    duration: float
    dependencies: [str]

def main():
    return

def build_arg_parser():
    #hHandles running tasks at the moment. 
    argparser = argparse.ArgumentParser(description="Scheduler")
    argparser.add_argument("-f", "--file", default="-", help="Task list or '-' for stdin")
    argparser.add_argument("--format", choices=["text", "json"], default="text")
    argparser.add_argument("--run", action="store_true", help="Run tasks")
    return argparser

if __name__ == "__main__":
    main()