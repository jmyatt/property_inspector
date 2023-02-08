## Looking ahead...
This POC offers an idea for satisying the septic check use case using jsonrpc to abstract the necessary call to an external service. Some considerations for next steps with this project:

* Extension of functionality
    * Add rpc methods to examine other subsets of the data returned by the HouseCanary, to answer questions relevant to other use cases
    * Add calls to other external property data services to aggregate, corroborate, and expand the sources we draw from
* Analytics
    * Emit tracking events to an analytics service to find correlations between certain property attributes and customer actions
* Security
    * This service is intended run local to our Virtual Private Cloud and not exposed to public traffic
    * Replace the implemented Basic Auth with a more secure and nimble pattern for microservices such as JWT and/or OAuth
    * Store API tokens for authenticated against 3rd party services such as HouseCanary in a secrets management service
* Availability
    * This is a stateless service so scaling horizontally via auto scaling groups should be straightforward.  However, as an extra layer of protection against a sudden flood of traffic, we should add rate limiting with exponential backoff to deny service in a transparent, communicative way.
    * If we find that the HouseCanary service (or others that we decide to add) has reliability issues, we might want to implement a local cache of data fetched. However, this might not be helpful depending on user traffic patterns, unless we see multiple requests for similar data over the course of a user session.
