# 10_SQLAlchemy_Challenge
Overview
This repository contains a two correlating python files ('Climate Analysis.ipynb' and 'app.py'), a "Resources" folder for the corresponding csv's for importing into and a .sqlite resources file ('Hawaii.sqlite'). The directions for the module were to use SQL file to pull data into a climate analysis and then also create an API with the data for easy searchability.

## Results
In the 10_SQLAlchemy_Challenge, this dataset is an aggregate of two sources into a SQLlite file. A analysis was created to run individiual queries in the data and then plot several graphs against the data. In the API section, a rudimentary API was created to reverse query the data in the SQL file. Several routes were created to look at different queries in the API. Most notably, a search function was added to be able to search specific dates in the API and return temperature data and observations for that day and forward. Similarly, a second search was added so that you can specify a start and end date to your search so that you can narrow your results in the API.


## Usage
Climate Analysis 

1. Open the respective file ('Climate Analysis.ipynb') in VSCode or Jupyter Notebook.

2. Be sure the resources folder is correctly correlated and run the cells to see the individual analysis.

API App 

1. Open the respective file ('app.py') in VSCode or Jupyter Notebook.

2. Be sure the resources folder is correctly correlated and run the cells to see the individual analysis.

3. Run the code in the terminal. You will receive an http environment in the terminal. (* Running on http://127.0.0.1:5000)
   
4. Enter the application route in a browser.

5. Navigate through the browser and view/query results.


## Resources and Citations

Study Group - Quentin O'Neal

Office Hours - Kristina D'Alessio

A LOT of General query - ChatGpt.com
