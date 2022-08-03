# Master thesis: Integrating SQL/PGQ into DuckDB
## Overview repository 
In this overview, pointers are given to other repositories used for implementation / experiments related to integrating SQL/PGQ in DuckDB.
Furthermore, scripts used to generate plots can be found in this repository. 

## [DuckPGQ](https://github.com/cwida/duckdb-pgq.old/tree/path_length)
In this repository, the beginnings of an extension module for DuckDB related to SQL/PGQ can be found [here](https://github.com/cwida/duckdb-pgq.old/tree/path_length/extension/sqlpgq).

This includes implementations of: 
* [Multi-source Breadth-first search](https://github.com/cwida/duckdb-pgq.old/blob/path_length/extension/sqlpgq/sqlpgq_functions/sqlpgq_shortest_path.cpp) used for shortest path and any shortest path.
* [Batched Bellman-Ford](https://github.com/cwida/duckdb-pgq.old/blob/path_length/extension/sqlpgq/sqlpgq_functions/sqlpgq_cheapest_path.cpp) used for cheapest path.
* [Weighted or unweighted CSR creation](https://github.com/cwida/duckdb-pgq.old/blob/path_length/extension/sqlpgq/sqlpgq_functions/sqlpgq_csr_creation.cpp) used to create a CSR data structure.

## [Vectorised batched Bellman-Ford microbenchmark](https://github.com/Dtenwolde/SIMD-Batched-Bellman-Ford)
This repository contains a microbenchmark conducted to test the speedup achieved when using vectorised instructions compared to scalar instructions for the batched Bellman-Ford algorithm. 

## [Shared hash join optimisation](https://github.com/diegomestre2/duckdb/tree/shared_hash_join)
This repository contains an optimisation that is able to share the hash table created between joins that use the same hash table. 

