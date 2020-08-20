# Thingiverse-scraper

## setup:
``` sh
brew install python3 openssl sqlite
make ve
source ve/bin/activate
make install
make prime
```

## usage:
set range of ids you want to scrape in the config.py file, keep CHUNK_SIZE the same, that is the interval that records are written to the sqlite db, and when the program gets new jwt authentication tokens for thingiverse, its unclear when they get stale

`make`
