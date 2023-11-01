all: workload0 workload1 workload2 workload3

workload0:
	$(info WORKLOAD 0)
	python3 main.py ./workload/workload0.json

workload1:
	$(info WORKLOAD 1)
	python3 main.py ./workload/workload1.json

workload2:
	$(info WORKLOAD 2)
	python3 main.py ./workload/workload2.json

workload3:
	$(info WORKLOAD 3)
	python3 main.py ./workload/workload3.json