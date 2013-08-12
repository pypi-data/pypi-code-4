import glob
import json
import datetime
from dateutil.rrule import rrule, MONTHLY, SA

import configbuilder.from_csv

output_file = "config.json"


def _ordinal_suffix(day):
    if 4 <= day <= 20 or 24 <= day <= 30:
        return "th"
    else:
        return ["st", "nd", "rd"][day % 10 - 1]


def _next_second_saturday():
    today = datetime.date.today()
    rule = rrule(MONTHLY, count=1, byweekday=SA(+2), dtstart=today)
    next_one = rule[0]
    return "".join((next_one.strftime("%B %d"),
                    "<span class=\"suffix\">",
                     _ordinal_suffix(next_one.day),
                    "</span>"
    ))


def main():
    data_parts = glob.glob("configs/*.csv")
    data = { }
    for part in data_parts:
        key = part.replace("configs\\", "").replace(".csv", "")
        data[key] = configbuilder.from_csv.main(part)

    boilerplate = json.load(open("configs/boiler.json"))
    data['next_artwalk'] = _next_second_saturday()  # Specific to buildingc
    boilerplate['data'] = data
    with open(output_file, "w") as f:
        json.dump(boilerplate, f, indent=2)

if __name__ == "__main__":
    main()