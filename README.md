# Patent Fetcher

Tool for fetching patents from the USPTO API between a specified start and end date.

## Running

An external postgreSQL server is required to persist patent data. This could be configured manually but the easiest solution is to use the included docker-compose configuration.

Run `docker-compose up` to start the DB server and initialise the schema specified in schema.sql.

Then, to run a task:
    `docker-compose run --rm patent_fetcher 2017-01-01 2017-01-03`

This will download all patents between the two dates in ISO format (inclusive). `--rm` is not required but auto-removes the container after running.

To load downloaded patents from the database and print to the console use the `-l` (or `--load`) flag:
    `docker-compose run --rm patent_fetcher 2017-01-01 2017-01-03 -l`

## Tests

Run tests with:
    `docker-compose run --rm tests`

(Note: DB server must be running)

## Design Decisions

The `Fetcher` class uses dependency injection to get an implementation of `PatentStoreBase`, allowing different stores to be swapped in/out without affecting the patent fetching logic. This was particularly useful for testing and debugging where I could use `MemoryPatentStore` to ensure the data download logic was correct. It is also feasible that a store implementation could be used to push the data to a separate web API or to some message dispatcher, illustrating the flexibility of the design.

The fetch process is designed to minimize database transactions by first downloading all patents before being passed to the store. It does however have the disadvantage that in the event of an error the full download must be restarted. This could at least be partly mitigated by implementing retry logic, or saving all downloaded patents before exiting. The final design is in the interest of time and minimizing complexity. Given a real project, I would use profiling tools to measure the impact of various approaches and implement a more robust solution.