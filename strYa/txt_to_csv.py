import csv

file_txt = 'steady.txt'
file_csv = file_txt.split('.')[0] + '.csv'
with open(file_txt) as f:
    data = f.readlines()
    file_csv = open(file_csv, 'w')
    writer = csv.writer(file_csv)
    writer.writerow(data[0].strip().split(', '))
    data = data[1:]
    for values in data:
        values = values.split(', ')
        values = [values[0]] + [float(i) for i in values[1:]]
        writer.writerow(values)
file_csv.close()
