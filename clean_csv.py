import csv
with open("data/hotels.csv","r") as source:
    rdr= csv.reader( source )
    with open("data/new_hotels.csv","w") as result:
        wtr= csv.writer( result )
        for r in rdr:
            wtr.writerow( (r[0], r[3], r[6], r[11] , r[12] , r[13] , r[16]) )