import csv
import yaml

locations = []

with open('locations.csv', 'r') as csv_file:
    csv_reader = csv.reader(csv_file)
    for row in csv_reader:
        location = {}
        location['Lat-Long'] = row[0]
        location['Grid Prec'] = row[1]
        location['names'] = []

        for number in range(2, len(row)):
            if row[number] != '':
                location['names'].append(row[number])

        locations.append(location)

with open('locations.yaml', 'w') as locations_yaml:
    yaml.dump(locations, locations_yaml)
