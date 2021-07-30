from flask import Flask,jsonify
from create import app

@app.route('/')
def api():
    return jsonify({'name':'adedamola'})