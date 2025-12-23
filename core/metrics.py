history = []

def add_metric(latency, valid):
    history.append({"latency": latency, "valid": valid})

def get_stats():
    if not history:
        return 0, 0
    avg_latency = sum(h["latency"] for h in history) / len(history)
    compliance = sum(1 for h in history if h["valid"]) / len(history) * 100
    return avg_latency, compliance
