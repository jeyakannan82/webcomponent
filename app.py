#!flask/bin/python
# ! /usr/bin/python

from DashboardBuilder import Director, ConcreteDashboardBuilder
from ExperienceBuilder import ExperienceDirector, ConcreteExperienceBuilder
from SolrURLSearch import SolrURLConnection
from RecommendationBuilder import ConcreteRecommendationBuilder, RecommendationDirector
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

fromdate = datetime.strptime('11/22/2020', '%m/%d/%Y').strftime('%Y-%m-%dT%H:%M:%SZ')


# fromdate = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')

def execute_solr_url_query_by_facet(query):
    # calculate the square of the value of x
    return SolrURLConnection.execute_facet_query(query)


def execute_solr_url_query_by_response_time(query):
    # calculate the square of the value of x
    return SolrURLConnection.execute_query(query, "stats", "response_time")


def execute_solr_url_query_by_response(query):
    # calculate the square of the value of x
    return SolrURLConnection.execute_query(query, "response")


def execute_solr_query_by_response_time(query):
    # calculate the square of the value of x
    return SolrURLConnection.execute_exp_query(query, "facet")


def execute_solr_query_by_response(query):
    # calculate the square of the value of x
    return SolrURLConnection.execute_exp_query(query, "response")


@app.route('/aztecs/custScores', methods=['GET'])
def get_scores():
    facet_query = ["*%3A*&wt=json&wt=json&fl=type&indent=true&facet=true&stats=true&stats.field=status&facet.pivot"
                   "=userID,status ", "*%3A*&wt=json&wt=json&fl=type&indent=true&facet=true&stats=true"
                                      "&stats.field=status&facet.pivot=type ",
                   "*%3A*&wt=json&wt=json&fl=type&indent=true&facet=true&stats=true&stats.field=status"
                   "&facet.range={!tag=r1}date&f.date.facet.range.start=2020-11-01T23:59:59Z"
                   "&f.date.facet.range.end=2020-12-01T23:59:59Z&f.date.facet.range.gap=%2B1DAY"
                   "&facet.pivot={!range=r1}status",
                   "*%3A*&wt=json&wt=json&fl=type&indent=true&facet=true&stats=true&stats.field=status"
                   "&facet.range={!tag=r1}date&f.date.facet.range.start=2020-10-01T23:59:59Z"
                   "&f.date.facet.range.end=2020-11-01T23:59:59Z&f.date.facet.range.gap=%2B1DAY"
                   "&facet.pivot={!range=r1}status"]
    agents = 4
    chunksize = 3
    with Pool(processes=agents) as pool:
        result = pool.map(execute_solr_url_query_by_facet, facet_query, chunksize)

    # Output the result
    print('Result:  ' + str(result[0]))

    director = Director()
    builder = ConcreteDashboardBuilder()
    director.builder = builder

    director.build_NPS_score(result[0]['facet_counts']['facet_pivot']['userID,status'], ['OK', 'UF', 'IF'])
    director.build_activity_by_action(result[1]['facet_counts']['facet_pivot']['type'], ['type'])
    director.build_customer_experience(result[2]['facet_counts']['facet_pivot'], 'current')
    director.build_customer_experience(result[3]['facet_counts']['facet_pivot'], 'previous')
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


