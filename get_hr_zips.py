#!/usr/bin/env python3
from garminexport.garminclient import GarminClient
from glob import glob
from datetime import date, timedelta
import re
import os
import os.path

f = open('creds.txt', 'r')
u_p = f.readline().strip().split(' ')

d_upto = date.today() - timedelta(days=1)
have = [re.sub('.zip', '', os.path.basename(x))
        for x in glob('hr/*zip')]
have.sort()
if have is None:
    d_from = date(2016, 12, 12)
else:
    ldate = [int(x) for x in have[-1].split('-')]
    d_from = date(*ldate) + timedelta(days=1)

# get date from file
need_days = [d_from for x in range((d_upto - d_from).days + 1)]
need_days = [x.strftime("%Y-%m-%d") for x in need_days]

with GarminClient(u_p[0], u_p[1]) as client:
    for i, d in enumerate(need_days):
        print("%d/%d: %s" % (i+1, len(need_days), d))
        r = client.session.get('https://connect.garmin.com/modern/proxy/' +
                               'download-service/files/wellness/%s' % d)

        if r.status_code != 200:
            print("failed to download %s" % d)
            continue

        with open('hr/%s.zip' % d, 'wb') as f:
                r.raw.decode_content = True
                f.write(r.content)
