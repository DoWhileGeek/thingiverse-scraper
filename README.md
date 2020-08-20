# Thingiverse-scraper

## setup:
we're runnin python3 'round here
``` sh
brew install python3 openssl sqlite
```
not sure if you know how to setup a virtual environment, so this'll do it for you
``` sh
make ve
```
ya cant source files for some reason in a makefile?
``` sh
source ve/bin/activate
```
install python requirements
```sh
pip install -r requirements.txt
```
prime the sqlite db with the `thing` table
``` sh
make prime
```

## usage:
set range of ids you want to scrape in the config.py file, keep CHUNK_SIZE the same, that is the interval that records are written to the sqlite db, and when the program gets new jwt authentication tokens for thingiverse, its unclear when they get stale

After you've set the range, you simply run:
`make`
