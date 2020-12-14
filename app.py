#!flask/bin/python
# ! /usr/bin/python

from DashboardBuilder import Director, ConcreteDashboardBuilder
from ExperienceBuilder import ExperienceDirector, ConcreteExperienceBuilder
from SolrURLSearch import SolrURLConnection
from flask import Flask, jsonify
from flask import abort
from flask import make_response
from flask import request
from flask_cors import CORS

import concurrent.futures
from multiprocessing import Pool
import json
from datetime import datetime
from urllib.parse import urlencode
from nps_utils import *
from experience_utils import *

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
CORS(app)

tasks = [
    {
        'id': 1,
        'title': u'Buy groceries',
        'description': u'Milk, Cheese, Pizza, Fruit, Tylenol',
        'done': False
    },
    {
        'id': 2,
        'title': u'Learn Python',
        'description': u'Need to find a good Python tutorial on the web',
        'done': False
    }
]

fromdate = datetime.strptime('11/22/2020','%m/%d/%Y').strftime('%Y-%m-%dT%H:%M:%SZ')
# fromdate = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')

def execute_solr_url_query_by_facet(query):
    # calculate the square of the value of x
    return SolrURLConnection.execute_facet_query(query, "facet")


def execute_solr_url_query_by_response_time(query):
    # calculate the square of the value of x
    return SolrURLConnection.execute_query(query, "stats", "response_time")


def execute_solr_url_query_by_response(query):
    # calculate the square of the value of x
    return SolrURLConnection.execute_query(query, "response")

def execute_solr_query_by_response_time(query):
    # calculate the square of the value of x
    return SolrURLConnection.execute_exp_query(query, "stats", "response_time")


def execute_solr_query_by_response(query):
    # calculate the square of the value of x
    return SolrURLConnection.execute_exp_query(query, "response","")


@app.route('/aztecs/custScores', methods=['GET'])
def get_scores():
    facet_query = ["&wt=json&wt=json&fl=type&indent=true&facet=true&stats=true&stats.field=status&facet.pivot=userID," \
                   "status ",
                   "&wt=json&wt=json&fl=type&indent=true&facet=true&stats=true&stats.field=status&facet.pivot=type ",
                   "&wt=json&wt=json&fl=type&indent=true&facet=true&stats=true&stats.field=status"
                   "&facet.range={!tag=r1}date&f.date.facet.range.start=2020-11-01T23:59:59Z"
                   "&f.date.facet.range.end=2020-12-01T23:59:59Z&f.date.facet.range.gap=%2B1DAY"
                   "&facet.pivot={!range=r1}status",
                   "&wt=json&wt=json&fl=type&indent=true&facet=true&stats=true&stats.field=status"
                   "&facet.range={!tag=r1}date&f.date.facet.range.start=2020-10-01T23:59:59Z"
                   "&f.date.facet.range.end=2020-11-01T23:59:59Z&f.date.facet.range.gap=%2B1DAY"
                   "&facet.pivot={!range=r1}status"]
    agents = 3
    chunksize = 3
    with Pool(processes=agents) as pool:
        result = pool.map(execute_solr_url_query_by_facet, facet_query, chunksize)

    # Output the result
    print('Result:  ' + str(result[0]))

    director = Director()
    builder = ConcreteDashboardBuilder()
    director.builder = builder

    director.build_NPS_score(result[0]['userID,status'], ['OK', 'UF', 'IF'])
    director.build_activity_by_action(result[1]['type'], ['type'])
    director.build_customer_experience(result[2], 'current')
    director.build_customer_experience(result[3], 'previous')
    print("All tasks complete")
    nps_scores = builder.customerData.getNPSScore()
    customer_experience = builder.customerData.getCustomerExperience()
    activityByAction = builder.customerData.getActivityByApi()
    month_scores = []
    for nps1 in nps_scores:
        for nps in nps1:
            if nps in 'score':
                month_scores.append(nps1[nps])

    return jsonify({'satisfactions': calculate_satisfaction_score(month_scores),
                    'activityByAction': user_activity_by_apy(activityByAction), 'experience': customer_experience,
                    'npsScore': calculate_nps(month_scores),
                    'monthScore': calculate_month_score(month_scores)})


