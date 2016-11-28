import aiohttp
import asyncio
import async_timeout
import base64
import configparser
import json
import os
import datetime

from bs4 import BeautifulSoup


class TicketManager():
    def __init__(self, name):
        # print("Instanciating new TicketManager (%s)" % name)
        self.name = str(name).lower()
        self.is_today = False
        self.days = {}
        self.tm_days = []

    def feed_table_data(self, date, days):
        """
            feed with a new date (month + year) and a list of days (with bool
            if is ticketmanager or not)
        """
        # print("Feeding data to TicketManager(%s): \ndate: %s\ndays: %s" %
        #          (self.name, date, days))
        for day_index, is_tm in enumerate(days):
            date = datetime.date(date.year, date.month, day_index + 1)
            self.days[date] = is_tm
            if is_tm:
                self.tm_days.append(date)

        self.tm_days.sort()
        self.is_today = datetime.date.today() in self.tm_days

    def merge(self, ticketmanager):
        """
            merges two instances of the same TicketManager
        """
        if self.name != ticketmanager.name:
            raise Exception("Unable to merge - not the same TicketManager \
                            instance")

        self.tm_days += ticketmanager.tm_days
        self.tm_days.sort()
        for key, value in ticketmanager.days.items():
            if key not in self.days:
                self.days[key] = value
            else:
                raise Exception("Merge error - day was set more than once")

        if self.is_today or ticketmanager.is_today:
            self.is_today = True


def read_config():
    cfg_parser = configparser.ConfigParser()
    home = os.path.expanduser("~")
    cfg_parser.read('%s/.who_is_ticketmanager.cfg' % home)
    if len(cfg_parser.sections()) == 0:
        raise Exception('No configuration provided!')

    all_section = cfg_parser['ALL']
    proxy_cfg = all_section['proxy']
    url_cfg = all_section['url']
    username_cfg = all_section['username']
    password_cfg = all_section['password']
    return (proxy_cfg, url_cfg, username_cfg, password_cfg)


async def parse_json_response(json_res):
    json_data = json.loads(json_res)
    html_data = json_data['body']['view']['value']
    return html_data


def find_tables(html_page):
    soup = BeautifulSoup(html_page, 'html.parser')
    tables = soup.find_all('table', class_='confluenceTable')
    return tables


def extract_date_from_table_header(table_header):
    date = None
    if table_header:
        table_header_text = table_header.get_text()
        # header should be like: "November 2016"
        date = datetime.datetime.strptime(table_header_text, '%B %Y')
        return date
    else:
        raise Exception('No table header or no date string found!')


def extract_ticketmanagers_from_table(html_table):
    # TODO: this part of the code is shitty and should be rewritten using
    # less nested loops and be more expressive!
    soup = BeautifulSoup(str(html_table), 'html.parser')
    date = None

    is_first_row = True
    is_first_header = True
    # days_list = []
    # iterate through the table rows
    for row in soup.find_all('tr'):
        # first row (#0) is for date and days
        if is_first_row:
            for table_header in row.find_all('th'):
                if is_first_header:
                    date = extract_date_from_table_header(table_header)
                    is_first_header = False
                # else:
                    # days_list.append(table_header.get_text())

            is_first_row = False
        else:
            is_first_column = True
            ticketmanager = None
            days = []
            for column in row:
                column_text = column.get_text().strip()
                if is_first_column:
                    ticketmanager = TicketManager(column_text)
                    is_first_column = False
                else:
                    days.append(True if str.lower(column_text) == 'x'
                                else False)
            ticketmanager.feed_table_data(date, days)
            yield ticketmanager


def create_auth(username, password):
    raw_auth = '%s:%s' % (username, password)
    res = base64.b64encode(raw_auth.encode('utf-8'))
    return res

async def download_ticketmanager_site(session):
    # move this late rto a better position in the code...
    proxy, url, username, password = read_config()
    auth = 'Basic ' + create_auth(username, password).decode('utf-8')
    headers = {'Accept': 'application/json', 'Authorization': auth}

    with async_timeout.timeout(10):
        async with session.get(url, headers=headers, proxy=proxy) as response:
            return await response.text()


def print_beautiful(ticketmanager):
    today = datetime.date.today()
    upcoming = [day for day in ticketmanager.tm_days if day > today]
    print('Upcoming:')
    for day in upcoming:
        print('\t| %s %02d %02d | X |' % (day.year, day.month, day.day))

    print()


def print_status(ticketmanager):
    if ticketmanager.is_today:
        print("###################################")
        print('#                                 #')
        print("#   YOU ARE TICKETMANAGER TODAY   #")
        print('#                                 #')
        print("###################################")
    else:
        print("+----------------------------------+")
        print("| Today is not your day...         |")
        print("+----------------------------------+")


async def check(loop, name):
    async with aiohttp.ClientSession(loop=loop, ) as session:

        name = str(name).lower()

        json_response = await download_ticketmanager_site(session)
        html_data = await parse_json_response(json_response)

        tables = find_tables(html_data)
        ticketmanagers_dict = {}

        for table in tables:
            for tm in extract_ticketmanagers_from_table(table):
                if tm.name in ticketmanagers_dict.keys():
                    tm.merge(ticketmanagers_dict[tm.name])
                ticketmanagers_dict[tm.name] = tm

        if name in ticketmanagers_dict.keys():
            tm = ticketmanagers_dict[name]
            print_beautiful(tm)
            print_status(tm)
