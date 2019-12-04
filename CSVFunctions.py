
import csv




def output( mylist,name,stilldown,outputdir,groupbyhost,percentAvail,Count):
    fname = '%s.csv' %name
    with open(outputdir+'/%s.csv' %name, 'w', newline='') as csvfile:
        fieldnames = ['SN  ','Host','Service', 'From', 'To','Duration','Info']
        if percentAvail:
            fieldnames= ['SN  ','Host','Service', 'From', 'To','Duration','Availability']
        #fieldnames = ['NAME', 'PID', 'SN', 'IOS', 'MEMORY', 'FAN STATUS', 'TEMPERATURE']
        if not 'Working' in outputdir : csvfile.write('SEP=,\n')
        writer = csv.DictWriter(csvfile, fieldnames = fieldnames)
        #writer=csv.writer(csvfile, dialect='excel')
        #writer.writerow('SEP=,')

        #writer.writerows(mylist)

        writer.writeheader()

        temp = mylist
        output_row={}
        output_row_tmp = {}
        writer.writerow(output_row)
        day='0'
        if not (stilldown) :
            for i,element in enumerate (mylist,start=1):
                output_row ['SN  '] =  str(i)
                if not groupbyhost :
                    if (element[3].split(", ")[1].split(" ")[0]!=day) :
                        writer.writerow({})
                        output_row_tmp['Host']=element[3].split(", ")[1].split(" ")[0]+'-'+element[3].split(", ")[1].split(" ")[1]
                        writer.writerow(output_row_tmp)
                if element[0] == "" :
                    output_row['Host']=element[1]
                    output_row['Service']=" "
                else :
                    output_row['Host'] = element[0]
                    if percentAvail:
                        output_row['Service'] = element[0]
                    else:
                        output_row['Service'] = element[1]
                    output_row['From']=element[2]
                #output_row['From']=element[2]
#
                #day = element[3].split(", ")[1].split(" ")[0]
                output_row['To']=element[3]
                if percentAvail :
                    pass
                else:
                    output_row['Info'] = element[4]

               #fromdt=datetime.strptime(element[2].split(", ")[1], '%d %b %Y %H:%M:%S')
               #todt=datetime.strptime(element[3].split(", ")[1], '%d %b %Y %H:%M:%S')
                output_row['Duration'] =element[5]
                if percentAvail:
                    output_row['Availability']=str("{0:.2f}".format(element[6]))+"%"
               # output_row['Type'] = element[5]

                #print (output_row)
                #input()
                writer.writerow(output_row)
        else :
            for key, value in mylist.items() :
                output_row['Host'] = value['host']
                if percentAvail:
                    output_row['Service'] = ""
                else:
                    output_row['Service'] = key
                    output_row['Info'] = value['info']
                output_row['From'] = value['date']

                #if 'type' in value :
               # output_row['Type'] = value ['type']
                writer.writerow(output_row)

        print ('\nOutput Successfull!\n')
        return 0
