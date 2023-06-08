from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/data')
def get_data():
    values = data_handler.get_values()
    return jsonify(values)

if __name__ == '__main__':
    app.run()