@app.route('/aztecs/customerExperience', methods=['GET'])
def get_customerExperience():
    print("Starting ThreadPoolExecutor")
    futures = []
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    start_date, end_date, range_gap = send_dates_with_range(start_date, end_date)
    print(range_gap)
    query = [
        "*%3A*&wt=json&wt=json&fl=type&indent=true&facet=true&stats=true&stats.field=status"
        "&facet.range={!tag=r1}date&f.date.facet.range.start="+start_date+
        "&f.date.facet.range.end="+end_date+"&f.date.facet.range.gap=%2B1"+range_gap+
        "&facet.pivot={!range=r1}status",
        "*%3A*&wt=json&wt=json&fl=type&indent=true&facet=true&stats=true&stats.field=status"
        "&facet.range={!tag=r1}date&f.date.facet.range.start="+start_date+
        "&f.date.facet.range.end="+end_date+"&f.date.facet.range.gap=%2B1"+range_gap+
        "&facet.pivot={!range=r1}status"
    ]

    # Run this with a pool of 5 agents having a chunksize of 3 until finished
    agents = 2
    chunksize = 2

    with Pool(processes=agents) as pool:
        result = pool.map(execute_solr_url_query_by_facet, query, chunksize)
    print("All tasks complete")
    director = Director()
    builder = ConcreteDashboardBuilder()
    director.builder = builder

    director.build_customer_experience(result[0]['facet_counts']['facet_pivot'], 'current')
    director.build_customer_experience(result[1]['facet_counts']['facet_pivot'], 'previous')
    customer_experience = builder.customerData.getCustomerExperience()

    return jsonify({'experience': customer_experience})


@app.route('/aztecs/npsScore', methods=['GET'])
def get_npsScore():
    print("Starting ThreadPoolExecutor")
    futures = []
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    start_date, end_date = send_dates(start_date, end_date)

    query = "*%3A*&wt=json&fl=type&fq=date%3A%5B"+start_date+"%20TO%20"+end_date+"%5D&indent=true&facet=true&stats=true" \
            "&stats.field=status&facet.pivot=userID,status "
    result = SolrURLConnection.execute_facet_query(query)
    print("NPS Score complete")
    director = Director()
    builder = ConcreteDashboardBuilder()
    director.builder = builder
    # print(result[0])

    director.build_NPS_score(result['facet_counts']['facet_pivot']['userID,status'], ['OK', 'UF', 'IF'])
    nps_scores = builder.customerData.getNPSScore()
    month_scores = []
    for nps1 in nps_scores:
        for nps in nps1:
            if nps in 'score':
                month_scores.append(nps1[nps])

    return jsonify({'npsScore': calculate_nps(month_scores), 'monthScore': calculate_month_score(month_scores)})

@app.route('/aztecs/reliability', methods=['GET'])
def get_reliability():
    print("Starting Reliability ThreadPoolExecutor")
    futures = []
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    start_date, end_date, range_gap = send_dates_with_range(start_date, end_date)
    print(start_date)
    print(end_date)
    query = ["status%3AUF&wt=json&fl=type&indent=true&facet=true&facet.range=date"
             "&f.date.facet.range.start="+start_date+"&f.date.facet.range.end="+end_date+
             "&f.date.facet.range.gap=%2b1"+range_gap+"&facet.range=date",
             "status%3AIF&wt=json&fl=type&indent=true&facet=true&facet.range=date"
             "&f.date.facet.range.start="+start_date+"&f.date.facet.range.end="+end_date+
             "&f.date.facet.range.gap=%2b1"+range_gap+"&facet.range=date",
             "status%3AOK&wt=json&fl=type&indent=true&facet=true&facet.range=date"
             "&f.date.facet.range.start="+start_date+"&f.date.facet.range.end="+end_date+
             "&f.date.facet.range.gap=%2b1"+range_gap+"&facet.range=date"]

    # Run this with a pool of 5 agents having a chunksize of 3 until finished
    agents = 3
    chunksize = 3

    with Pool(processes=agents) as pool:
        result = pool.map(execute_solr_url_query_by_facet, query, chunksize)

    print("Reliability complete")
    director = Director()
    builder = ConcreteDashboardBuilder()
    director.builder = builder
    # print(result[0])
    director.build_UF(result[0]['facet_counts']['facet_ranges']['date']['counts'], ['OK', 'UF', 'IF'])
    director.build_IF(result[1]['facet_counts']['facet_ranges']['date']['counts'], ['OK', 'UF', 'IF'])
    director.build_OK(result[2]['facet_counts']['facet_ranges']['date']['counts'], ['OK', 'UF', 'IF'])

    return jsonify({'reliability': builder.customerData.getReliabilityData()})

