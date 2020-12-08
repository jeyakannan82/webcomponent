from urllib.request import urlopen
import simplejson

host = 'lngrdul-7015703.legal.regn.net'
port = '8983'
collection = "core1"
# fl = "id,name"
fl = ""
# qt = "select"
qt = "select"
fq = ""
rows = "10"
url = 'http://' + host + ':' + port + '/solr/' + collection + '/select?q='


class SolrURLConnection(object):
    connection = None

    @classmethod
    def execute_query(cls, query, attribute, stats_field):
        """execute query on singleton db connection"""
        solr_url = '{0}{1}'.format(url, query)
        print(solr_url)
        response = "None"
        try:
            rsp = urlopen(solr_url)
            response = simplejson.load(rsp)
            # print("number of matches=", response['response']['docs'])
            print('try in solr request')
            if attribute == "response":
                response = response['response']['docs']
            else:
                response = response['stats']['stats_fields'][stats_field]
        except Exception as e:
            print("Oops!", e.__class__, "occurred.")
        else:
            return response
