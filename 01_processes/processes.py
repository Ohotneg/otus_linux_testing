import subprocess
from datetime import datetime

result = subprocess.run(
    ["ps", "aux"],
    capture_output=True,
    text=True
)

if result.returncode != 0:
    print("Ошибка при выполнении команды ps aux:")
    print(result.stderr)
    raise SystemExit(1)

lines = result.stdout.splitlines()

users = {}
process_count = 0

total_memory = 0.0
total_cpu = 0.0

max_memory = -1.0
max_memory_process = ""

max_cpu = -1.0
max_cpu_process = ""

for line in lines[1:]:
    parts = line.split(maxsplit=10)

    if len(parts) < 11:
        continue

    user = parts[0]
    cpu = float(parts[2])
    memory = float(parts[3])
    command = parts[10]

    process_count += 1

    if user not in users:
        users[user] = 0

    users[user] += 1

    total_cpu += cpu
    total_memory += memory

    if memory > max_memory:
        max_memory = memory
        max_memory_process = command

    if cpu > max_cpu:
        max_cpu = cpu
        max_cpu_process = command

user_list = ", ".join(f"'{user}'" for user in users)

report = (
    "Отчёт о состоянии системы:\n"
    f"Пользователи системы: {user_list}\n"
    f"Процессов запущено: {process_count}\n"
    "\n"
    "Пользовательских процессов:\n"
)

for user, count in users.items():
    report += f"{user}: {count}\n"

report += (
    "\n"
    f"Всего памяти используется: {total_memory:.1f}%\n"
    f"Всего CPU используется: {total_cpu:.1f}%\n"
    f"Больше всего памяти использует: {max_memory_process[:20]}\n"
    f"Больше всего CPU использует: {max_cpu_process[:20]}\n"
)

print(report)

filename = datetime.now().strftime("%m-%d-%Y-%H-%M-scan.txt")

with open(filename, "w", encoding="utf-8") as file:
    file.write(report)

print(f"Отчёт сохранён в файл: {filename}")