@app.route('/aztecs/availability', methods=['GET'])
def get_availability():
    print("Starting Availability ThreadPoolExecutor")
    futures = []
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    start_date, end_date, range_gap = send_dates_with_range(start_date, end_date)

    query = ["status%3AUF&wt=json&fl=type&indent=true&facet=true&facet.range=date"
             "&f.date.facet.range.start="+start_date+"&f.date.facet.range.end="+end_date+
             "&f.date.facet.range.gap=%2b1"+range_gap+"&facet.range=date",
             "status%3AIF&wt=json&fl=type&indent=true&facet=true&facet.range=date"
             "&f.date.facet.range.start="+start_date+"&f.date.facet.range.end="+end_date+
             "&f.date.facet.range.gap=%2b1"+range_gap+"&facet.range=date",
             "status%3AOK&wt=json&fl=type&indent=true&facet=true&facet.range=date"
             "&f.date.facet.range.start="+start_date+"&f.date.facet.range.end="+end_date+
             "&f.date.facet.range.gap=%2b1"+range_gap+"&facet.range=date"]

    # Run this with a pool of 5 agents having a chunksize of 3 until finished
    agents = 3
    chunksize = 3

    with Pool(processes=agents) as pool:
        result = pool.map(execute_solr_url_query_by_facet, query, chunksize)

    print("Availability complete")
    director = Director()
    builder = ConcreteDashboardBuilder()
    director.builder = builder
    # print(result[0])
    director.build_UF(result[0]['facet_counts']['facet_ranges']['date']['counts'], ['OK', 'UF', 'IF'])
    director.build_IF(result[1]['facet_counts']['facet_ranges']['date']['counts'], ['OK', 'UF', 'IF'])
    director.build_OK(result[2]['facet_counts']['facet_ranges']['date']['counts'], ['OK', 'UF', 'IF'])

    return jsonify({'availability': builder.customerData.getReliabilityData()})

@app.route('/aztecs/response', methods=['GET'])
def get_response():
    print("Starting Response ThreadPoolExecutor")
    futures = []
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    start_date, end_date = send_dates(start_date, end_date)
    query = "*%3A*&fl=date%2C%20response_time&fq=date%3A%5B"+start_date+"%20TO%20"+end_date+"%5D&sort=date%20asc"
    print(query)

    result = SolrURLConnection.execute_facet_query(query)

    print("Response complete")
    director = Director()
    builder = ConcreteDashboardBuilder()
    director.builder = builder
    # print(result[0])
    director.build_response(result['response']["docs"], ['mean'])

    return jsonify({'response': builder.customerData.getResponseData()})

@app.route('/aztecs/satisfactions', methods=['GET'])
def get_satisfactions():
    print("Starting Satisfactions ThreadPoolExecutor")
    futures = []
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    start_date, end_date = send_dates(start_date, end_date)

    query ="*%3A*&wt=json&fl=type&fq=date%3A%5B"+start_date+"%20TO%20"+end_date+"%5D&indent=true&facet=true&stats=true&stats.field=status&facet.pivot" \
           "=userID,status "

    result = SolrURLConnection.execute_facet_query(query)

    print("Satisfactions complete")
    director = Director()
    builder = ConcreteDashboardBuilder()
    director.builder = builder
    # print(result[0])

    director.build_NPS_score(result['facet_counts']['facet_pivot']['userID,status'], ['OK', 'UF', 'IF'])
    nps_scores = builder.customerData.getNPSScore()
    month_scores = []
    for nps1 in nps_scores:
        for nps in nps1:
            if nps in 'score':
                month_scores.append(nps1[nps])


    return jsonify({'satisfactions': calculate_satisfaction_score(month_scores)})

