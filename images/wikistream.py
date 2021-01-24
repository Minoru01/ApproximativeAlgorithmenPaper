from datetime import datetime, timedelta
from hll_custom import HyperLogLog as HyperLogLogCustom
from hyperloglog import HyperLogLog
from json import loads
from sseclient import SSEClient
from sys import getsizeof

start_time = datetime.now()

duration_counter = 1
max_duration = 24
duration = timedelta(hours=duration_counter)

hll = HyperLogLog(0.01)
hll_custom = HyperLogLogCustom(0.01)
naive = set()
write_counter = 0

hll_log = []
hll_size_log = []
hll_custom_log = []
hll_custom_size_log = []
naive_log = []
naive_size_log = []

url = 'https://stream.wikimedia.org/v2/stream/'
url_stream = 'recentchange'

stream = SSEClient(url + url_stream)

for event in stream:
    # Check for error events and continue
    if not event.event == 'message':
        continue

    # Try to parse event data
    try:
        data = loads(event.data)
    except ValueError:
        continue

    # Ignore other wiki sources like
    # wikimedia, wikidata, wikisource, wiktionary, ...
    server_search = 'wikipedia.org'
    if not server_search in data['server_name']:
        continue

    # Add page title to HyperLogLog and Set
    hll.add(data['title'])
    hll_custom.add(data['title'])
    naive.add(data['title'])
    write_counter += 1

    # ... Keep track of current approximation and size

    dtn = datetime.now()
    print(f'[{dtn}] +{dtn - start_time}', end = '\r')

    # Write Log
    if dtn - start_time >= duration:
        # ... Log results
        duration_counter += 1
        duration = timedelta(hours=duration_counter)
        if duration_counter > max_duration:
            break