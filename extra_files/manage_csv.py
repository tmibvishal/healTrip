import csv
with open("data/flights.csv","r") as source:
    my_dict = {}
    rdr= csv.reader( source )
    with open("data/new_flights.csv","w") as result:
        wtr= csv.writer( result )
        first = True
        i = 0
        for r in rdr:
            if not first:
                if (r[1],r[3],r[4]) not in my_dict:
                    my_dict[(r[1],r[3],r[4])] = [False,False,False,False,False,False]

                ind1 = int(r[5])//800
                ind2 = int(r[6])//800

                if my_dict[(r[1],r[3],r[4])][ind1] and my_dict[(r[1],r[3],r[4])][ind2]:
                    continue

                else:
                    my_dict[(r[1],r[3],r[4])][ind1] = True
                    my_dict[(r[1],r[3],r[4])][ind2] = True
                    wtr.writerow( (i , r[1] , r[2] , r[3] , r[4] , r[5] , r[6] , r[7]) )
                    i += 1

            else:
                first = False
                wtr.writerow( (r[0] , r[1] , r[2] , r[3] , r[4] , r[5] , r[6] , r[7]) )

