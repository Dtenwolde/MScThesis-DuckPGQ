import duckdb
import json
from csv import writer
import pandas as pd
import os

output_filename = 'test_results_optimization_with_connections.csv'


def find_csv_filenames(path_to_dir, suffix=".csv"):
    filenames = os.listdir(path_to_dir)
    return [filename for filename in filenames if filename.endswith(suffix)]


def execute_query_test(sf, fraction, optimization, num_connections):
    filename = f'query_profiler{str(sf)}f{str(fraction)}o{str(optimization)}.json'
    con = duckdb.connect(database=':memory:')
    con.execute('CREATE TABLE person (id bigint);')
    con.execute('CREATE TABLE knows (source bigint, target bigint);')
    con.execute(
        f"copy knows from '/home/daniel/PycharmProjects/MScThesis-Scripts/input_files/person_knows_person_trimmed_{sf}_{fraction}_{num_connections}.csv' (HEADER, DELIMITER ',');")
    con.execute('insert into knows select target, source from knows;')
    con.execute(f"copy person from '/home/daniel/Documents/Programming/duckdb-pgq/data/csv/{sf}/Person.csv' (HEADER);")
    con.execute('PRAGMA enable_profiling=json;')
    con.execute(f"PRAGMA profiling_output='{filename}';")
    if optimization:
        con.execute('PRAGMA enable_shared_hash_join;')
    con.execute("SELECT min(CREATE_CSR_EDGE(0, (SELECT count(p.id) as vcount FROM person p), "
                "CAST ((SELECT sum(CREATE_CSR_VERTEX(0, (SELECT count(p.id) as vcount FROM person p), "
                "sub.dense_id , sub.cnt )) AS numEdges "
                "FROM ("
                "  SELECT p.rowid as dense_id, count(k.source) as cnt "
                "FROM person p "
                "LEFT JOIN  knows k ON k.source = p.id "
                "GROUP BY p.rowid "
                ") sub) AS BIGINT), "
                "src.rowid, dst.rowid )) "
                "FROM   knows k "
                "JOIN person src ON k.source = src.id "
                "JOIN person dst ON k.target = dst.id; ")
    con.close()

    f = open(filename)
    query_output = json.load(f)
    f.close()
    os.remove(filename)

    query_total_time = query_output['timing']
    df = pd.DataFrame({'time': query_total_time, 'optimization': optimization, 'sf': sf, 'fraction': fraction,
                       'num_connections': num_connections},
                      index=[0])
    if not os.path.isfile(output_filename):
        df.to_csv(output_filename, header=True, index=False)
    else:  # else it exists so append without writing the header
        df.to_csv(output_filename, mode='a', header=False, index=False)


def main():
    for _ in range(100):
        filenames = find_csv_filenames("/home/daniel/PycharmProjects/MScThesis-Scripts/input_files")
        for file in filenames:
            file_split = file.split("_")
            sf = file_split[-3]
            fraction = file_split[-2]
            num_connections = file_split[-1].split(".")[0]
            execute_query_test(sf, fraction, True, num_connections)
            execute_query_test(sf, fraction, False, num_connections)


if __name__ == "__main__":
    main()