@app.route('/aztecs/activityByAction', methods=['GET'])
def get_activityByAction():
    print("Starting ActivityByAction ThreadPoolExecutor")
    futures = []
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    start_date, end_date = send_dates(start_date, end_date)

    query ="*%3A*&wt=json&fl=type&fq=date%3A%5B"+start_date+"%20TO%20"+end_date+"%5D&indent=true&facet=true&stats=true" \
           "&stats.field=status&facet.pivot=type "

    result = SolrURLConnection.execute_facet_query(query)

    print("ActivityByAction complete")
    director = Director()
    builder = ConcreteDashboardBuilder()
    director.builder = builder
    director.build_activity_by_action(result['facet_counts']['facet_pivot']['type'], ['type'])
    activityByAction = builder.customerData.getActivityByApi()

    return jsonify({'activityByAction': user_activity_by_apy(activityByAction)})

@app.route('/aztecs/customer_experience', methods=['GET'])
def get_customer_experience():
    print("Starting Customer Experience ThreadPoolExecutor")
    futures = []
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    start_date, end_date, range_gap = send_dates_with_range(start_date, end_date)

    query = [
        "*%3A*&wt=json&wt=json&fl=type&indent=true&facet=true&stats=true&stats.field=status"
        "&facet.range={!tag=r1}date&f.date.facet.range.start="+start_date+
        "&f.date.facet.range.end="+end_date+"&f.date.facet.range.gap=%2B1"+range_gap+
        "&facet.pivot={!range=r1}status",
        "*%3A*&wt=json&wt=json&fl=type&indent=true&facet=true&stats=true&stats.field=status"
        "&facet.range={!tag=r1}date&f.date.facet.range.start="+start_date+
        "&f.date.facet.range.end="+end_date+"&f.date.facet.range.gap=%2B1"+range_gap+
        "&facet.pivot={!range=r1}status"
    ]

    # Run this with a pool of 2 agents having a chunksize of 2 until finished
    agents = 2
    chunksize = 2

    with Pool(processes=agents) as pool:
        result = pool.map(execute_solr_url_query_by_facet, query, chunksize)

    print("Customer Experience complete")
    director = Director()
    builder = ConcreteDashboardBuilder()
    director.builder = builder
    director.build_customer_experience(result[0]['facet_counts']['facet_pivot'], 'current')
    director.build_customer_experience(result[1]['facet_counts']['facet_pivot'], 'previous')
    customer_experience = builder.customerData.getCustomerExperience()

    return jsonify({'experience': customer_experience})


