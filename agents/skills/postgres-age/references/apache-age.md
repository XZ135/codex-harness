# Apache AGE Reference

## Scope

Use this reference for PostgreSQL databases using Apache AGE, "A Graph Extension" that adds graph objects and openCypher support to PostgreSQL. AGE is not a separate graph database; it is a PostgreSQL extension with AGE metadata, graph schemas, label tables, custom `agtype`, and Cypher execution through SQL.

Primary project source: `docs/pg_age.md`.

Official source anchors:
- Apache AGE setup: https://age.apache.org/age-manual/master/intro/setup.html
- Apache AGE graphs: https://age.apache.org/age-manual/master/intro/graphs.html
- Apache AGE Cypher format: https://age.apache.org/age-manual/master/intro/cypher.html
- Apache AGE agtype: https://age.apache.org/age-manual/master/intro/types.html
- Apache AGE prepared statements: https://age.apache.org/age-manual/master/advanced/prepared_statements.html
- Apache AGE file import: https://age.apache.org/age-manual/master/intro/agload.html
- Apache AGE repository: https://github.com/apache/age
- PostgreSQL extension docs: https://www.postgresql.org/docs/current/extend-extensions.html
- PostgreSQL schemas/search_path docs: https://www.postgresql.org/docs/current/ddl-schemas.html

## Mental Model

AGE lives inside a PostgreSQL database:

```text
PostgreSQL cluster
└── database
    ├── public
    ├── app schemas
    ├── ag_catalog          -- AGE functions, types, operators, metadata
    └── graph schema        -- one schema/namespace per AGE graph
        ├── _ag_label_vertex
        ├── _ag_label_edge
        ├── VertexLabel
        └── EDGE_LABEL
```

`CREATE EXTENSION age` registers AGE in the current database only. Every database that needs AGE must have the extension created there.

## Version And Installation Checks

Before implementing or debugging:

1. Check PostgreSQL major version.
2. Check AGE extension version, branch, image, or package.
3. Confirm the official AGE compatibility matrix for that version, because docs and releases can differ by branch.
4. Check whether deployment uses the official Docker image, source build, cloud-provider build, or packaged extension.

Useful SQL:

```sql
SELECT version();

SELECT extname, extversion
FROM pg_extension
WHERE extname = 'age';
```

## Database And Connection Initialization

In a target database:

```sql
CREATE EXTENSION IF NOT EXISTS age;
LOAD 'age';
SET search_path = ag_catalog, "$user", public;
```

Meaning:

- `CREATE EXTENSION` registers extension objects in the current database.
- `LOAD 'age'` loads the AGE shared library in the current session.
- `SET search_path` lets unqualified `cypher`, `create_graph`, `agtype`, and AGE operators resolve from `ag_catalog`.

If not setting `search_path`, qualify AGE functions and types explicitly:

```sql
SELECT ag_catalog.create_graph('demo_graph');

SELECT *
FROM ag_catalog.cypher('demo_graph', $$
  MATCH (n)
  RETURN n
$$) AS (n ag_catalog.agtype);
```

For connection pools, run `LOAD 'age'` and `SET search_path = ag_catalog, "$user", public` for every newly opened DBAPI connection. Do not assume it persists across pool connections.

## Graph Lifecycle

Create a graph:

```sql
SELECT create_graph('shop_graph');
-- or
SELECT ag_catalog.create_graph('shop_graph');
```

Inspect graphs and labels:

```sql
SELECT * FROM ag_catalog.ag_graph;
SELECT * FROM ag_catalog.ag_label;
```

Drop a graph:

```sql
SELECT drop_graph('shop_graph', true);
```

Use `true` for cascade unless intentionally dropping dependent graph objects manually.

AGE creates one PostgreSQL namespace/schema for each graph. Graph creation also creates `_ag_label_vertex` and `_ag_label_edge`; vertex and edge labels become child tables. Cypher writes can auto-create label tables.

Do not execute ordinary SQL DML or DDL in AGE graph namespaces unless you have an official, version-checked reason. Prefer `cypher()` and AGE functions.

## Cypher Query Shape

All Cypher runs through `cypher()`:

```sql
SELECT *
FROM cypher('graph_name', $$
  MATCH (n)
  RETURN n
$$) AS (n agtype);
```

Rules:

- `cypher(graph_name, query_string, parameters)` returns a PostgreSQL `SETOF record`.
- Always put `cypher()` in the `FROM` clause or a subquery/CTE, not as a standalone `SELECT` expression.
- Always provide an `AS (...)` record definition.
- Even write-only queries need an `AS (...)` definition.
- Match the number of `RETURN` expressions to declared columns.
- Prefer typed output such as `text`, `bigint`, `numeric`, or `boolean` only after confirming AGE can cast the returned expression correctly; otherwise use `agtype`.

Write-only example:

```sql
SELECT *
FROM cypher('shop_graph', $$
  CREATE (:User {uid: 'u1', name: 'Alice'})
$$) AS (v agtype);
```

