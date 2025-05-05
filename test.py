#%%
# Note: the module name is psycopg, not psycopg3
import psycopg

#%%
# Connect to an existing database
with psycopg.connect("dbname=mtg_scrapper user=admin password=123456") as conn:

    # Open a cursor to perform database operations
    with conn.cursor() as cur:

        # Execute a command: this creates a new table
        cur.execute('DROP TABLE test')
        
        '''        
            cur.execute("""
            CREATE TABLE test (
                id serial PRIMARY KEY,
                num integer,
                data text)
            """)
        '''

        # Pass data to fill a query placeholders and let Psycopg perform
        # the correct conversion (no SQL injections!)

        # Query the database and obtain data as Python objects.
        #cur.execute("DELETE FROM test")
        cur.execute("SELECT * FROM test")
        print(cur.fetchmany())
        # will print (1, 100, "abc'def")