@app.route('/aztecs/dashboards', methods=['GET'])
def get_tasks():
    print("Starting ThreadPoolExecutor")
    futures = []

    query = ["status%3AUF&wt=json&fl=type&indent=true&facet=true&facet.range=date"
             "&f.date.facet.range.start=2020-12-01T23%3A59%3A59Z&f.date.facet.range.end=2020-12-07T23%3A59%3A59Z"
             "&f.date.facet.range.gap=%2b1DAY&facet.range=date",
             "status%3AIF&wt=json&fl=type&indent=true&facet=true&facet.range=date"
             "&f.date.facet.range.start=2020-12-01T23%3A59%3A59Z&f.date.facet.range.end=2020-12-07T23%3A59%3A59Z"
             "&f.date.facet.range.gap=%2b1DAY&facet.range=date",
             "status%3AOK&wt=json&fl=type&indent=true&facet=true&facet.range=date"
             "&f.date.facet.range.start=2020-12-01T23%3A59%3A59Z&f.date.facet.range.end=2020-12-07T23%3A59%3A59Z"
             "&f.date.facet.range.gap=%2b1DAY&facet.range=date",
             "*%3A*&fl=date%2Cresponse_time&sort=date%20asc",
             "*%3A*&wt=json&wt=json&fl=type&indent=true&facet=true&stats=true&stats.field=status&facet.pivot"
             "=userID,status ", "*%3A*&wt=json&wt=json&fl=type&indent=true&facet=true&stats=true"
                                "&stats.field=status&facet.pivot=type ",
             "*%3A*&wt=json&wt=json&fl=type&indent=true&facet=true&stats=true&stats.field=status"
             "&facet.range={!tag=r1}date&f.date.facet.range.start=2020-11-01T23:59:59Z"
             "&f.date.facet.range.end=2020-12-01T23:59:59Z&f.date.facet.range.gap=%2B1DAY"
             "&facet.pivot={!range=r1}status",
             "*%3A*&wt=json&wt=json&fl=type&indent=true&facet=true&stats=true&stats.field=status"
             "&facet.range={!tag=r1}date&f.date.facet.range.start=2020-10-01T23:59:59Z"
             "&f.date.facet.range.end=2020-11-01T23:59:59Z&f.date.facet.range.gap=%2B1DAY"
             "&facet.pivot={!range=r1}status"
             ]

    # Run this with a pool of 5 agents having a chunksize of 3 until finished
    agents = 8
    chunksize = 8

    with Pool(processes=agents) as pool:
        result = pool.map(execute_solr_url_query_by_facet, query, chunksize)

    print("All tasks complete")
    director = Director()
    builder = ConcreteDashboardBuilder()
    director.builder = builder
    # print(result[0])
    director.build_UF(result[0]['facet_counts']['facet_ranges']['date']['counts'], ['OK', 'UF', 'IF'])
    director.build_IF(result[1]['facet_counts']['facet_ranges']['date']['counts'], ['OK', 'UF', 'IF'])
    director.build_OK(result[2]['facet_counts']['facet_ranges']['date']['counts'], ['OK', 'UF', 'IF'])
    director.build_response(result[3]['response']["docs"], ['mean'])
    director.build_NPS_score(result[4]['facet_counts']['facet_pivot']['userID,status'], ['OK', 'UF', 'IF'])
    director.build_activity_by_action(result[5]['facet_counts']['facet_pivot']['type'], ['type'])
    director.build_customer_experience(result[6]['facet_counts']['facet_pivot'], 'current')
    director.build_customer_experience(result[7]['facet_counts']['facet_pivot'], 'previous')
    print("All tasks complete")
    nps_scores = builder.customerData.getNPSScore()
    customer_experience = builder.customerData.getCustomerExperience()
    activityByAction = builder.customerData.getActivityByApi()
    month_scores = []
    for nps1 in nps_scores:
        for nps in nps1:
            if nps in 'score':
                month_scores.append(nps1[nps])

    return jsonify({'reliability': builder.customerData.getReliabilityData(),
                    'availability': builder.customerData.getAvailabilityData(),
                    'response': builder.customerData.getResponseData(),
                    'satisfactions': calculate_satisfaction_score(month_scores),
                    'activityByAction': user_activity_by_apy(activityByAction), 'experience': customer_experience,
                    'npsScore': calculate_nps(month_scores),
                    'monthScore': calculate_month_score(month_scores)})


