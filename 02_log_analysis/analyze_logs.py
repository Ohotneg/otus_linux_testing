import os
import re
import json
import argparse


METHODS = {"GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"}

PATTERN = re.compile(
    r'(?P<ip>\S+) \S+ \S+ '
    r'\[(?P<date>[^\]]+)\] '
    r'"(?P<request>(?:\\.|[^"\\])*)" '
    r'(?P<status>\d{3}) \S+ '
    r'"(?:\\.|[^"\\])*" "(?:\\.|[^"\\])*" '
    r'(?P<duration>\d+)'
)


def analyze_log_file(file_path):
    total_stat = {}
    total_requests = 0
    ip_stat = {}
    top_longest = []

    with open(file_path, "r", encoding="utf-8", errors="replace") as log_file:
        for log_line in log_file:
            match = PATTERN.fullmatch(log_line.rstrip("\r\n"))

            if not match:
                continue

            data = match.groupdict()
            total_requests += 1

            ip = data["ip"]
            ip_stat[ip] = ip_stat.get(ip, 0) + 1

            request_parts = data["request"].split(maxsplit=2)

            if len(request_parts) < 2:
                continue

            method = request_parts[0].upper()
            url = request_parts[1]

            if method in METHODS:
                total_stat[method] = total_stat.get(method, 0) + 1

            duration = int(data["duration"])

            request_info = {
                "ip": ip,
                "date": f'[{data["date"]}]',
                "method": method,
                "url": url,
                "duration": duration,
            }

            if len(top_longest) < 3:
                top_longest.append(request_info)
            elif duration > top_longest[-1]["duration"]:
                top_longest[-1] = request_info

            top_longest.sort(
                key=lambda item: item["duration"],
                reverse=True,
            )

    top_ips = dict(
        sorted(
            ip_stat.items(),
            key=lambda item: item[1],
            reverse=True,
        )[:3]
    )

    result = {
        "top_ips": top_ips,
        "top_longest": top_longest,
        "total_stat": total_stat,
        "total_requests": total_requests,
    }

    return result


def save_result(result, output_path):
    with open(output_path, "w", encoding="utf-8") as result_file:
        json.dump(
            result,
            result_file,
            indent=4,
            ensure_ascii=False,
        )


def print_result(file_path, result):
    print(f"\nРезультаты анализа файла: {file_path}")
    print(json.dumps(result, indent=4, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(
        description="Анализ логов веб-сервера"
    )
    parser.add_argument(
        "path",
        help="Путь к файлу лога или директории с логами",
    )
    args = parser.parse_args()

    input_path = os.path.abspath(args.path)

    if os.path.isfile(input_path):
        files_to_process = [input_path]
    elif os.path.isdir(input_path):
        files_to_process = [
            os.path.join(input_path, filename)
            for filename in sorted(os.listdir(input_path))
            if os.path.isfile(os.path.join(input_path, filename))
            and not filename.lower().endswith(".json")
        ]
    else:
        print(f"Ошибка: путь не существует: {args.path}")
        return

    if not files_to_process:
        print("В указанном месте нет файлов для обработки.")
        return

    for file_path in files_to_process:
        try:
            result = analyze_log_file(file_path)

            if len(files_to_process) == 1:
                output_path = os.path.abspath("result.json")
            else:
                output_path = os.path.join(
                    os.path.dirname(file_path),
                    f"result_{os.path.basename(file_path)}.json",
                )

            save_result(result, output_path)
            print_result(file_path, result)
            print(f"Результат сохранён в: {output_path}")

        except (OSError, UnicodeError) as error:
            print(f"Ошибка при обработке файла {file_path}: {error}")


if __name__ == "__main__":
    main()