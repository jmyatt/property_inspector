## Description
__PropertyInspector__ is a simple web service that aggregates U.S. property data from various sources to provide useful insights to our main web application. This can be used in support of common use cases as customers and prospective customer explore our products and services.

An example usage for determining whether a given property contains a septic system is [diagrammed here](https://github.com/jmyatt/property_inspector/blob/main/property_inspector/docs/sequence.png).



### The Path to Production
See [this document](https://github.com/jmyatt/property_inspector/blob/main/property_inspector/docs/next_steps.md) for considerations on next steps to be taken if we want to productionalize this service.


## Installation

1. Clone the repo:
    ```
    git clone git@github.com:jmyatt/property_inspector.git
    ```
1. Change to the project directory, configure a virtual env and activate it
    ```
	cd property_inspector
    python3 -m venv jasonmyatt_venv
	source jasonmyatt_venv/bin/activate
    ```
1. Install required packages and run migrations
    ```
	pip3 install -r requirements.txt
	./manage.py migrate
    ```
1. Run tests
    ```
	./manage.py test property_inspector_api.tests
    ```
1. Create a super user which we'll use to query the service
    ```
	./manage.py createsuperuser
	```
1. Run the development server on port 8000
    ```
	./manage.py runserver
	```
1. From a separate shell, send a CURL command to the jsonrpc endpoint using the username and password you created
    ```
	curl -X POST localhost:8000/rpc/ -H "Content-Type: application/json" -d '{"jsonrpc": "2.0", "id": 1, "method": "check_has_septic", "params": ["123 main st", "94132"]}' -u "USERNAME:PASSWORD"
    ```
1. If everything's working correctly, the response should show that the specified property contains a septic system 
    ```
    {"id": 1, "jsonrpc": "2.0", "result": "septic"}
    ```

