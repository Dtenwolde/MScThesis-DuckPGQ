import pandas as pd
import warnings
import os
import duckdb

warnings.filterwarnings("ignore")

def load_entities_csv(con, data_dir: str):
    dynamic_path = f"{data_dir}/initial_snapshot/dynamic"
    dynamic_entities = ["Person_knows_Person"]

    for entity in dynamic_entities:
        for csv_file in [f for f in os.listdir(f"{dynamic_path}/{entity}") if
                         f.startswith("part-") and (f.endswith(".csv") or f.endswith(".csv.gz"))]:
            csv_path = f"{dynamic_path}/{entity}/{csv_file}"
            con.execute(
                f"COPY {entity} FROM '{csv_path}' (DELIMITER '|', HEADER, FORMAT csv)")

def main():
    all_sf = ['sf1', 'sf3', 'sf10']  #
    fractions = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]

    for sf in all_sf:
        con = duckdb.connect(database=":memory:")
        con.execute("DROP TABLE IF EXISTS Person_knows_Person")
        con.execute("CREATE TABLE Person_knows_Person (    "
                    "creationDate timestamp NOT NULL, "
                    "source bigint NOT NULL,    "
                    "target bigint NOT NULL)")

        load_entities_csv(con, f"/home/daniel/Documents/ldbc_snb_datagen_spark/out-{sf}/graphs/csv/bi/composite-merged-fk")
        try:
            print(f"Starting {sf}")
            for fraction in fractions:
                print(f"Starting {fraction}")
                df = con.execute("SELECT * FROM Person_knows_Person").fetch_df()
                running_sum = 0
                running_length = 0
                df_grouped = df.groupby('source')
                df_trimmed = pd.DataFrame(columns=['source', 'target'])

                for name, group in df_grouped:
                    # Change this for the number of connections
                    if fraction != 1:
                        num_of_knows = int(len(group) * fraction)
                        trimmed = group.sample(num_of_knows, replace=True).drop_duplicates()
                        running_sum += num_of_knows
                    else:
                        trimmed = group
                        running_sum += len(group)
                    running_length += 1
                    # if file does not exist write header
                    if not os.path.isfile(f"input_files/person_knows_person_trimmed_{sf}_{fraction}.csv"):
                        trimmed.to_csv(f"input_files/person_knows_person_trimmed_{sf}_{fraction}.csv", header=True,
                                       index=False)
                    else:  # else it exists so append without writing the header
                        trimmed.to_csv(f"input_files/person_knows_person_trimmed_{sf}_{fraction}.csv", mode='a',
                                       header=False, index=False)

                final_df = pd.read_csv(f"input_files/person_knows_person_trimmed_{sf}_{fraction}.csv")
                os.remove(f"input_files/person_knows_person_trimmed_{sf}_{fraction}.csv")
                final_df.to_csv(
                    f"input_files/person_knows_person_trimmed_{sf}_{fraction}_{int(round(running_sum / running_length))}.csv",
                    index=False)
        except:
            print(f"{sf} not found")


if __name__ == "__main__":
    main()