import sys


def main():
    print(
        "This entrypoint moved. Run one of the examples instead:\n"
        "  - python examples/cursor-control.py\n"
        "  - python examples/head-cursor.py (Linux + webcam)\n"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
