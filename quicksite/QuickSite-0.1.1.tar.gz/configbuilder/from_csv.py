import csv

def main(input_file):


    reader = csv.DictReader(open(input_file))
    data = [ ]
    for row in reader:
        if row['active'] == '1':
            retval = { }
            for (key, value) in row.items():
                if "|" in value:
                    value = value.split("|")
                retval[key] = value
            data.append(retval)

    return data

if __name__ == "__main__":
    print main("configs/artists.csv")