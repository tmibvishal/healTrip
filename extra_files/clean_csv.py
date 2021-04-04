import csv
with open("data/covid.csv","r") as source:
    rdr= csv.reader( source )
    with open("data/covid_status.csv","w") as result:
        wtr= csv.writer( result )
        for r in rdr:
            wtr.writerow( (r[1], r[2], r[6], r[11] , r[18] , r[19] , r[28]) )