Read example:

```sql
SELECT *
FROM cypher('shop_graph', $$
  MATCH (u:User)
  RETURN u.uid, u.name
$$) AS (uid agtype, name agtype);
```

## agtype

AGE's central value type is `agtype`, a JSON-like custom type that can represent:

- null
- integer, float, numeric, boolean, string
- list and map
- vertex, edge, path

Vertices and edges include AGE metadata plus properties. If application code needs ordinary JSON/dicts, explicitly parse/cast according to the driver and AGE version in use. Do not assume every `agtype` string is plain JSON because vertices and edges may include type suffixes such as `::vertex` or `::edge`.

## CRUD Patterns

Create vertex:

```sql
SELECT *
FROM cypher('shop_graph', $$
  CREATE (u:User {uid: 'u1', name: 'Alice', age: 30})
  RETURN u
$$) AS (u agtype);
```

Create edge:

```sql
SELECT *
FROM cypher('shop_graph', $$
  MATCH (a:User {uid: 'u1'}), (b:User {uid: 'u2'})
  CREATE (a)-[r:KNOWS {since: 2024}]->(b)
  RETURN r
$$) AS (r agtype);
```

Read with direction:

```sql
SELECT *
FROM cypher('shop_graph', $$
  MATCH (a:User)-[r:KNOWS]->(b:User)
  RETURN a.uid, r.since, b.uid
$$) AS (from_uid agtype, since agtype, to_uid agtype);
```

Update:

```sql
SELECT *
FROM cypher('shop_graph', $$
  MATCH (u:User {uid: 'u1'})
  SET u.name = 'Alice Zhang', u.updated_at = '2026-07-06'
  RETURN u
$$) AS (u agtype);
```

Remove a property:

```sql
SELECT *
FROM cypher('shop_graph', $$
  MATCH (u:User {uid: 'u1'})
  REMOVE u.updated_at
  RETURN u
$$) AS (u agtype);
```

Delete relationship:

```sql
SELECT *
FROM cypher('shop_graph', $$
  MATCH (:User {uid: 'u1'})-[r:KNOWS]->(:User {uid: 'u2'})
  DELETE r
$$) AS (v agtype);
```

Delete vertex with relationships:

```sql
SELECT *
FROM cypher('shop_graph', $$
  MATCH (u:User {uid: 'u2'})
  DETACH DELETE u
$$) AS (v agtype);
```

Use `MERGE` carefully. It ensures a pattern exists, but it is not a substitute for database-level uniqueness or application-level idempotency under concurrency.

## Query Design

Use `WHERE` near its `MATCH`:

```sql
MATCH (u:User)
WHERE u.age >= 18 AND u.name STARTS WITH 'A'
RETURN u.uid, u.name
```

Bound multi-hop traversals:

```sql
MATCH (a:User {uid: 'u1'})-[:KNOWS*1..3]->(b:User)
RETURN b.uid, b.name
```

Avoid unbounded `[*]` on non-trivial graphs.

Use `WITH` for staged aggregation, filtering, and scoping:

```sql
MATCH (u:User)-[:KNOWS]->(friend:User)
WITH u, count(friend) AS friend_count
RETURN u.uid, friend_count
ORDER BY friend_count DESC
LIMIT 10
```

Use `UNWIND` to expand lists:

```sql
UNWIND ['u1', 'u2', 'u3'] AS uid
RETURN uid
```

## SQL And Cypher Composition

Prefer CTEs when joining graph results to relational tables:

```sql
WITH graph_users AS (
  SELECT *
  FROM cypher('shop_graph', $$
    MATCH (u:User)
    RETURN u.uid, u.name
  $$) AS (uid text, name text)
)
SELECT o.id, o.amount, g.name AS user_name
FROM public.orders AS o
JOIN graph_users AS g
  ON g.uid = o.user_uid;
```

This is often AGE's main value: keep relational facts in ordinary PostgreSQL tables and use graph traversal for relationship logic.

## Parameterization And Injection Safety

AGE's `cypher()` third argument is for prepared statements. Do not pass a parameter map to ad hoc `cypher()` calls unless using a prepared statement form supported by AGE.

Prepared statement example:

```sql
PREPARE find_user(agtype) AS
SELECT *
FROM cypher('shop_graph', $$
  MATCH (u:User)
  WHERE u.uid = $uid
  RETURN u
$$, $1) AS (u agtype);

EXECUTE find_user('{"uid": "u1"}'::agtype);
```

Rules:

- Cypher parameters use `$name`.
- The SQL parameter goes in `cypher()`'s third argument.
- Execution passes an `agtype` map.
- Parameter names in the map omit `$`.
- Labels, relationship types, graph names, and returned column definitions are identifiers or SQL syntax, not normal value parameters. Validate them with strict allowlists before interpolation.

In application code, never concatenate untrusted values into Cypher string literals.

