#!flask/bin/python
# ! /usr/bin/python

from DashboardBuilder import Director, ConcreteDashboardBuilder
from SolrSearch import SolrConnection
from flask import Flask, jsonify
from flask import abort
from flask import make_response
from flask import request
import concurrent.futures
from multiprocessing import Pool
import json

app = Flask(__name__)

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


def execute_solr_query(queries):
    return SolrConnection.execute_query(queries)


def square(query):
    # calculate the square of the value of x
    return SolrConnection.execute_query(query)


@app.route('/aztecs/dashboards', methods=['GET'])
def get_tasks():
    print("Starting ThreadPoolExecutor")
    futures = []
    # Define the dataset
    query = ["*:*", "*:*"]
    dataset = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]

    # Run this with a pool of 5 agents having a chunksize of 3 until finished
    agents = 5
    chunksize = 3
    with Pool(processes=agents) as pool:
        result = pool.map(square, query, chunksize)

    # Output the result
    print ('Result:  ' + str(result))
    print("All tasks complete")
    # results = SolrConnection.execute_query()
    # print(results)

    with Pool(processes=5) as pool:
        outputs = pool.map(execute_solr_query, query)
    # print("Output: {}".format(outputs))
    director = Director()
    builder = ConcreteDashboardBuilder()
    director.builder = builder
    director.build_reliability(result, 'type')
    # print(builder.customerData.getResponseData())
    # director.build_availability(reliability.result())
    # director.build_response(reliability.result())
    # director.build_customer_satisfaction(reliability.result())
    # director.build_activity_by_action(reliability.result())
    # director.build_customer_satisfaction(reliability.result())
    # director.build_NPS_score(reliability.result())
    # builder.customerData.list_data()
    return jsonify({'reliability': json.dumps(builder.customerData.getReliabilityData()), 'availability': tasks, 'response': tasks, 'satisfactions': tasks,
                    'activityByAction': tasks, 'experience': tasks, 'npsScore': tasks})


@app.route('/aztecs/experience', methods=['GET'])
def get_task(task_id):
    task = [task for task in tasks if task['id'] == task_id]
    if len(task) == 0:
        abort(404)
    return jsonify({'task': task[0]})


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
