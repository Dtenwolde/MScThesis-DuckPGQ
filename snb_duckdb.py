import duckdb

all_sf = ['sf1']  #  , 'sf3', 'sf10', 'sf30', 'sf100', 'sf300'
fractions = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
for sf in all_sf:
    for fraction in fractions:
        con = duckdb.connect(database=':memory:')
        con.execute("CREATE TABLE person_knows_person (person1id bigint, person2id bigint);")
        con.execute(
            "copy person_knows_person from '/home/daniel/Documents/Programming/duckdb-pgq/data/csv/sf1/Person_knows_Person.csv' (HEADER, DELIMITER '|');")
        con.execute("create table sparse_pkp as (select person1id, person2id "
                    "from "
                    "(select "
                    "pkp.person1id, "
                    "pkp.person2id, "
                    "row_number() OVER (partition by pkp.person1id order by md5(pkp.person2id)) as rnum, "
                    "person1deg "
                    "from person_knows_person pkp "
                    "join (select person1id, count(person2id) as person1deg "
                    "      from person_knows_person "
                    "      group by person1id "
                    "    ) deg "
                    "on deg.person1id = pkp.person1id "
                    "order by person1id, md5(person2id) "
                    ") "
                    "where rnum < person1deg * 0.1 "
                    "order by person1id, person2id)")

        average_connections = con.execute(
            "select cast(avg(deg) as int) from (select person1id, count(person2id) as deg from sparse_pkp group by person1id);").fetchall()[
            0][0]
        con.execute(
            f"copy (select person1id as source, person2id as target from sparse_pkp) to 'input_files/person_knows_person_trimmed_{sf}_{fraction}_{average_connections}.csv' WITH (HEADER, DELIMITER ',');")
