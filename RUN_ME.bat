@echo off

echo Create virtual environment
python -m venv .\venv

echo Install depedencies
.\venv\Scripts\python -m pip install -r requirements.txt

echo Run the code

echo There are four workloads to be run 
echo You can check the config in under workload/ folder
echo Each workload might take a few minutes
echo Run workload0
.\venv\Scripts\python main.py ./workload/workload0.json
echo Run workload1
.\venv\Scripts\python main.py ./workload/workload1.json
echo Run workload2
.\venv\Scripts\python main.py ./workload/workload2.json
echo Run workload3
.\venv\Scripts\python main.py ./workload/workload3.json

echo Deactivate environment
deactivate