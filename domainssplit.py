import csv

with open('emailsdilash.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter='\n')
    writer = csv.writer(open("domainssplitemails.csv", 'a'),['domain','emails',"count"])
    dict={}
    for row in reader:
        print(row[0].split('@'))
        domain= row[0].split('@')
        if(len(domain)>1):
            if (domain[1] in dict):
                dict[domain[1]].append(row[0])
            else:
                dict[domain[1]] = [row[0]]

    print(dict)
    for k,v in dict.items():
        writer.writerow([k,v,len(v)])



