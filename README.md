# Public Transportation Optimization Project

## Overview
Proof-of-Concept (PoC) to optimize routes based on user behavior. This is my degree project regarding Software Development Mobility Services.

## Background
I’m always in a rush, and I’m fast. So when using a route planner app, I have to make multiple searches and puzzle it together to "my route." Route planners tend to exclude some routes because the app assumes I wouldn’t make it, but I would. Therefore, I concluded that there’s room for optimization on the end-user side of public transportation. Since there are physical limitations such as infrastructure, optimizing/personalizing routes based on end-users' historical and location data (latitude, longitude, time, speed) can improve the user experience.

## Purpose
To achieve more streamlined public transportation, the end-user behavior must be considered. By making route planning more personalized and aiming to provide the smoothest route based on end-user geospatial data and patterns, we can build better behavior profiles.

## Tools

### regen_trajectories
A blunt tool to regenerate GPX trajectories if needed. For example, it doesn't filter out points in water.

### sl_rtd.py (Real-Time Data)
Collect data from SL's API. Utilizing endpoints for real-time data. No API-KEY required.
- SL Sites
- SL Site Departures
- SL Deviations

### user_trajectories.py
Processes geospatial data from users, such as data from GPX files.

### lbrp.py (Location-Based Route Planner)
A simple route planner that uses the Haversine formula to calculate distances between points. It finds the nearest stop to a given location and utilizes sl_rtd.py and user_trajectories.py to achieve this.

### user_patterns.py
Analyzes user patterns.

## Dependencies
- Python 3.12
- pandas
- geopandas
- folium
- streamlit
- streamlit-folium
- geopy
- shapely
- scikit-learn
- matplotlib
- python-dotenv
- requests
- gpxpy

## Installation

### Clone the Repository
```
git clone <repository-url>
cd <repository-directory>
```
Set Up Virtual Environment:
```
python -m venv env
source env/bin/activate
```
On Windows use `env\Scripts\activate`

#### Install dependencies
You can either install dependencies manually or use the setup.py file.
Using setup.py

In the root directory of your project, run:
```
pip install .
```

#### Install dependencies manually
If you prefer to install dependencies manually, run:
```
pip install pandas geopandas folium streamlit streamlit-folium geopy shapely scikit-learn matplotlib python-dotenv requests gpxpy
```
Usage
Run the Scripts to Generate Data
Run user_trajectories.py:
```
python -m gtfs.user_trajectories
```
Run lbrp.py:
```
python -m gtfs.lbrp
```
Run user_patterns.py:
```
python -m gtfs.user_patterns
```
Run the Streamlit Application

After generating the required data, you can run the Streamlit application to visualize the results. The data generation takes time because it runs a simulation of a 48-hour period. Simulation time is set to 20 minutes to provide real-time data in a realistic way.
```
streamlit run app.py
```
This will start a local server. Open the provided URL in your web browser to view the application.
Streamlit Tabs
User Trajectories

Displays user trajectory data and maps.
Real-Time Data

Shows sites and departures in real-time.
User Patterns

Visualizes user patterns and optimized routes.
Optimization Comparison

Compares original routes with optimized routes to show the impact of optimization.

