import csv
import sys

writer = csv.writer(open("emailsdilash.csv", 'a'))

csv.field_size_limit(sys.maxsize)
reader = csv.reader(open('Final-Output.csv', newline='') , delimiter='\n')
for row in reader:
    print(row)
    for value in row:
        for result in value.split(','):
            writer.writerow([result])

