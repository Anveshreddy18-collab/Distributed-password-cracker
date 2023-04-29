import subprocess
import sys
import json
from flask import Flask, request, jsonify, make_response
import threading
import time
import crypt


app = Flask(__name__)

start_char = 0
no_of_chars = 0
password_length = 0
hash = ''
start_string = ''
job_id = 0
password = "None"

latest_string = ''

flag = False
fiveSecondsFlag = False

@app.route('/dataPost', methods=['GET','POST'])
def dataPost():
    if request.method == 'GET':
        return 'hi'
    worker_info = request.json
    print("GOT JOB INFO: ", worker_info)
    global start_char
    start_char = worker_info['start_char']
    global no_of_chars
    no_of_chars = worker_info['no_of_chars']
    global password_length
    password_length = worker_info['password_length']
    global hash
    hash = worker_info['hash']
    global start_string
    start_string = worker_info['cur_string']
    global job_id
    job_id = worker_info['job_id']
    global flag
    flag = True

    response_data = {'hi': 'hello'}
    # response = make_response(response_data, 200)
    return response_data

def runlogic(start_char1, no_of_chars1, password_length1, hash1, index, cur):

    n = password_length1
    m = no_of_chars1

    if index == n:
        global latest_string

        latest_string = cur

        salt = "aa"
        if hash == crypt.crypt(cur, salt):
            global password
            password = cur

            return password
        else:
            return ""
        
    for i in range(m):
        c = chr( ord('a') + i+start_char1)
        cur += c
        runlogic(0, 26, password_length1, hash1, index+1, cur)
        cur = cur[:-1]

    return ""
    
def runthisfirst(password_length1, hash1, start_string, end_char):

    n = len(start_string)
    temp = start_string
    for i in range(len(start_string)):
        index = n-i-1
        
        val1 = ord(start_string[index]) - ord('a') + 1
        val2 = ord('z') - ord(start_string[index])
        if index == 0:
            val2 = ord(end_char) - ord(start_string[index])
        
        temp = temp[:-1] 
        
        runlogic(val1, val2, password_length1, hash1, index, temp)
        

def crack_password(): 
    
    # print(request.json)
    while True:
        global flag
        while flag == False:
            continue

        flag = False

        # run the actual code here
        cur = ''
        # runlogic(start_char, no_of_chars, password_length, hash, 0, cur)
        end_char = chr(ord('a') + start_char + no_of_chars - 1)
        runthisfirst(password_length, hash, start_string, end_char)
        global password
        if password == "None":
            password = "No password found"
    
        return

    


@app.route('/receiveUpdate', methods=['GET', 'POST'])
def receiveUpdate():
    if request.method == 'GET':
        return 'hi'
    while True:
        # data = request.json
        response_data = { 'job_id': job_id ,'start_char': start_char, 'no_of_chars': no_of_chars, 'password_length': password_length, 'hash': hash, 'latest_string': latest_string, 'password': password}
        return response_data



# create server with input argument as port number
if __name__ == '__main__':

    port = int(sys.argv[1])

    # thread_dataPost = threading.Thread(target=dataPost)
    thread_crack_password = threading.Thread(target=crack_password)
    # thread_receiveUpdate = threading.Thread(target = receiveUpdate)

    # thread_dataPost.start()
    thread_crack_password.start()
    # thread_receiveUpdate.start()
    

    # get port number from command line argument
    app.run(host='0.0.0.0', port=port)