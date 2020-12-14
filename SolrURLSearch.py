from urllib.request import urlopen
import simplejson
import pprint

host = 'lngrdul-7015703.legal.regn.net'
port = '8983'
collection = "log_data_core"
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
    def execute_query(cls, query, attribute, fields):
        """execute query on singleton db connection"""
        solr_url = '{0}{1}'.format(url, "type:search" + query)
        print(solr_url)
        response = "None"
        try:
            rsp = urlopen(solr_url)
            response = simplejson.load(rsp)
            # print("number of matches=", response['response']['docs'])
            # pprint.pprint(response)
            print('try in solr request')
            if attribute in "stats":
                response = response['stats']['stats_fields'][fields]
            elif attribute in "facet":
                response = response['facet_counts']['facet_pivot'][fields]
            else:
                response = response['response']['docs']
        except Exception as e:
            print("Oops!", e.__class__, "occurred.")
        else:
            return response

    @classmethod
    def execute_exp_query(cls, query, attribute, stats_field):
        """execute query on singleton db connection"""
        solr_url = '{0}{1}'.format(url, query)
        print(solr_url)
        response = "None"
        try:
            rsp = urlopen(solr_url)
            response = simplejson.load(rsp)
            # print("number of matches=", response['response']['docs'])
            print('try in solr request')
            if attribute == "response" and stats_field=="":
                print('try in solr request')
                response = response['response']['docs']
            else:
                response = response['stats']['stats_fields'][stats_field]
        except Exception as e:
            print("Oops!", e.__class__, "occurred.")
        else:
            return response

    @classmethod
    def execute_facet_query(cls, query, attribute):
        """execute query on singleton db connection"""
        solr_url = '{0}{1}'.format(url, "*%3A*"+query)
        fields_array = query.split("=")
        print("*************")
        print(query)
        print(attribute)
        print(fields_array[len(fields_array)-1])
        response = "None"
        try:
            rsp = urlopen(solr_url)
            response = simplejson.load(rsp)
            print('try in solr request')
            if attribute in "response":
                response = response['stats']['stats_fields'][fields]
            elif attribute in "facet":
                response = response['facet_counts']['facet_pivot']
            else:
                response = response['response']['docs']
        except Exception as e:
            print("Oops!", e.__class__, "occurred.")
        else:
            return response