@app.route('/aztecs/experience', methods=['GET'])
def get_experience():
    # task = [task for task in tasks if task['id'] == task_id]
    # if len(task) == 0:
    # abort(404)
    print("Starting Experience Builder ThreadPoolExecutor")
    print(fromdate)

    facet_query = ["*%3A*&wt=json&fl=type&indent=true&facet=true&stats=true&stats.field=status&facet.pivot=status",
                   "*%3A*&wt=json&fl=type&indent=true&facet=true&stats=true&stats.field=status&facet.pivot=type",
                   "*%3A*&wt=json&wt=json&fl=type&indent=true&facet=true&stats=true&stats.field=status&facet.pivot"
                   "=userID,status ", "*%3A*&wt=json&wt=json&fl=type&indent=true&facet=true&stats=true"
                                      "&stats.field=status&facet.pivot=response_time "]

    experience_query = ["&wt=json&fl=type&indent=true&facet=true&stats=true&stats.field=status&facet.pivot=userID," \
                        "status ",
                        "&wt=json&fl=type&indent=true&stats=true&stats.field=response_time&facet=true&facet.pivot=userID," \
                        "response_time," \
                        "status&facet.field=status&omitHeader=true&group=true&group.field=userID&group.field=status"]
    agents = 3
    new_agent = 3
    with Pool(processes=agents) as pool:
        results = pool.map(execute_solr_url_query_by_facet, facet_query)

    with Pool(processes=new_agent) as pool:
        result_experience = pool.map(execute_solr_query_by_response_time, experience_query)

    # Output the result
    # print('Result:  ' + str(result[1]))
    # print('Result:  ' + str(result[0]))
    # print('Experience Response Time Result:  ' + str(result_experience[1]))
    # print("All tasks complete")
    # print('Success 2 Result:  ' + str(results[2]))
    director = ExperienceDirector()
    builder = ConcreteExperienceBuilder()
    director.builder = builder
    director.build_success_rate(results[0]['facet_counts']['facet_pivot']['status'], ['value', 'count'])
    director.build_uptime(results[0]['facet_counts']['facet_pivot'], ['status'])
    director.build_category(results[1], ['type'])
    director.build_good_experience(result_experience[0]['userID,status'], ['OK', 'IF', 'UF'])
    director.build_average_experience(result_experience[0]['userID,status'], ['OK', 'IF', 'UF'])
    director.build_bad_experience(result_experience[0]['userID,status'], ['OK', 'IF', 'UF'])
    good_experience_result = user_experience(builder.customerData.getGoodExperience())
    average_experience_result = user_experience(builder.customerData.getAverageExperience())
    bad_experience_result = user_experience(builder.customerData.getBadExperience())
    good_exp_sorted = sortedlist(good_experience_result)
    average_exp_sorted = sortedlist(average_experience_result)
    bad_exp_sorted = sortedlist(bad_experience_result)

    return jsonify({'successRate': builder.customerData.getSuccessData(),
                    'upTime': builder.customerData.getSuccessData(),
                    'category': builder.customerData.getCategoryData(),
                    'goodExperience': good_exp_sorted, 'averageExperience': average_exp_sorted,
                    'badExperience': bad_exp_sorted})

@app.route('/aztecs/successRate', methods=['GET'])
def get_successRate():
    print("Starting SuccessRate ThreadPoolExecutor")
    futures = []
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    start_date, end_date = send_dates(start_date, end_date)

    query = "*%3A*&wt=json&fl=type&fq=date%3A%5B"+start_date+"%20TO%20"+end_date+"%5D&indent=true&facet=true&stats=true&stats.field=status&facet.pivot=status"

    result = SolrURLConnection.execute_facet_query(query)

    print("SuccessRate complete")
    director = ExperienceDirector()
    builder = ConcreteExperienceBuilder()
    director.builder = builder
    director.build_success_rate(result['facet_counts']['facet_pivot']['status'], ['value', 'count'])

    return jsonify({'successRate': builder.customerData.getSuccessData()})

@app.route('/aztecs/upTime', methods=['GET'])
def get_upTime():
    print("Starting UpTime ThreadPoolExecutor")
    futures = []
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    start_date, end_date = send_dates(start_date, end_date)

    query = "*%3A*&wt=json&fl=type&fq=date%3A%5B"+start_date+"%20TO%20"+end_date+"%5D&indent=true&facet=true&stats=true&stats.field=status&facet.pivot=status"

    result = SolrURLConnection.execute_facet_query(query)

    print("UpTime complete")
    director = ExperienceDirector()
    builder = ConcreteExperienceBuilder()
    director.builder = builder
    director.build_success_rate(result['facet_counts']['facet_pivot']['status'], ['value', 'count'])

    return jsonify({'upTime': builder.customerData.getSuccessData()})

@app.route('/aztecs/category', methods=['GET'])
def get_category():
    print("Starting Category ThreadPoolExecutor")
    futures = []
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    start_date, end_date = send_dates(start_date, end_date)

    query = "*%3A*&wt=json&fl=type&fq=date%3A%5B"+start_date+"%20TO%20"+end_date+"%5D&indent=true&facet=true&stats=true&stats.field=status&facet.pivot=type"

    result = SolrURLConnection.execute_facet_query(query)

    print("Category complete")
    director = ExperienceDirector()
    builder = ConcreteExperienceBuilder()
    director.builder = builder
    director.build_category(result, ['type'])

    return jsonify({'category': builder.customerData.getCategoryData()})

