
Tools:
regen_trajectories:
    A blunt tool to regenerate GPX trajectories if needed. For example, it doesn't filter out points in water.

sl_rtd.py (Real-Time Data):
    Collect data from SL:s API. Utilizing endpoints for real-time data. No API-KEY required.
    https://transport.integration.sl.se/v1/sites
    https://transport.integration.sl.se/v1/sites/{SiteId}/departures
    https://deviations.integration.sl.se/v1/messages?

user_trajectories.py: Process geospatial data from user. For example, from GPX file.

lbrp.py (Location-Based Route Planner):
    A simple route planner that uses the Haversine formula to calculate distances between points.
    It can be used to find the nearest stop to a given location. Utilize sl_rtd.py
    and user_trajectories.py to find the nearest stop to a given location.

user_patterns.py: 
    Analyze user patterns