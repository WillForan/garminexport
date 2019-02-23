#!/usr/bin/env python
from fitparse import FitFile
from datetime import datetime
import zipfile
import sys
import re

# time parsing from
# https://github.com/4kbt/ParseVivosmartHR/blob/master/parseFITs.sh
# https://github.com/dtcooper/python-fitparse/issues/46
UTC_REFERENCE = 631065600  # timestamp for UTC 00:00 Dec 31 1989

# see a bunch of debug messages?
DEBUG = False


def debug(*kargs):
    if DEBUG:
        print(*kargs)


def get_hr_values(fitfile):
    d = {'time': 0, 'last_full': 0, 'epoch': 0}
    hr = []
    # Get all data messages that are of type record
    for record in fitfile.get_messages():
        # Go through all the data entries in this record
        for r in record:
            if r.name not in ['heart_rate', 'timestamp', 'timestamp_16']:
                continue
            # Print the records name and value (and units if it has any)
            debug("%s: %s" % (r.name, r.value))

            # got a normal 32 bit timestamp. update fields
            if r.name == 'timestamp':
                d['time'] = r.value
                d['last_full'] = r.raw_value
                debug(" * set time to %s, last epoch is %d" %
                      (d['time'], d['last_full']))

            # have a 16 bit timestamp -- add to last full timestep
            elif r.name == 'timestamp_16':
                to32 = int(d['last_full']/2**16) * 2**16 + r.value
                debug(" * looking at converted %d" % to32)

                # rolled over 16bits before we got next full timestamp
                if(to32 < d['last_full']):
                    to32 = to32 + 2**16
                    debug(" * overrun, inc by 16bits: %d" % to32)
                d['time'] = datetime.utcfromtimestamp(UTC_REFERENCE + to32)
                debug("   * updateing to %s" % d['time'])

            elif r.name == 'heart_rate':
                print("%s\t%s" % (d['time'], r.value))
                hr.append({'time': d['time'], 'hr': r.value})
            else:
                debug("? %s %s" % (r.name, r.value))
    return(hr)


if __name__ == "__main__":
    for zfile in sys.argv[1:]:
        with zipfile.ZipFile(zfile) as z:
            for n in z.namelist():
                if not re.match('.*.fit', n):
                    print("%s is not a fit file in zip %s" % (n, zfile))
                with z.open(n) as ffile:
                    get_hr_values(FitFile(ffile))