## SQLAlchemy And Python Integration

Follow the project's SQLAlchemy 2.0 style for normal relational operations. AGE-specific calls will often require SQL text because `LOAD`, `SET search_path`, `create_graph`, and `cypher()` are extension-specific.

Connection initialization pattern:

```python
from sqlalchemy import event, text

@event.listens_for(engine, "connect")
def init_age_connection(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("LOAD 'age'")
        cursor.execute('SET search_path = ag_catalog, "$user", public')
    finally:
        cursor.close()
```

Query pattern:

```python
from sqlalchemy import text

stmt = text("""
SELECT *
FROM cypher('shop_graph', $$
  MATCH (u:User)
  RETURN u.uid, u.name
$$) AS (uid agtype, name agtype)
""")

rows = session.execute(stmt).all()
```

If using psycopg v3 directly, remember transaction visibility: setup or graph creation inside a nested transaction/savepoint may not be visible to other sessions until the outer transaction commits. Commit setup steps explicitly or use autocommit for administrative initialization.

## Bulk Import

AGE supports file-based import:

```sql
LOAD 'age';
SET search_path = ag_catalog, "$user", public;

SELECT create_graph('import_graph');

SELECT create_vlabel('import_graph', 'User');
SELECT create_elabel('import_graph', 'KNOWS');

SELECT load_labels_from_file('import_graph', 'User', '/path/to/users.csv');
SELECT load_edges_from_file('import_graph', 'KNOWS', '/path/to/knows_edges.csv');
```

Import order:

1. Create graph.
2. Create vertex and edge labels.
3. Load vertices.
4. Load edges.
5. Verify counts.
6. Run `ANALYZE` if bulk load volume is meaningful.

Edges must reference vertex ids present in vertex files.

## Indexing And Performance

AGE uses PostgreSQL indexes on graph label tables. Add indexes only for real query paths and verify with `EXPLAIN`.

Common indexes:

```sql
CREATE INDEX user_id_idx
ON shop_graph."User" USING BTREE (id);

CREATE INDEX user_properties_gin_idx
ON shop_graph."User" USING GIN (properties);

CREATE INDEX knows_start_id_idx
ON shop_graph."KNOWS" USING BTREE (start_id);

CREATE INDEX knows_end_id_idx
ON shop_graph."KNOWS" USING BTREE (end_id);
```

Property expression index pattern:

```sql
CREATE INDEX user_uid_expr_idx
ON shop_graph."User"
USING BTREE (
  agtype_access_operator(VARIADIC ARRAY[properties, '"uid"'::agtype])
);
```

Plan inspection:

```sql
SELECT *
FROM cypher('shop_graph', $$
  EXPLAIN
  MATCH (u:User)
  WHERE u.uid = 'u1'
  RETURN u
$$) AS (plan text);
```

Performance checklist:

- Start traversals from selective labels/properties.
- Add upper bounds to variable-length paths.
- Index frequently used vertex lookup keys.
- Index edge `start_id` and `end_id` for traversal-heavy workloads.
- Compare property-pattern syntax and `WHERE` syntax with `EXPLAIN`; planner behavior can differ.
- Run `ANALYZE` after large imports.

## Permissions

Common requirements:

- `CREATE EXTENSION` usually needs elevated database privileges.
- Non-superusers may need server setup to `LOAD 'age'`.
- Application users need `USAGE` on `ag_catalog`.
- Application users may need schema/table privileges on graph namespaces, depending on access pattern.

Example:

```sql
GRANT USAGE ON SCHEMA ag_catalog TO app_user;
GRANT USAGE ON SCHEMA shop_graph TO app_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA shop_graph TO app_user;
```

Prefer application access through AGE functions and `cypher()`, not direct graph table DML.

## Troubleshooting

`function cypher(...) does not exist`:

- Run `LOAD 'age'`.
- Set `search_path` to include `ag_catalog`.
- Or qualify as `ag_catalog.cypher` and `ag_catalog.agtype`.

`type "agtype" does not exist`:

- Set `search_path`.
- Or use `ag_catalog.agtype` in return definitions.

Parameter map errors:

- Confirm the query is a prepared statement.
- Confirm the third `cypher()` argument is an `agtype` map.
- Confirm Cypher uses `$name` and the map uses `"name"`.

Empty result after create:

- Check transaction commit.
- Check graph name and database.
- Check that code is not writing on one pooled connection and reading on another before commit.

Unexpected slow query:

- Bound variable-length paths.
- Use `EXPLAIN`.
- Check indexes on graph label tables.
- Check whether a property-pattern query or `WHERE` query gets a better plan.

Missing graph or labels:

```sql
SELECT * FROM ag_catalog.ag_graph;
SELECT * FROM ag_catalog.ag_label;
```

Data quality, missing data, unclear field semantics, and slow retrieval issues discovered during project work must be recorded in `docs/database_problem.md`.
