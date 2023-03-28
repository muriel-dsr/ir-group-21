from quart import Quart, request, Response
from quart_cors import route_cors
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

    # Need to add code here to process query and determine results

    # Temporary results response
    results = [
        {'_id': '63fba27d460689f9341ded89', 'title': 'Student Finance Guide - Stand Alone', 'url': 'https://www.standalone.org.uk/guides/student-guide/', 'links_outgoing': 42, 'references': 14, 'clicks': 1},
        {'_id': '63fba27d460689f9341ded93', 'title': '\n      Student finance: how to apply: Change an application - GOV.UK\n  ', 'url': 'https://www.gov.uk/apply-for-student-finance/change-an-application?step-by-step-nav=18045f76-ac04-41b7-b147-5687d8fbb64a', 'links_outgoing': 123, 'references': 11, 'clicks': 0},
        {'_id': '63fba273460689f9341dd892', 'title': 'Student Loans Company - GOV.UK', 'url': 'https://www.gov.uk/government/organisations/student-loans-company', 'links_outgoing': 157, 'references': 12, 'clicks': 0},
        {'_id': '63fba27d460689f9341ded95', 'title': '\n      Student finance if you suspend or leave your course: Overview - GOV.UK\n  ', 'url': 'https://www.gov.uk/student-finance-if-you-suspend-or-leave?step-by-step-nav=18045f76-ac04-41b7-b147-5687d8fbb64a', 'links_outgoing': 112, 'references': 4, 'clicks': 0},
        {'_id': '63fba27d460689f9341ded84', 'title': '\n      Student finance for undergraduates: EU students - GOV.UK\n  ', 'url': 'https://www.gov.uk/student-finance/eu-students?step-by-step-nav=18045f76-ac04-41b7-b147-5687d8fbb64a', 'links_outgoing': 129, 'references': 17, 'clicks': 1},
        {'_id': '63fba27d460689f9341ded7a', 'title': '\n      Student finance for undergraduates: Eligibility - GOV.UK\n  ', 'url': 'https://www.gov.uk/student-finance/who-qualifies?step-by-step-nav=18045f76-ac04-41b7-b147-5687d8fbb64a', 'links_outgoing': 130, 'references': 21, 'clicks': 0},
        {'_id': '63fba27d460689f9341ded92', 'title': 'Apply online for student finance - GOV.UK', 'url': 'https://www.gov.uk/apply-online-for-student-finance?step-by-step-nav=18045f76-ac04-41b7-b147-5687d8fbb64a', 'links_outgoing': 115, 'references': 6, 'clicks': 0},
        {'_id': '63fba2342a9f10c6071b9760', 'title': 'Student finance login - GOV.UK', 'url': 'https://www.gov.uk/student-finance-register-login', 'links_outgoing': 110, 'references': 3, 'clicks': 0},
        {'_id': '63fba27d460689f9341ded90', 'title': '\n      Student finance: how to apply: Proof of identity - GOV.UK\n  ', 'url': 'https://www.gov.uk/apply-for-student-finance/proof-of-identity?step-by-step-nav=18045f76-ac04-41b7-b147-5687d8fbb64a', 'links_outgoing': 117, 'references': 8, 'clicks': 0},
        {'_id': '63fba29e2b02d99564d3114a', 'title': 'Bill prioritiser: which debts or bills are most important? | MoneyHelper', 'url': 'https://www.moneyhelper.org.uk/en/money-troubles/cost-of-living/bill-prioritiser', 'links_outgoing': 422, 'references': 83, 'clicks': 0}]

    # Temporary qts response
    qts = [
        {'_id': '63fba2a743fe129994910517', 'name': 'student', 'df': 18, 'idf': 2.2921329545641838, 'stop_word_auto': False, 'stop_word_man': False, 'category': ''},
        {'_id': '63fba2a843fe1299949105d7', 'name': 'finance', 'df': 20, 'idf': 2.2776092143040914, 'stop_word_auto': False, 'stop_word_man': False, 'category': ''}]

    # return response to the client side
    return json.dumps([results, qts]), 200, {"Access-Control-Allow-Origin": "*"}


# Start the app when the code is executed
if __name__ == "__main__":
    app.run()
