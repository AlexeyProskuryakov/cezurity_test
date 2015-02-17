# coding:utf-8
from flask.templating import render_template

__author__ = '4ikist'
from flask import jsonify, Flask, request
import json
import database as db

app = Flask('hierarchy')


@app.route('/')
def main():
    return render_template('index.html')


@app.route('/roots')
def form_roots():
    roots = db.get_children(None)
    return jsonify(roots=roots)


@app.route('/children', methods=['GET'])
def get_children():
    try:
        id = int(request.args.get('id', -1))
    except ValueError as e:
        return jsonify(ok=False, details=e.message)
    result = db.get_children(id if id != -1 else None)
    return jsonify(result=result, ok=True)


@app.route('/manage_element', methods=['DELETE', 'POST'])
def manage_element():
    id = request.form.get('id')
    if request.method == 'DELETE':
        db.delete_element(id)
    if request.method == 'POST':
        new_label = request.form.get('new_label')
        db.change_element_label(id, new_label)
    return jsonify(ok=True)


@app.route('/label', methods=['POST'])
def form_paths():
    label = request.form.get('label')
    result = db.get_elements_by_label(label)
    return jsonify(ok=True, result=result)


@app.route('/level', methods=['POST'])
def form_level():
    try:
        level = int(request.form.get('level'))
    except ValueError as e:
        return jsonify(ok=False, details=e.message)

    result = db.get_elements_by_level(level)
    return jsonify(ok=True, result=result)


if __name__ == '__main__':
    app.run(host='localhost', port=8888)