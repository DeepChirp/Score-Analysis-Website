import csv
import os
import json

random_name_list = []

with open("../data/random_name.txt", "r") as f:
    lines = f.readlines()

    for line in lines:
        random_name_list.append(line.strip())

name_map = {}

for filename in os.listdir("../data/csv"):
    mapped_rows = []
    with open("../data/csv/{}".format(filename), "r", encoding="GB18030") as f:
        reader = csv.reader(f)
        for row in reader:
            if row[2] != "姓名":
                if row[2] not in name_map:
                    mapped_name = random_name_list.pop()
                    name_map[row[2]] = mapped_name
                    row[2] = mapped_name
                else:
                    row[2] = name_map[row[2]]
            mapped_rows.append(row)

    with open("../data/csv/{}".format(filename), "w", encoding="UTF-8") as f:
        writer = csv.writer(f)
        writer.writerows(mapped_rows)

    mapped_rows.clear()

with open("name_map.txt", "w", encoding="UTF-8") as f:
    f.write(json.dumps(name_map))