@app.route('/aztecs/dashboards', methods=['GET'])
def get_tasks():
    print("Starting ThreadPoolExecutor")
    futures = []
    # Define the dataset
    print(fromdate)
    # requestresponsedict = {'fq':'date:['+ str(fromdate) +' TO NOW]', 'fl':'id,date,response_code,response_time'}
    # requestavailabilitydict = {'fq': 'date:[' + str(fromdate) + ' TO NOW]', 'fl': 'response_code,response_time'}
    # requestreliabilitydict={'fl': 'type','fq': 'isPremiumUser:true', 'rows':'50'}

    requestresponsedict = {'fl':'status,response_code,response_time','rows':'10'}
    requestavailabilitydict = {'fl':'status,response_code,response_time','rows':'50'}

    # requestcategorydict = {'fq': 'date:[' + str(fromdate) + ' TO NOW]'}

    query = ["type:search&wt=json&" + urlencode(requestavailabilitydict),
             "*%3A*&wt=json&" + urlencode(requestresponsedict)]

    response_time_query = ["&wt=json&indent=true&stats=true&stats.field=response_time"]

    dataset = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]

    # Run this with a pool of 5 agents having a chunksize of 3 until finished
    agents = 5
    chunksize = 3

    with Pool(processes=agents) as pool:
        result = pool.map(execute_solr_query_by_response, query, chunksize)

    with Pool(processes=agents) as pool:
        responsetimeresult = pool.map(execute_solr_url_query_by_response_time, response_time_query, chunksize)

    # Output the result
    print('Result:  ' + str(result[0]))
    print('Result:  ' + str(result[1]))
    print('Result:  ' + str(responsetimeresult[0]))
    print("All tasks complete")
    # results = SolrConnection.execute_query()
    # print(results)

    # with Pool(processes=5) as pool:
    #    outputs = pool.map(execute_solr_query, query)
    # print("Output: {}".format(outputs))
    # facet_query = "&wt=json&wt=json&fl=type&indent=true&facet=true&stats=true&stats.field=status&facet.pivot=userID," \
                 # "status "
    # facet_result = SolrURLConnection.execute_query(facet_query, "facet", "userID,status")
    director = Director()
    builder = ConcreteDashboardBuilder()
    director.builder = builder
    director.build_reliability(responsetimeresult[0], ['sum', 'mean', 'count', 'min'])

    # director.build_NPS_score(facet_result, ['OK', 'UF', 'IF'])
    # nps_scores = builder.customerData.getNPSScore()
    #month_scores = []
    # for nps1 in nps_scores:
        # for nps in nps1:
            # if nps in 'score':
                # month_scores.append(nps1[nps])
    # director.build_NPS_score(facet_result, ['OK', 'UF', 'IF'])
    # nps_scores = builder.customerData.getNPSScore()
    # month_scores = []
    # for nps1 in nps_scores:
        # for nps in nps1:
            # print(nps)
            # if nps in 'score':
                # month_scores.append(nps1[nps])

    # print(calculate_month_score(month_scores), "({})".format(len(month_scores)))
    # print(builder.customerData.getResponseData())
    director.build_availability(result[0], ['response_code','response_time','status'])
    director.build_response(result[1], ['response_code','response_time','status'])
    # director.build_customer_satisfaction(reliability.result())
    # director.build_activity_by_action(reliability.result())
    # director.build_customer_satisfaction(reliability.result())
    # director.build_NPS_score(reliability.result())
    # builder.customerData.list_data()
    return jsonify({'reliability': builder.customerData.getReliabilityData(),
                    'availability': builder.customerData.getAvailabilityData(),
                    'response': builder.customerData.getResponseData()})

