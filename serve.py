from flask import Flask, request
import json

app = Flask(__name__)
PATH_TO_JSON = 'versions.json'

@app.route('/api', methods=['POST'])
def api():
    # Load the JSON data from the file
    with open(PATH_TO_JSON, 'r') as f:
        data = json.load(f)

    # Get the request data from the POST request
    request_data = request.get_json()

    # Find the data in the JSON file that matches the request data
    result = None
    for item in data:
        if item['key'] == request_data['key']:
            result = item['value']
            break

    # Return the result as a JSON response
    return json.dumps({'result': result})

if __name__ == '__main__':
    app.run()