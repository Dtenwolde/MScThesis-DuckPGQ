# import pandas as pd

# import csv

# open the file in the write mode
# f = open('persons.csv', 'w')
# g = open('knows.csv', 'w')

# create the csv writer
# writer_person = csv.writer(f)

# writer_knows = csv.writer(g)
# write a row to the csv file
# for i in range(0,4294968295):
    # writer_person.writerow([i])
    # writer_knows.writerow([i, i+1])
# close the file
# f.close()
# g.close()


# source = range(0, 4294968295)
# target = range(1, 4294968296)
# persons = list(source) + list(target)[-1]
# pdf = pd.DataFrame(persons, columns=['id'])
# pdf.to_csv("long_path_persons.csv", index=False)
#
# df = pd.DataFrame(list(zip(source, target)), columns=['source', 'target'])
# df.to_csv("long_path_knows.csv", index=False)
#
# hops_df = pd.DataFrame(list(zip([persons[0]], [persons[-1]], [0])), columns=['source', 'target', 'hops'])
# hops_df.to_csv("long_path_hops.csv", index=False)



import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq


chunksize=100000 # this is the number of lines

pqwriter = None
i = 0
# 4300000000
while i < 4300000000:
    chunk = list(range(i, i+chunksize))

    table = pa.Table.from_pandas(pd.DataFrame(chunk, columns=['id']))
    # for the first chunk of records
    if i == 0:
        # create a parquet write object giving it an output file
        pqwriter = pq.ParquetWriter('person.parquet', table.schema)
    pqwriter.write_table(table)
    i += chunksize
    print(i)
    # close the parquet writer
if pqwriter:
    pqwriter.close()