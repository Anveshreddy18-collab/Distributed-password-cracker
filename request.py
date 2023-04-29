import requests

def crack_password(password, hash):
    # Send a POST request to the server to initiate the password cracking job
    url = 'http://localhost:5000/crack_password'
    data = {'password': password, 'hash': hash}
    print('data', data)
    response = requests.post(url, json=data)

    # Return the cracked password or a failure message
    if response.ok:
        print("Received:", response.text)
        # if response.text is equal to password, then the password was cracked
        s1 = str(response.text)
        # remove last char from s1
        return response.text
        if s1 == password:
            return response.text
        else:
            return 'Attempted to crack but failed'
    else:
        return 'Failed due to server error'


if __name__ == '__main__':
    
    # read the password from the password.txt file
    password = open('password.txt', 'r').read()
    # read the hash of it from the hash.txt file
    hash = open('hash.txt', 'r').read()

    # Crack the password
    cracked_password = crack_password(password, hash)
    print(cracked_password)
