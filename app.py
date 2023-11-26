from flask import Flask, jsonify, copy_current_request_context
import requests
import aiohttp
import asyncio
import random

app = Flask(__name__)

@app.route('/sync-random-selection')
def sync_random_selection():
    postings_response = requests.get('http://3.135.197.136:5000/jobs')
    app.logger.info("Received response from postings service")
    postings_json  = postings_response.json()
    
    if 'data' in postings_json and isinstance(postings_json['data'], list):
        selected_posting = random.choice(postings_json['data'])
    else:
        app.logger.error("Invalid format or empty list in postings response")
        return "Error: Invalid postings data format", 500
    
    users_response = requests.get('http://18.219.228.128:5001/users/1')
    app.logger.info("Received response from users service")
    user = users_response.json()

    applications_response = requests.get('https://coms6156-yw4174.uk.r.appspot.com/application/1')
    app.logger.info("Received response from applications service")
    application = applications_response.json()

    return jsonify({
        'selected_posting': selected_posting,
        'user': user,
        'application': application
    })

async def fetch_and_log(url, session, service_name):
    async with session.get(url) as response:
        app.logger.info(f"Received response from {service_name} service")
        data = await response.json()
        return service_name, data

@app.route('/async-random-selection')
def async_random_selection():
    app.logger.info("Starting asynchronous calls")

    async def get_random_selection():
        async with aiohttp.ClientSession() as session:
            tasks = [
                fetch_and_log('http://3.135.197.136:5000/jobs', session, "postings"),
                fetch_and_log('http://18.219.228.128:5001/users/1', session, "users"),
                fetch_and_log('https://coms6156-yw4174.uk.r.appspot.com/application/1', session, "applications")
            ]
            results = await asyncio.gather(*tasks)
            return {key: val for key, val in results}

    new_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(new_loop)
    try:
        result = new_loop.run_until_complete(get_random_selection())
    finally:
        new_loop.close()

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)