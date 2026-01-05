from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/chat', methods=['POST'])
def chat():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    if 'query' not in data:
        return jsonify({"error": "Missing query in request"}), 400

    query = data['query']

    # Dummy response
    response = {
        "sources": [
            {"name": "Source 1", "url": "http://example.com/source1"},
            {"name": "Source 2", "url": "http://example.com/source2"}
        ],
        "response": f"This is a dummy response to your query: '{query}'"
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run(port=8000, debug=True)
