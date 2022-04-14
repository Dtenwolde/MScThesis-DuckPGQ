import sys

print(sys.path)
sys.path.remove('/usr/lib/python3.8/site-packages/duckdb-0.2.2.dev6998+g8f0019d39-py3.8-linux-x86_64.egg')
print(sys.path)
import duckdb
import pandas as pd
import json
import os


print(duckdb.__version__)
scale_factors = ['sf0.1', 'sf1', 'sf3', 'sf10', 'sf30', 'sf100', 'sf300']
num_of_cores = [1, 2, 3, 4, 5, 6, 7, 8]
path_percentages = [1, 2, 5, 10, 15, 20, 25]

filepath = '/home/daniel/Documents/Programming/duckdb-pgq'
filename = 'shortest_path.json'
output_filename = 'shortest_path_test.csv'

duplicates_allowed = True

for sf in scale_factors:
    for cores in num_of_cores:
        for path_percentage in path_percentages:
            con = duckdb.connect(":memory:")

            con.execute("CREATE TABLE person (id bigint);")

            con.execute(f"copy person from '{filepath}/data/csv/{sf}/Person.csv' (HEADER);")

            num_of_persons = con.execute(f'select count(*) from person;').fetchone()
            con.execute("CREATE TABLE knows (source bigint, target bigint);")

            con.execute(
                f"copy knows from '{filepath}/data/csv/{sf}/Person_knows_Person.csv' (HEADER, DELIMITER '|');")

            con.execute("insert into knows select target, source from knows;")

            random_source = con.execute(
                f"SELECT id FROM person USING SAMPLE {path_percentage} PERCENT (bernoulli);").fetchdf()
            random_target = con.execute(
                f"SELECT id FROM person USING SAMPLE {path_percentage} PERCENT (bernoulli);").fetchdf()

            if not duplicates_allowed:
                while set(random_source['id']) & set(random_target['id']):
                    random_source = pd.DataFrame(
                        con.execute(
                            f"SELECT id FROM person USING SAMPLE {path_percentage} PERCENT (bernoulli);").fetchdf())
                    random_target = pd.DataFrame(
                        con.execute(
                            f"SELECT id FROM person USING SAMPLE {path_percentage} PERCENT (bernoulli);").fetchdf())

            outlist = [(i, j) if i != j else ''
                       for i in random_source['id']
                       for j in random_target['id']]

            filtered = list(filter(lambda ele: ele != '', outlist))
            num_of_paths = len(filtered)

            df = pd.DataFrame(data=filtered, columns=['source', 'target'])
            # print(list(set(list(df['source']))))
            # print(list(set(list(df['target']))))

            con.register("hops", df)

            con.execute("SELECT CREATE_CSR_VERTEX( "
                        "0, "
                        "v.vcount, "
                        "sub.dense_id, "
                        "sub.cnt "
                        ") AS numEdges "
                        "FROM ( "
                        "SELECT p.rowid as dense_id, count(k.source) as cnt "
                        "FROM person p "
                        "LEFT JOIN  knows k ON k.source = p.id "
                        "GROUP BY p.rowid "
                        ") sub,  (SELECT count(p.id) as vcount FROM person p) v;")

            con.execute("SELECT min(CREATE_CSR_EDGE(0, (SELECT count(p.id) as vcount FROM person p), "
                        "CAST ((SELECT sum(CREATE_CSR_VERTEX(0, (SELECT count(p.id) as vcount FROM person p), "
                        "sub.dense_id , sub.cnt )) AS numEdges "
                        "FROM ( "
                        "SELECT p.rowid as dense_id, count(k.source) as cnt "
                        "FROM person p "
                        "LEFT JOIN  knows k ON k.source = p.id "
                        "GROUP BY p.rowid "
                        ") sub) AS BIGINT), "
                        "src.rowid, dst.rowid )) "
                        "FROM "
                        "knows k "
                        "JOIN person src ON k.source = src.id "
                        "JOIN person dst ON k.target = dst.id;")

            con.execute("CREATE TABLE src_dest(id int default 0, v_size bigint, src bigint, dst bigint);")

            con.execute(
                "CREATE table hops_rowid as select p.rowid as src_rowid, p2.rowid as dest_rowid from hops h "
                "JOIN person p on p.id = h.source "
                "JOIN person p2 on p2.id = h.target;")

            con.execute("insert into src_dest (src, dst) select src_rowid, dest_rowid from hops_rowid h;")

            con.execute("update src_dest s set v_size = (select count(*) from person p) where v_size is NULL;")
            con.execute('PRAGMA enable_profiling=json;')
            con.execute(f"PRAGMA profiling_output='{filename}';")
            con.execute(f"PRAGMA threads={cores}")

            result = pd.DataFrame(con.execute(
                "SELECT p.id as source, p2.id as target, shortest_path(s.id, false, v_size, s.src, s.dst) as hops FROM src_dest s "
                "LEFT JOIN person p ON s.src = p.rowid "
                "LEFT JOIN person p2 ON s.dst = p2.rowid "
                "order by p.id, p2.id").fetchdf())

            con.close()
            f = open(filename)
            query_output = json.load(f)
            f.close()
            os.remove(filename)

            query_total_time = query_output['timing']
            df = pd.DataFrame(
                {'time': query_total_time, 'sf': sf, 'num_of_paths': num_of_paths, 'path_percentages': path_percentage,
                 'num_of_persons': num_of_persons[0], 'num_of_cores': cores},
                index=[0])

            if not os.path.isfile(output_filename):
                df.to_csv(output_filename, header=True, index=False)
            else:  # else it exists so append without writing the header
                df.to_csv(output_filename, mode='a', header=False, index=False)
