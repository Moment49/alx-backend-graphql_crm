from datetime import datetime

def log_crm_heartbeat():
    """Logs heartbeat message and optionally queries GraphQL hello field."""
    log_file = "/tmp/crm_heartbeat_log.txt"
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")

    # Log heartbeat
    with open(log_file, "a") as f:
        f.write(f"{timestamp} CRM is alive\n")

    # (Optional) GraphQL check
    try:
        import requests
        query = {"query": "{ hello }"}
        response = requests.post("http://localhost:8000/graphql", json=query)
        if response.status_code == 200:
            with open(log_file, "a") as f:
                f.write(f"{timestamp} GraphQL hello OK\n")
        else:
            with open(log_file, "a") as f:
                f.write(f"{timestamp} GraphQL hello FAILED\n")
    except Exception as e:
        with open(log_file, "a") as f:
            f.write(f"{timestamp} GraphQL check error: {e}\n")