@app.route('/aztecs/goodExperience', methods=['GET'])
def get_goodExperience():
    print("Starting GoodExperience ThreadPoolExecutor")
    futures = []
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    start_date, end_date = send_dates(start_date, end_date)

    query = "&wt=json&fl=type&fq=date%3A%5B"+start_date+"%20TO%20"+end_date+"%5D&indent=true&facet=true&stats=true&stats.field=status&facet.pivot=userID," \
                        "status "

    result = SolrURLConnection.execute_exp_query(query, "facet")

    print("GoodExperience complete")
    director = ExperienceDirector()
    builder = ConcreteExperienceBuilder()
    director.builder = builder
    director.build_good_experience(result['userID,status'], ['OK', 'IF', 'UF'])
    good_experience_result = user_experience(builder.customerData.getGoodExperience())
    good_exp_sorted = sortedlist(good_experience_result)

    return jsonify({'goodExperience': good_exp_sorted})

@app.route('/aztecs/averageExperience', methods=['GET'])
def get_averageExperience():
    print("Starting AverageExperience ThreadPoolExecutor")
    futures = []
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    start_date, end_date = send_dates(start_date, end_date)

    query = "&wt=json&fl=type&fq=date%3A%5B"+start_date+"%20TO%20"+end_date+"%5D&indent=true&facet=true&stats=true&stats.field=status&facet.pivot=userID," \
                        "status "

    result = SolrURLConnection.execute_exp_query(query, "facet")

    print("AverageExperience complete")
    director = ExperienceDirector()
    builder = ConcreteExperienceBuilder()
    director.builder = builder
    director.build_average_experience(result['userID,status'], ['OK', 'IF', 'UF'])
    average_experience_result = user_experience(builder.customerData.getAverageExperience())
    average_exp_sorted = sortedlist(average_experience_result)

    return jsonify({'averageExperience': average_exp_sorted})

@app.route('/aztecs/badExperience', methods=['GET'])
def get_badExperience():
    print("Starting BadExperience ThreadPoolExecutor")
    futures = []
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    start_date, end_date = send_dates(start_date, end_date)

    query = "&wt=json&fl=type&fq=date%3A%5B"+start_date+"%20TO%20"+end_date+"%5D&indent=true&facet=true&stats=true&stats.field=status&facet.pivot=userID," \
                        "status "

    result = SolrURLConnection.execute_exp_query(query, "facet")

    print("BadExperience complete")
    director = ExperienceDirector()
    builder = ConcreteExperienceBuilder()
    director.builder = builder
    director.build_bad_experience(result['userID,status'], ['OK', 'IF', 'UF'])
    bad_experience_result = user_experience(builder.customerData.getBadExperience())
    bad_exp_sorted = sortedlist(bad_experience_result)

    return jsonify({'badExperience': bad_exp_sorted})

@app.route('/aztecs/recommendation', methods=['GET'])
def get_recommendation_data():
    # task = [task for task in tasks if task['id'] == task_id]
    # if len(task) == 0:
    # abort(404)
    print("Starting recommendation Builder ThreadPoolExecutor")
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    start_date, end_date = send_dates(start_date, end_date)

    facet_query = ["*%3A*&wt=json&fl=type&fq=date%3A%5B"+start_date+"%20TO%20"+end_date+"%5D&indent=true&facet=true&stats=true&stats.field=status&facet.pivot=type,"
                   "response_code", "*%3A*&wt=json&fq=date%3A%5B"+start_date+"%20TO%20"+end_date+"%5D"]
    agents = 2

    with Pool(processes=agents) as pool:
        results = pool.map(execute_solr_url_query_by_facet, facet_query)

    # Output the result
    # print('Result:  ' + str(result[1]))
    # print('Result:  ' + str(result[0]))
    # print('Result:  ' + str(result[3]))
    # print("All tasks complete")

    recommendation_director = RecommendationDirector()
    recommendation_builder = ConcreteRecommendationBuilder()
    recommendation_director.builder = recommendation_builder
    # print(results[0])
    recommendation_director.build_Radar_data(results[0], ['OK', 'UF', 'IF'])
    # director.build_good_experience(results[0]['userID,status'], ['OK', 'IF', 'UF'])
    # director.build_customer_experience(results[1]) director.build_average_experience(result[3], ['date', 'userID',
    # 'type', 'response_code', 'response_time', 'status','isPremiumUser']) director.build_bad_experience(result[3],
    # ['date', 'userID', 'type', 'response_code', 'response_time', 'status','isPremiumUser'])
    # goodExperienceResult = goodexperienceuser(builder.customerData.getGoodExperience())
    # sorted = sortedlist(goodExperienceResult)
    radar_Data = recommendation_builder.customerData.getRadarData()

    return jsonify({'radarData': radar_Data, 'caption': recommendation_builder.customerData.getCaption(),
                    'errorCode': recommendation_builder.customerData.getErrorCodes()})

