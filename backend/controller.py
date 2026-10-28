# ==========================================
# VOLTVISION - SMART GRID CONTROLLER
# ==========================================


def determine_grid_mode(demand_kw, timestamp):
    """
    Determine which power source should be used
    based on predicted electricity demand and time.

    Rules:
    1. Demand > 160 kW → Renewable Storage
    2. Time 18:00–22:00 → Renewable Storage
    3. Otherwise → Main Grid
    """

    hour = int(timestamp.split(":")[0])

    if demand_kw > 160 or 18 <= hour <= 22:
        return "Renewable Storage"

    return "Main Grid"


def check_overload(demand_kw):
    """
    Check whether predicted demand reaches
    the critical overload threshold.

    Threshold: 200 kW
    """

    return demand_kw >= 200


def make_grid_decision(timestamp, demand_kw):
    """
    Generate the complete smart-grid decision
    for one forecasted hour.
    """

    grid_mode = determine_grid_mode(
        demand_kw,
        timestamp
    )

    overload_alert = check_overload(
        demand_kw
    )

    return {
        "timestamp": timestamp,
        "target_demand_kw": demand_kw,
        "grid_mode": grid_mode,
        "overload_alert": overload_alert
    }


# ------------------------------------------
# TEST THE CONTROLLER
# ------------------------------------------

if __name__ == "__main__":

    test_data = [
        ("10:00", 130),
        ("10:00", 160),
        ("10:00", 170),
        ("19:00", 150),
        ("14:00", 200),
        ("20:00", 220)
    ]

    for timestamp, demand in test_data:

        decision = make_grid_decision(
            timestamp,
            demand
        )

        print(decision)