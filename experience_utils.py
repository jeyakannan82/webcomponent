import random

from collections import Counter
from collections import defaultdict
import json
from datetime import datetime
from datetime import timedelta
from copy import deepcopy
from itertools import groupby
from operator import itemgetter

def successfailurecount(response_types):
    server_failures = 0
    user_failures = 0
    success = 0
    total = len(response_types)

    for status in response_types:
        if status['status']=='IF':
            server_failures += 1
        elif status['status']=='UF':
            user_failures += 1
        elif status['status']=='OK':
            success += 1
        else:
            raise Exception("Invalid Output: {}".format(status))
    return [{'y': round((success / total) * 100, 0), 'label': 'Success'},
            {'y': round((user_failures / total) * 100, 0), 'label': 'User Failures'},
            {'y': round((server_failures / total) * 100, 0), 'label': 'Server Failures'}]


def typeCount(typeResponse):
    uptime_count = 0
    downtime_count = 0
    total = len(typeResponse)

    for status in typeResponse:
        if status['status']=='IF' or status['status']=='UF':
            downtime_count += 1
        elif status['status']=='OK':
            uptime_count += 1
        else:
            raise Exception("Invalid Output: {}".format(status))
    return [{'y': round((uptime_count / total) * 100, 0), 'label': 'Up Time'},
            {'y': round((downtime_count / total) * 100, 0), 'label': 'Down Time'}]


def categorycount(categoryCounts):
    search = 0
    retrieve = 0
    suggest = 0
    download=0
    multisearch=0
    total = len(categoryCounts)

    for type in categoryCounts:
        if type['type']=='search':
            search += 1
        elif type['type']=='retrieve':
            retrieve += 1
        elif type['type']=='suggest':
            suggest += 1
        elif type['type'] == 'download':
            download += 1
        elif type['type'] == 'multisearch':
            multisearch += 1
        else:
            raise Exception("Invalid Output: {}".format(type))
    return [{'y': round((search / total) * 100, 0), 'label': 'Search'},
            {'y': round((retrieve / total) * 100, 0), 'label': 'Retrieve'},
            {'y': round((suggest / total) * 100, 0), 'label': 'Suggest'},
            {'y': round((download / total) * 100, 0), 'label': 'Download'},
            {'y': round((multisearch / total) * 100, 0), 'label': 'Multi Search'}]

def user_experience(good_results):
    seen = set()
    new_l = []
    for d in good_results:
        t = tuple(d.items())
        if t not in seen:
            seen.add(t)
            new_l.append(d)
    return new_l

def sortedlist(sorted_list):
    new_data = []
    not_found = True
    for item in sorted_list:
        for new_item in new_data:
            not_found = True
            if item['userID'] == new_item['userID']:
                not_found = False
                # for data_item in new_item['details']:
                    # if item['userID'] == date['userID']:
                new_data['userID'].append({'success': item['success'],'user_failed': item['user_failed'],
                                                                                        'server_failed': item['server_failed'],'percentage': item['percentage'],'meetExp': item['meet']})
                break
        if not_found:
            new_data.append({'userID': item['userID'], 'success': item['success'],'user_failed': item['user_failed'],
                                                                                        'server_failed': item['server_failed'],'percentage': item['percentage'],'meetExp': item['meet']})
    return new_data

