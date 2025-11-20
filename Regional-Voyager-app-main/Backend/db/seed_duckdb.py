import duckdb

con = duckdb.connect("data/warehouse.duckdb")

con.execute(open("db/duckdb_init.sql").read())
con.execute("COPY sales_history FROM 'data/sales_history.csv' (AUTO_DETECT TRUE)")

con.execute("INSERT INTO aggregated_sales SELECT * FROM aggregated_sales")
con.execute("INSERT INTO sku_features SELECT * FROM sku_features")

print("DuckDB seeded successfully")