@app.route('/aztecs/experience', methods=['GET'])
def get_experience():
    # task = [task for task in tasks if task['id'] == task_id]
    # if len(task) == 0:
        # abort(404)
    print("Starting Experience Builder ThreadPoolExecutor")
    print(fromdate)
    requestsuccessdict = {'fl': 'status','rows':'50'}
    requesttimedict = {'fl': 'type','rows':'50'}
    requestcategorydict={'fl': 'type','fq': 'isPremiumUser:true', 'rows':'50'}
    # requestUserExperiencedict = {'rows': '10'}

    # requestcategorydict = {'fq': 'date:[' + str(fromdate) + ' TO NOW]'}

    query = ["type:search&wt=json&" + urlencode(requestsuccessdict),
             "*%3A*&wt=json&" + urlencode(requesttimedict),
             "*%3A*&wt=json&" + urlencode(requestcategorydict)]

    facet_query = ["&wt=json&fl=type&indent=true&facet=true&stats=true&stats.field=status&facet.pivot=userID," \
                   "status ",
                   "&wt=json&&fl=type&indent=true&facet=true&stats=true&stats.field=response_time&facet.pivot=userID," \
                    "response_time "]
    agents = 5
    chunksize = 3

    with Pool(processes=agents) as pool:
        results = pool.map(execute_solr_url_query_by_facet, facet_query, chunksize)

    dataset = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]

    # Run this with a pool of 3 agents having a chunksize of 3 until finished
    agents = 5
    chunksize = 3
    with Pool(processes=agents) as pool:
        result = pool.map(execute_solr_query_by_response, query, chunksize)


   # Output the result
    # print('Result:  ' + str(result[1]))
    # print('Result:  ' + str(result[0]))
    # print('Result:  ' + str(result[3]))
    # print("All tasks complete")
    director = ExperienceDirector()
    builder = ConcreteExperienceBuilder()
    director.builder = builder
    director.build_success_rate(result[0],['status'])
    director.build_uptime(result[0],['status'])
    director.build_category(result[2], ['type'])
    director.build_good_experience(results[0]['userID,status'], ['OK','IF','UF'])
    # director.build_customer_experience(results[1])
    # director.build_average_experience(result[3], ['date', 'userID', 'type', 'response_code', 'response_time', 'status','isPremiumUser'])
    # director.build_bad_experience(result[3], ['date', 'userID', 'type', 'response_code', 'response_time', 'status','isPremiumUser'])
    goodExperienceResult = goodexperienceuser(builder.customerData.getGoodExperience())
    sorted =sortedlist(goodExperienceResult)

    return jsonify({'successRate': successfailurecount(builder.customerData.getSuccessData()), 'upTime':typeCount(builder.customerData.getUptimeData()),
                    'category':categorycount(builder.customerData.getCategoryData()), 'goodExperience':goodExperienceResult})

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/aztecs/api/v1.0/tasks', methods=['POST'])
def create_task():
    if not request.json or not 'title' in request.json:
        abort(400)
    task = {
        'id': tasks[-1]['id'] + 1,
        'title': request.json['title'],
        'description': request.json.get('description', ""),
        'done': False
    }
    tasks.append(task)
    return jsonify({'task': task}), 201


@app.route('/aztecs/solutions/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = [task for task in tasks if task['id'] == task_id]
    if len(task) == 0:
        abort(404)
    if not request.json:
        abort(400)
    if 'title' in request.json and type(request.json['title']) != unicode:
        abort(400)
    if 'description' in request.json and type(request.json['description']) is not unicode:
        abort(400)
    if 'done' in request.json and type(request.json['done']) is not bool:
        abort(400)
    task[0]['title'] = request.json.get('title', task[0]['title'])
    task[0]['description'] = request.json.get('description', task[0]['description'])
    task[0]['done'] = request.json.get('done', task[0]['done'])
    return jsonify({'task': task[0]})


@app.route('/aztecs/api/v1.0/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = [task for task in tasks if task['id'] == task_id]
    if len(task) == 0:
        abort(404)
    tasks.remove(task[0])
    return jsonify({'result': True})


if __name__ == '__main__':
    app.run(debug=True)
