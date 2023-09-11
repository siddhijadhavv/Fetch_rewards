# Fetch_rewards
Data Engineering ETL process to extract data from Amazon SQS queue, transform data, and load to Postgres database

## Steps to run the code

#### Clone repository

#### Download the required dependencies
pip download -r requirements.txt

#### Run the file 
python3 fetch_rewards.py

## Check data in postgres

#### Connect to the database
psql -d postgres -U postgres -p 5432 -h localhost -W

#### Check if the data is present
postgres=# select * from user_logins;

# NOTE: Answers for the questions for this assignment have been added to the "answers to questions.txt"
