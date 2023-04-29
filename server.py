from flask import Flask, request, jsonify
import requests
import math
import subprocess
import time


app = Flask(__name__)

# Initialize a dictionary to store job and task information 
# jobs = {}
# worker_responses = []
# for each worker, we need to maintain a dictionary of {worker_id, start_char, no_of_chars[i], password_length, hash}
worker_info = {}

final_ans = ''

import json

def send_post_request(client_url):
    try:
        response = requests.post(client_url, timeout=1)
        return response
    except Exception as e:
        print("SEND POST Exception: ", e)
        return None

def check_client_status(client_url):
    response = send_post_request(client_url)
    if response is not None:
        return [True, response]
    else:
        return [False, None]

@app.route('/crack_password', methods=['GET', 'POST'])
def crack_password():
    if request.method == 'GET':
        return 'hi'
    # convert request.data ad print
    password = request.json['password']
    hash = request.json['hash']
    
    total_chars = 26 # curently considering only lowercase alphabets
    no_of_workers = 7
    password_length = len(password)

    # how many chars each worker will have to do, the array is indexed from 1 to no_of_workers
    no_of_chars = [0] * (no_of_workers+1)

    if total_chars%no_of_workers == 0:
        for i in range(1, no_of_workers+1):
            no_of_chars[i] = total_chars/no_of_workers

    else:
        for i in range(1, no_of_workers+1):
            no_of_chars[i] = math.floor(total_chars/no_of_workers)

        for i in range(1, (total_chars%no_of_workers)+1):
            no_of_chars[i] += 1



    counter = 0 # to keep track of the start_char for each worker
    for i in range(1, no_of_workers+1):

        # calculate the cur_string which is the string that the worker will start with
        s = ''
        s += chr(counter + 97)
        for j in range(1, password_length):
            s += 'a'

        global worker_info    
        worker_info[i] = {'worker_id': i, 
                        'start_char': counter, 
                        'no_of_chars': no_of_chars[i], 
                        'password_length': password_length, 
                        'hash': hash,
                        'cur_string': s}
        
        counter += no_of_chars[i]

    # -------------------------------------------------------------------
    # Now send a POST request to each worker with the worker_info dictionary as the data and store the response in a dictionary with worker_id as the key and response as the value  


    active_ports_list = []
    for i in range(1, no_of_workers+1):
        active_ports_list.append(8000+i)

    original_ports_list = active_ports_list.copy()

    active_jobs_list = {}
    for i in range(1, no_of_workers+1):
        active_jobs_list[i] = {
                                'job_id': i,
                                'start_char': worker_info[i]['start_char'],
                                'no_of_chars': worker_info[i]['no_of_chars'],
                                'cur_string': worker_info[i]['cur_string'],
                                'password_length': worker_info[i]['password_length'],
                                'hash': worker_info[i]['hash'],
                                'is_done': False
                              }
        
    # while active_jobs_list is not empty
    while len(active_jobs_list) != 0:
        
        # sort the active_jobs based on the number of remaining possible passwords to crack
        
        # Open ports and run worker.py in them
        worker_pids = [0] * (no_of_workers+1)
        try:
            outfile = open('outfile.txt', '+a')
            for i in range(1, no_of_workers+1):
                worker_pids[i] = subprocess.Popen(['python3', 'worker.py', str(8000+i)])
                print(worker_pids[i])
        except Exception as e:
            print(e)
            print("Error in opening ports")
        # try:
        #     for i in range(1, no_of_workers+1):
        #         outfile = open('outfile.txt', '+a')
        #         worker_pids[i] = subprocess.Popen(['python3', 'worker.py', str(8000+i)], stdout=outfile, stderr=outfile)
        #         print(worker_pids[i].pid)
                
        #         print("Worker", i, "started")
        #     print(worker_pids)
        # except Exception as e:
        #     print(e)
        #     print("Error in opening ports")

        time.sleep(5)
        size = min(len(active_jobs_list), len(active_ports_list))
        keys_list = sorted(active_jobs_list.keys())
        i = 0
        # print("i am here")
        for key in keys_list:
            try:
                url = 'http://localhost:' + str(active_ports_list[i]) + '/dataPost'
                print("URL", url)
                data = active_jobs_list[key]
                # print("Assigning job to worker:", data)
                response = requests.post(url, json=data)
                i += 1
                if i == size:
                    break

            except Exception as e:
                print("ERR:", e)
                print(active_jobs_list)
                print(active_ports_list)
            


        new_active_jobs_list = {}
        new_active_ports_list = []

        for j in range(1,5):

            new_active_ports_list = []

            i = 0
            for key in keys_list:
                url = 'http://localhost:' + str(active_ports_list[i]) + '/receiveUpdate'
                status = check_client_status(url)
                print("STATUS:", status)
                if status[0]:
                    # The client is active
                    new_active_ports_list.append(active_ports_list[i])

                    # status[1] has response in the format of make_response(response_data, 200)
                    response_data = status[1]

                    # print information in response
                    print("Response = ", response_data.content)                    

                    response_data = json.loads(response_data.content)
                    start_char = response_data['start_char']

                    #  status[1] is a dictionary that contains 'start_char', 'no_of_chars', 'cur_string', 'password_length', 'hash', 'password'
                    if response_data['password'] == "None":
                        active_jobs_list[key]['cur_string'] = response_data['latest_string']
                    else:
                        if response_data['password'] == "No password found":
                            active_jobs_list[key]['cur_string'] = response_data['latest_string']
                            active_jobs_list[key]['is_done'] = True

                        else:
                            global final_ans
                            final_ans = response_data['password']
                            active_jobs_list[key]['is_done'] = True
                            return final_ans
                        
                i += 1
                if i == size:
                    break

            # sleep for 5 seconds
            time.sleep(3)
            
        print('setting new active ports list', new_active_ports_list)
        active_ports_list = new_active_ports_list
        # Now go through all the jobs of active_jobs_list and check if any of them is done, if not, then add it to the new_active_jobs_list
        keys_list = sorted(active_jobs_list.keys())
        for key in keys_list:
            if active_jobs_list[key]['is_done'] == False:
                new_active_jobs_list[key] = active_jobs_list[key]

        print('setting new active jobs list', new_active_jobs_list)
        active_jobs_list = new_active_jobs_list

        # Kill all the workers running on worker.py using their pids
        try:
            for i in range(1, no_of_workers+1):
                worker_pids[i].kill()
        except Exception as e:
            print("FAILED TO KILL workers", e)
        
    return 'No worker could crack the password'

    

if __name__ == '__main__':

    app.run(host='0.0.0.0', port=5000)
