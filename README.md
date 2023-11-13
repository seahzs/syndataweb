# syndataweb
This project is a web app for generating synthetic data using single table and multi table models from SDV, including [IRGAN](https://github.com/lll-jy/irgv2) developed by Li Jiayu. 

## Local deployment
- Install all dependencies stated in requirements.txt using ```pip install -r requirements.txt``` 
- Run ```streamlit run Home.py``` to start local web server 
- Launch web browser and go to [localhost:8501](http://localhost:8501) or [127.0.0.1:8501](http://127.0.0.1:8501)

## Online demo
- Go to https://syndataweb.streamlit.app/
- Note that this app is hosted on a third-party server for demonstration purposes only. 
> **Warning: Do not upload any confidential or sensitive data!**

## Usage Instructions
### Step 1: Uploading Real Data
- At the homepage, upload CSV files each containing one table. 
- It would be best to prepare pre-processed CSV files with table headers and records with missing fields pre-filled or removed.

### Step 2: Preparing the Data
- On the sidebar, go to '(1) Prepare Data'. 
- You will see 7 tasks available. Each task is optional depending on what needs to be done, but tasks must be performed in the order shown.
#### Step 2a: Set datatypes
- Most datatypes should be auto-detected except for 'datetime' and 'id'. 
- It is important to identify these for the synthetic data to be generated correctly later. 
- Set datetime format as 'default'. If data is not generated correctly or errors encountered, select the other datetime formats and retry (your data must match the other format). 
- Columns that are to be used for primary key or foreign key later should be set as 'id'.
#### Step 2b: Set/remove primary key
- Set the primary key of each table if necessary. This will mainly be used for inter-table relationships.
- No options will be available if the table does not have a column set as 'id' datatype.
#### Step 2c: Drop columns
- This is for last minute removal of unnecessary columns. Tables should be well-prepared before it is uploaded in Step 1.
#### Step 2d: Group tables
- Select 2 or more tables to be grouped. These tables will be used for multi table generation.
### Step 2e: Add/remove inter-table relationship
