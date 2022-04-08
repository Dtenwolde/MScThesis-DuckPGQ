import duckdb
import pandas as pd

print(duckdb.__version__)
sf = 'sf0.1'

filepath = '/home/daniel/Documents/Programming/duckdb-pgq'

con = duckdb.connect(":memory:")

con.execute("CREATE TABLE person (id bigint);")

con.execute(f"copy person from '{filepath}/data/csv/{sf}/Person.csv' (HEADER);")

con.execute("CREATE TABLE knows (source bigint, target bigint);")

con.execute(
    f"copy knows from '{filepath}/data/csv/{sf}/Person_knows_Person.csv' (HEADER, DELIMITER '|');")

con.execute("insert into knows select target, source from knows;")

# con.execute("create table hops (source bigint, target bigint, hops int);")

# con.execute(
#     f"copy hops from '{filepath}/data/csv/{sf}/shortest_unweighted_path{sf}_comma.csv' (DELIMITER ',', HEADER);")


random_source = con.execute("SELECT id FROM person USING SAMPLE 2 PERCENT (bernoulli);").fetchdf()
random_target = con.execute("SELECT id FROM person USING SAMPLE 2 PERCENT (bernoulli);").fetchdf()
while set(random_source['id']) & set(random_target['id']):
    random_source = con.execute("SELECT id FROM person USING SAMPLE 2 PERCENT (bernoulli);").fetchdf()
    random_target = con.execute("SELECT id FROM person USING SAMPLE 2 PERCENT (bernoulli);").fetchdf()

outlist = [(i, j) if i!=j else ''
           for i in random_source['id']
           for j in random_target['id']]

filtered = list(filter(lambda ele: ele != '', outlist))

df = pd.DataFrame(data=filtered, columns=['source', 'target'])
print(list(set(list(df['source']))))
print(list(set(list(df['target']))))

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

result = con.execute(
    "SELECT p.id as source, p2.id as target, shortest_path(s.id, false, v_size, s.src, s.dst) as hops FROM src_dest s "
    "LEFT JOIN person p ON s.src = p.rowid "
    "LEFT JOIN person p2 ON s.dst = p2.rowid "
    "order by p.id, p2.id").fetchdf()

print(set(result['hops']))
