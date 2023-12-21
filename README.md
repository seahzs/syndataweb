# syndataweb
This project is a web app for generating synthetic data using ```single table``` and ```multi table``` models from [SDV](https://docs.sdv.dev/sdv/), including [IRGAN](https://github.com/lll-jy/irgv2) developed by Li Jiayu. 

## Local deployment
- Install all dependencies stated in requirements.txt using ```pip install -r requirements.txt``` 
- Run ```streamlit run Home.py``` to start the local web server.
- Launch web browser and go to [localhost:8501](http://localhost:8501) or [127.0.0.1:8501](http://127.0.0.1:8501)
- It is recommended to have a system with at least 16GB of memory.
- The configuration and uploaded data of each session will be reset when the page is reloaded. 
> **Warning: Some data may remain in the local folder ```./irgan``` when the IRGAN model is used for data generation.**

## Online demo
- Go to https://syndataweb.streamlit.app/
- This app is hosted on a third-party server for demonstration purposes only. 
> **Warning: Do not upload any confidential or sensitive data!**
- The online demo may crash if the data is too big or if processing takes too long causing a time-out.
- Click on the menu at the bottom-right to restart the app if there are issues.

## Usage Instructions
https://github.com/seahzs/syndataweb/assets/22360274/1a9662b5-fe03-4400-9bbb-6f794adf8e2a

### To begin: Uploading Real Data
- At the homepage, upload CSV files each containing one table. 
- It would be best to prepare pre-processed CSV files with table headers and records with missing fields pre-filled or removed.

### Step 1: Preparing the Data
- On the sidebar, go to ```(1) Prepare Data```. You will see 7 tasks available. 
- Each task is optional depending on what needs to be done, but must be performed in the order shown to avoid errors.
#### Step 1a: Set datatypes
- Most datatypes should be auto-detected except for ```datetime``` and ```id```. 
- It is important to identify these for the synthetic data to be generated correctly later. 
- Set ```datetime``` format as ```default```. If data is not generated correctly or errors encountered, select the other ```datetime``` formats and retry (your data must match the other format). 
- Columns that are to be used for primary key or foreign key later should be set as ```id```.
#### Step 1b: Set/remove primary key
- Set the primary key of each table if necessary. This will mainly be used for inter-table relationships.
- No options will be available if the table does not have a column set as ```id``` datatype.
#### Step 1c: Drop columns
- This is for last minute removal of unnecessary columns. Tables should be well-prepared before it is uploaded.
#### Step 1d: Group tables
- Select 2 or more tables to be grouped. These tables will be used for multi table generation.
#### Step 1e: Add/remove inter-table relationship
- Inter-table relationships are necessary for multi table generation to produce desirable results.
- To add inter-table relationship, tables must be grouped and primary key of the parent key and foreign key of the child table must be set as ```id``` datatype.

### Step 2: Model fitting
- On the sidebar, go to ```(2) Model Fitting```. Select the task (single table/multi table) and the model to fit. 
- For multi table generation, tables must be grouped first.
- Not all models allow for setting the epoch (training cycles). If available, try setting ```1``` epoch first. 
- The higher the epoch (training cycles) the better the results, but takes longer time. 
- Fitting may take a few minutes to more than an hour, depending on the model chosen and the system performance. 
- If running on a local machine, check the streamlit terminal for the actual progress and any errors encountered.

### Step 3: 
- On the sidebar, go to ```(3) Generate Data```. Select the task (single table/multi table) and the model to generate. 
- Data must be fitted to a model before generating data. 
- Not all models allow for setting number of records to be generated. If not available, the number of records generated will be same as the original data.

### Step 4:
- On the sidebar, go to ```(4) Visualisation```. This page generates basic visualisations and is completely optional. 
- Select a visualisation (distribution/correlation) and table column(s) to make a comparison between original data and generated data.

### Step 5:
- On the sidebar, go to ```(5) Export Synthetic Data```. Select the type (single table/multi table) and the table(s) to be downloaded as CSV file.
