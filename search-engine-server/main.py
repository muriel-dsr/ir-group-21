from quart import Quart, request, Response
from quart_cors import route_cors
from retrieval_model import retrieval_model
import json

# Create engine
app = Quart(__name__)


#  Add a test route - for debug purposes
@app.route('/test')
@route_cors(allow_origin="*")
def home_route():
    return {"test": "again"}


# Add a route which accepts a user query and returns a ranked set of results
@app.route('/data')
@route_cors(allow_origin="*")
async def data():
    query_string = request.query_string.decode("utf-8")

    # code to process query and determine results
    results = list(await retrieval_model(query_string))

    # return response to the client side
    return json.dumps(results), 200, {"Access-Control-Allow-Origin": "*"}


# Start the app when the code is executed
if __name__ == "__main__":
    app.run()
