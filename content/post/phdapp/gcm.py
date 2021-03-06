from pprint import pprint
from urllib.request import urlopen
from datetime import datetime, tzinfo
import pytz
import re
import argparse
import os


parser = argparse.ArgumentParser(description='Type your query.')
parser.add_argument('-i', '--institution')
parser.add_argument('-p', '--program')

if __name__ == '__main__':
    # parsing query
    args = parser.parse_args()
    query = ''
    if args.institution:
        query += ('+' if query else '') + args.institution
    if args.program:
        query += ('+' if query else '') + args.program

    # parsing url
    with urlopen(f'https://www.thegradcafe.com/survey/index.php?q={query}&t=a&o=&pp=100') as response:
        html = response.read().decode()
    header = '<table class="submission-table">' + re.compile(
        '<table class="submission-table">(.*?)</thead>', re.DOTALL).findall(html)[0] + '</thead>'
    submissions = re.compile(
        '</thead>(.*?)</table>', re.DOTALL).findall(html)[0]

    # selecting only phds
    submissions_phd = ''
    for line in submissions.split('\n'):
        if re.search('<td class="tcol2">.+PhD.+\((F[0-9]{2})\)</td>', line):
            cmm = re.findall('<li>(.+)</li></ul></td></tr>', line)
            submissions_phd += re.sub('<td class="tcol6">.+</td></tr>',
                                      f'<td class="tcol6">{cmm[0] if cmm else ""}</td></tr>', line) + '\n'

    with open(f'pages/{query}.html', 'w') as html_file:
        tz = pytz.timezone('US/Eastern')
        time_stamp = datetime.now(tz).strftime("%Y-%m-%d %a %I:%M %p")
        html_file.writelines(
            '''<style>
table, th, td {
    border: 1px solid black;
    }
</style>
'''f'''
<h3>{query}</h3>
<h4>{time_stamp}</h4>

''' + header + submissions_phd + '</table>'
        )