@app.route('/aztecs/radarData', methods=['GET'])
def get_radarData():
    # task = [task for task in tasks if task['id'] == task_id]
    # if len(task) == 0:
    # abort(404)
    print("Starting RadarData ThreadPoolExecutor")
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    start_date, end_date = send_dates(start_date, end_date)

    query = "*%3A*&wt=json&fl=type&fq=date%3A%5B"+start_date+"%20TO%20"+end_date+"%5D&indent=true&facet=true&stats=true&stats.field=status&facet.pivot=type," \
                  "response_code"

    result = SolrURLConnection.execute_facet_query(query)

    recommendation_director = RecommendationDirector()
    recommendation_builder = ConcreteRecommendationBuilder()
    recommendation_director.builder = recommendation_builder
    # print(results[0])
    recommendation_director.build_Radar_data(result, ['OK', 'UF', 'IF'])
    radar_Data = recommendation_builder.customerData.getRadarData();

    return jsonify({'radarData': radar_Data })

@app.route('/aztecs/caption', methods=['GET'])
def get_caption():
    # task = [task for task in tasks if task['id'] == task_id]
    # if len(task) == 0:
    # abort(404)
    print("Starting Recommendation Caption")
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    start_date, end_date = send_dates(start_date, end_date)

    query = "*%3A*&wt=json&fl=type&fq=date%3A%5B"+start_date+"%20TO%20"+end_date+"%5D&indent=true&facet=true&stats=true&stats.field=status&facet.pivot=type," \
            "response_code"

    result = SolrURLConnection.execute_facet_query(query)

    recommendation_director = RecommendationDirector()
    recommendation_builder = ConcreteRecommendationBuilder()
    recommendation_director.builder = recommendation_builder
    # print(results[0])
    recommendation_director.build_Radar_data(result, ['OK', 'UF', 'IF'])
    radar_Data = recommendation_builder.customerData.getRadarData();

    return jsonify({'caption': recommendation_builder.customerData.getCaption()})

@app.route('/aztecs/errorCode', methods=['GET'])
def get_errorCode():
    # task = [task for task in tasks if task['id'] == task_id]
    # if len(task) == 0:
    # abort(404)
    print("Starting Recommendation Error Codes")
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    start_date, end_date = send_dates(start_date, end_date)

    query = "*%3A*&wt=json&fl=type&fq=date%3A%5B"+start_date+"%20TO%20"+end_date+"%5D&indent=true&facet=true&stats=true&stats.field=status&facet.pivot=type," \
            "response_code"

    result = SolrURLConnection.execute_facet_query(query)

    recommendation_director = RecommendationDirector()
    recommendation_builder = ConcreteRecommendationBuilder()
    recommendation_director.builder = recommendation_builder
    # print(results[0])
    recommendation_director.build_Radar_data(result, ['OK', 'UF', 'IF'])
    radar_Data = recommendation_builder.customerData.getRadarData();

    return jsonify({'errorCode': recommendation_builder.customerData.getErrorCodes()})

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
