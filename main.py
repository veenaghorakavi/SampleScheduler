#!/usr/bin/env python3
from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Iterator, Dict, List
from collections import OrderedDict


@dataclass
class Task:
    name: str
    duration_seconds: float
    deps: List[str]


@dataclass
class TaskSet:
    tasks: Dict[str, Task]
    order: List[str]

    def __iter__(self):
        for name in self.order:
            yield self.tasks[name]


def _parse_deps(fields: List[str]):
    #find dependencies
    if len(fields) < 3:
        return []
    dep_field = ",".join(fields[2:]).strip()
    if not dep_field or dep_field == "-":
        return []
    seen = set()
    ordered: List[str] = []
    for token in dep_field.split(","):
        dep = token.strip()
        if dep and dep not in seen:
            seen.add(dep)
            ordered.append(dep)
    return ordered


def parse_task_line(line: str):
    #parse each task from the text file
    raw = line.strip()
    if not raw or raw.startswith("#"):
        print("Skipping line:", line.rstrip(), flush=True)
        return None

    fields = [field.strip() for field in raw.split(",")]
    print("Fields parsed:", fields, flush=True)

    name = fields[0]
    duration = float(fields[1])
    deps = _parse_deps(fields)
    print("Created Task: name=" + name + ", duration=" + str(duration) + ", deps=" + str(deps), flush=True)
    return Task(name=name, duration_seconds=duration, deps=deps)


def load_tasks_from_text(path: Path):
    #working on the text model
    print("Loading tasks from:", path, flush=True)
    by_name: "OrderedDict[str, Task]" = OrderedDict()
    order: List[str] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            print("Reading line:", line.rstrip(), flush=True)
            task = parse_task_line(line)
            if task is None:
                continue
            by_name[task.name] = task
            order.append(task.name)
            print("Task '" + task.name + "' added to TaskSet.", flush=True)
    print("Total tasks loaded:", len(by_name), flush=True)
    return TaskSet(tasks=dict(by_name), order=order)


def build_arg_parser():
    #create parser
    parser = argparse.ArgumentParser(
        description="Parse a text task file into a structured model."
    )
    parser.add_argument(
        "task_file",
        type=Path,
        help="Path to the task list."
    )
    parser.add_argument(
        "--print",
        dest="do_print",
        action="store_true",
        help="Print parsed tasks to stdout (for inspection)."
    )
    return parser


def main(argv: Iterable[str] | None = None):
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    task_set = load_tasks_from_text(args.task_file)

    if args.do_print:
        print("Loaded", len(task_set.tasks), "task(s) from", args.task_file, ":", flush=True)
        for t in task_set:
            deps_str = ", ".join(t.deps) if t.deps else "-"
            print("  - " + t.name + ": duration=" + str(t.duration_seconds) + "s, deps=[" + deps_str + "]", flush=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
