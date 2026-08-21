---
name: postgres-age
description: Work accurately with PostgreSQL databases that use the Apache AGE graph extension. Use when implementing, reviewing, debugging, or documenting AGE setup, CREATE EXTENSION/LOAD/search_path initialization, graph/schema/label management, openCypher queries through cypher(), agtype handling, SQLAlchemy/psycopg integration, SQL + Cypher joins, prepared statements, imports, indexing, permissions, or production troubleshooting for PostgreSQL AGE.
---

# PostgreSQL AGE

## Overview

Use this skill whenever a task touches Apache AGE, the PostgreSQL extension that adds graph storage and openCypher querying inside PostgreSQL. Treat AGE as PostgreSQL plus graph namespaces, AGE metadata, `agtype`, and the `ag_catalog.cypher()` set-returning function.

## First Steps

1. Read `references/apache-age.md` before making design or implementation decisions.
2. Verify the target PostgreSQL major version, AGE version/branch, driver, and deployment environment before relying on version-sensitive behavior.
3. Inspect existing project database helpers and PRDs before adding new connection, migration, or query code.
4. Prefer the project's existing database stack. In this repository that usually means SQLAlchemy 2.0 style unless raw SQL is required for AGE-specific functions.

## Core Rules

- Initialize every AGE connection with `LOAD 'age'` and `SET search_path = ag_catalog, "$user", public`, or use explicit `ag_catalog.` qualification.
- Execute Cypher through `cypher(graph_name, $$ ... $$)` in the SQL `FROM` clause and always declare the returned columns and types with `AS (...)`.
- Treat AGE graph namespaces as AGE-owned storage. Do not directly insert, update, delete, or alter label tables unless official AGE behavior explicitly requires it.
- Use bounded traversal patterns for multi-hop queries, such as `*1..3`; avoid unbounded `*` on non-trivial graphs.
- Do not concatenate untrusted values into Cypher. Use prepared statements for value parameters, and use strict allowlists for labels, relationship types, graph names, or other identifiers that cannot be parameterized.
- Record database data problems in `docs/database_problem.md`; record ontology design issues in `docs/ontology_design_opimization.md`.

## Implementation Workflow

1. Establish the graph model: graph name, vertex labels, edge labels, property keys, uniqueness expectations, and expected traversal patterns.
2. Plan initialization: extension registration, per-connection `LOAD`, `search_path`, non-superuser privileges, and connection pool behavior.
3. Write Cypher as SQL-backed calls with explicit return schemas. Keep graph reads composable through CTEs when joining to relational tables.
4. Decide parameter strategy. Prefer prepared statements for values; validate identifiers through allowlists.
5. Add indexes only for known query entry points and relationship traversal paths. Verify important queries with `EXPLAIN`.
6. Validate with an end-to-end path: initialize connection, create or locate graph, write sample data if appropriate, run the target query, and verify transaction/rollback behavior.

## Resource Guide

- `references/apache-age.md`: operational reference for AGE setup, graph storage, Cypher call shape, `agtype`, SQL/Cypher composition, prepared statements, bulk import, indexing, permissions, transactions, and troubleshooting.
