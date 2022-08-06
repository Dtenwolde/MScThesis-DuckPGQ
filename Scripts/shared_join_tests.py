import duckdb
import json
from csv import writer
import pandas as pd
import os

output_filename = 'test_results_optimization_with_connections.csv'

def load_entities_csv(con, data_dir: str):
    dynamic_path = f"{data_dir}/initial_snapshot/dynamic"
    dynamic_entities = ["Person"]

    con.execute("CREATE TABLE Person (     creationDate timestamp NOT NULL,     "
                "id bigint PRIMARY KEY, "
                "firstName varchar(40) NOT NULL, "
                "lastName varchar(40) NOT NULL, "
                "gender varchar(40) NOT NULL, "
                "birthday date NOT NULL,  "
                "locationIP varchar(40) NOT NULL,"
                "browserUsed varchar(40) NOT NULL, "
                "LocationCityId bigint NOT NULL,  "
                "speaks varchar(640) NOT NULL, "
                "email varchar(8192) NOT NULL)")



    for entity in dynamic_entities:
        for csv_file in [f for f in os.listdir(f"{dynamic_path}/{entity}") if
                         f.startswith("part-") and (f.endswith(".csv") or f.endswith(".csv.gz"))]:
            csv_path = f"{dynamic_path}/{entity}/{csv_file}"
            con.execute(
                f"COPY {entity} FROM '{csv_path}' (DELIMITER '|', HEADER, FORMAT csv)")
            if entity == "Person_knows_Person":
                con.execute(
                    f"COPY {entity} (creationDate, Person2id, Person1id) FROM '{csv_path}' (DELIMITER '|', HEADER, FORMAT csv)")

def find_csv_filenames(path_to_dir, suffix=".csv"):
    filenames = os.listdir(path_to_dir)
    return [filename for filename in filenames if filename.endswith(suffix)]


def execute_query_test(sf, fraction, optimization, num_connections):
    filename = f'query_profiler{str(sf)}f{str(fraction)}o{str(optimization)}.json'
    con = duckdb.connect(database=':memory:')

    load_entities_csv(con, f"/home/daniel/Documents/ldbc_snb_datagen_spark/out-{sf}/graphs/csv/bi/composite-merged-fk")

    con.execute("CREATE TABLE Person_knows_Person (    "
                "creationDate timestamp NOT NULL, "
                "source bigint NOT NULL,    "
                "target bigint NOT NULL)")
    con.execute(
        f"copy Person_knows_Person from 'input_files/person_knows_person_trimmed_{sf}_{fraction}_{num_connections}.csv' (HEADER, DELIMITER ',');")
    con.execute('insert into Person_knows_Person select creationdate, target, source from Person_knows_Person;')

    con.execute('PRAGMA enable_profiling=json;')
    con.execute(f"PRAGMA profiling_output='{filename}';")
    if optimization:
        con.execute('PRAGMA enable_shared_hash_join;')
    else:
        con.execute('PRAGMA disable_shared_hash_join;')
    con.execute("select * FROM person_knows_person k "
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
    filenames = find_csv_filenames("input_files")
    for file in filenames:
        file_split = file.split("_")
        sf = file_split[-3]
        fraction = file_split[-2]
        print(sf, fraction)
        for _ in range(100):
            num_connections = file_split[-1].split(".")[0]
            execute_query_test(sf, fraction, True, num_connections)
            execute_query_test(sf, fraction, False, num_connections)


if __name__ == "__main__":
    main()
