import pprint
import pysolr
import pandas as pd
import json

host = 'lngrdul-7015703.legal.regn.net'
port = '8983'
collection = "core1"
q = "*:*"
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
    def execute_query(cls):
        """execute query on singleton db connection"""
        connection = cls.get_connection()
        results = None
        try:
            results = connection.search(q, **{
                'fl': fl,
                'fq': fq,
                'rows': rows
            })
        except:
            print('Exception in solr request')
        else:
            docs = pd.DataFrame(results.docs)
            return results.docs
    # print("Number of hits: {0}".format(len(results)))
    # for i in results:
    #    pprint.pprint(i)
