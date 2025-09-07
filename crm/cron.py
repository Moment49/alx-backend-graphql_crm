from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

def log_crm_heartbeat():
    """Logs heartbeat message and queries GraphQL hello field to verify health."""
    log_file = "/tmp/crm_heartbeat_log.txt"
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")

    # Log heartbeat
    with open(log_file, "a") as f:
        f.write(f"{timestamp} CRM is alive\n")

    # GraphQL hello query
    try:
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            verify=True,
            retries=3,
        )
        client = Client(transport=transport, fetch_schema_from_transport=True)

        query = gql(
            """
            query {
              hello
            }
            """
        )
        response = client.execute(query)

        hello_value = response.get("hello", "No response")
        with open(log_file, "a") as f:
            f.write(f"{timestamp} GraphQL hello response: {hello_value}\n")

    except Exception as e:
        with open(log_file, "a") as f:
            f.write(f"{timestamp} GraphQL check error: {e}\n")
