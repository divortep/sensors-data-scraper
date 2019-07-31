import csv
import json
import os
import re
from datetime import datetime
from pathlib import Path

CSV_SEPARATOR = '|'


def main():
    with open('./input.txt', 'r') as file:
        content = file.read()

    variables = re.findall(r'var\s(.*=\s\[.*\]);', content)
    var_map = {}
    for var in variables:
        var_entry = var.split(' = ')
        var_map[var_entry[0]] = var_entry[1].encode().decode('unicode_escape')

    if not var_map:
        print("Didn't find any variables.")
        exit(1)

    dir_name = datetime.now().strftime('%d-%m-%Y %H:%M:%S.%f')
    os.mkdir('./' + dir_name)

    for var_name, var_value in var_map.items():
        json_data = json.loads(var_value)
        file_path = Path(__file__).resolve() / Path(dir_name).resolve() / f'{var_name}.csv'
        if var_name == 'context_data_chart_map':
            result = transform_data(json_data)
            with open(file_path, 'w+') as csv_file:
                csv_writer = csv.writer(csv_file, delimiter=CSV_SEPARATOR)
                write_result_to_csv(result, csv_writer)

        else:
            write_data_to_csv(file_path, json_data)


def transform_data(json_data):
    result = {}
    for json_obj in json_data:
        map_flat_obj(result, json_obj)

    return result


def map_flat_obj(result, json_obj, prefix=''):
    if not prefix:
        prefix = json_obj['name']

        if 'value' in json_obj.keys():
            value = json_obj['value']
            if prefix not in result.keys():
                result[prefix] = {}
            result[prefix]['amount'] = value

    if 'data' in json_obj.keys():
        data = json_obj['data']

        for data_obj in data:
            date = str(data_obj['date'])
            for key, val in data_obj.items():
                if not key == 'date':
                    group = prefix + CSV_SEPARATOR + key
                    if group not in result.keys():
                        result[group] = {}
                    result[group][date] = val

    if 'children' in json_obj.keys():
        children = json_obj['children']
        for child in children:
            prefix += CSV_SEPARATOR + child['name']
            if 'data' in child.keys():
                map_flat_obj(result, child, prefix)


def write_result_to_csv(result, csv_writer):
    all_cols = [col for row in result.keys() for col in result[row]]
    cols = sorted(set(filter(lambda _: not _ == 'amount', all_cols)))

    max_group_num = max([len(groups.split(CSV_SEPARATOR)) for groups in result.keys()])
    csv_writer.writerow(['' for _ in range(max_group_num)] + ['amount'] + cols)

    for row in result.keys():
        group_num = len(row.split(CSV_SEPARATOR))
        row_data = row.split(CSV_SEPARATOR) + ['' for _ in range(max_group_num - group_num)]
        if 'amount' in result[row].keys():
            row_data = row_data + [result[row]['amount']]
        else:
            row_data = row_data + ['']

        for col in cols:
            if col in result[row].keys():
                row_data.append(result[row][col])
        csv_writer.writerow(row_data)


def write_data_to_csv(file_path, json_data):
    with open(file_path, 'w+') as csv_file:
        if json_data and isinstance(json_data[0], dict):
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(json_data[0].keys())
            for json_obj in json_data:
                csv_writer.writerow(json_obj.values())

        elif json_data:
            for json_obj in json_data:
                csv_file.write(json_obj)


if __name__ == '__main__':
    main()
