#!/usr/bin/env python
from shellstream.shell import StreamingShell


if __name__ == "__main__":
    with StreamingShell() as shell:
        shell.stream()
