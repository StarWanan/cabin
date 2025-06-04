import re
from collections import defaultdict


def parse_log_file(log_file_path):
    pattern = re.compile(r'\[A\* Route\].*原因：(.*)')

    reason_count = defaultdict(int)

    with open(log_file_path, 'r') as file:
        for line in file:
            match = pattern.search(line)
            if match:
                reason = match.group(1).strip()
                reason_count[reason] += 1

    return reason_count


def print_reason_statistics(reason_count):
    print("原因\t条数")
    for reason, count in reason_count.items():
        print(f"{reason}\t{count}")


if __name__ == "__main__":
    log_file_path = 'log_20250604_212035.txt'
    reason_count = parse_log_file(log_file_path)
    print_reason_statistics(reason_count)