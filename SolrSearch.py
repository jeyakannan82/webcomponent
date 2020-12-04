import pprint
import pysolr
import pandas as pd
import json
from flask import Flask, jsonify

host = 'lngrdul-7015703.legal.regn.net'
port = '8983'
collection = "core1"
# fl = "id,name"
fl = ""
# qt = "select"
qt = "select"
fq = ""
rows = "10"
url = 'http://' + host + ':' + port + '/solr/' + collection


class SolrConnection(object):
    connection = None

    @classmethod
    def get_connection(cls, new=False):
        """Creates return new Singleton Solr connection"""
        if new or not cls.connection:
            cls.connection = pysolr.Solr(url, search_handler="/" + qt, timeout=5)
        return cls.connection

    @classmethod
    def execute_query(cls, query):
        """execute query on singleton db connection"""
        print(query)
        connection = cls.get_connection()
        response = []
        try:
            results = connection.search(query, **{
                'fl': fl,
                'fq': fq,
                'rows': rows
            })
            print('try in solr request')
        except:
            print('Exception in solr request')
        else:
            docs = pd.DataFrame(results.docs)
            print("Number of hits: {0}".format(len(results)))
            for i in results:
                pprint.pprint(i)
                # response.add(i)
            return results
