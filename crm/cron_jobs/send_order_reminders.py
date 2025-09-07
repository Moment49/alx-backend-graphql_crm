import sys
import os
from datetime import datetime, timedelta
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# GraphQL endpoint
GRAPHQL_ENDPOINT = "http://localhost:8000/graphql"

# Set date range (last 7 days)
today = datetime.utcnow()
seven_days_ago = today - timedelta(days=7)

# Define GraphQL query
query = gql(
    """
    query GetRecentOrders($startDate: DateTime!) {
      orders(orderDate_Gte: $startDate, status: "PENDING") {
        id
        customer {
          email
        }
      }
    }
    """
)

def main():
    try:
        # Configure transport
        transport = RequestsHTTPTransport(
            url=GRAPHQL_ENDPOINT,
            verify=True,
            retries=3,
        )
        client = Client(transport=transport, fetch_schema_from_transport=True)

        # Execute query
        variables = {"startDate": seven_days_ago.isoformat()}
        response = client.execute(query, variable_values=variables)

        orders = response.get("orders", [])
        log_file = "/tmp/order_reminders_log.txt"

        with open(log_file, "a") as f:
            for order in orders:
                log_entry = f"{datetime.utcnow().isoformat()} - Order ID: {order['id']}, Customer Email: {order['customer']['email']}\n"
                f.write(log_entry)

        print("Order reminders processed!")

    except Exception as e:
        print(f"Error processing reminders: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
