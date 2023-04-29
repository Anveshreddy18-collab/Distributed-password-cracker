import subprocess
no_of_workers = 7
worker_pids = [0] * (no_of_workers+1)

try:
    outfile = open('outfile.txt', '+a')
    for i in range(1, no_of_workers+1):
	    # worker_pids[i] = subprocess.Popen(['python3', 'worker.py', str(8000+i)])
        worker_pids[i] = subprocess.Popen(['python3', 'worker.py', str(8000+i)])
        print(worker_pids[i])
except Exception as e:
    print(e)
    print("Error in opening ports")
