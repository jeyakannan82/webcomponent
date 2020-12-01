#!flask/bin/python
# ! /usr/bin/python
from DashboardBuilder import Director, ConcreteDashboardBuilder
from SolrSearch import SolrConnection
from flask import Flask, jsonify
from flask import abort
from flask import make_response
from flask import request
from concurrent.futures import ThreadPoolExecutor

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


@app.route('/aztecs/dashboards', methods=['GET'])
def get_tasks():
    print("Starting ThreadPoolExecutor")
    with ThreadPoolExecutor(max_workers=10) as executor:
        reliability = executor.submit(SolrConnection.execute_query())
        future2 = executor.submit(SolrConnection.execute_query())
        future3 = executor.submit(SolrConnection.execute_query())
        print(future1.result())
    print("All tasks complete")
    # results = SolrConnection.execute_query()
    director = Director()
    builder = ConcreteBuilder()
    director.builder = builder
    director.build_reliability(reliability.result())
    director.build_availability(reliability.result())
    director.build_response(reliability.result())
    director.build_customer_satisfaction(reliability.result())
    director.build_activity_by_action(reliability.result())
    director.build_customer_satisfaction(reliability.result())
    director.build_NPS_score(reliability.result())
    builder.customerData.list_data()
    return jsonify({'reliability': tasks, 'availability': tasks, 'response': tasks, 'satisfactions': tasks, 'activityByAction': tasks, 'experience': tasks, 'npsScore': tasks})


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
