import json
import requests
import hashlib
import os


# Globals
token = os.environ["SERVER_KEY"]
url = 'https://lambda-treasure-hunt.herokuapp.com/api/bc/'
headers = {'Authorization': f'Token {token}', 'Content-Type': 'application/json'}
hr = "---------------------------------"

while True:
    proof_response = requests.get(f"{url}last_proof/", headers=headers )
    bc_response = ""
    last_proof = ""
    try:
        bc_response = json.loads(proof_response.content)
    except:
        print(f"Waiting")
        break

    bc_response = json.loads(proof_response.content)
    try:
        last_proof = bc_response['proof']
    except:
        print(f"Missing last proof")
        break
    difficulty = bc_response['difficulty']
    proof = 101010101

    print(f"{hr} \n{proof_response}")
    print(f" proof: {bc_response['proof']}")
    print(f" difficulty: {bc_response['difficulty']}")
    print(f" cooldown: {bc_response['cooldown']}")
    print(f" messages: {bc_response['messages']}")
    print(f" errors: {bc_response['errors']}")

    while True:
        hash = hashlib.sha256((f'{last_proof}'+f'{proof}').encode()).hexdigest()
        if hash[:difficulty] == "0" * difficulty:
            print(f'proof found {proof}')
            break
        else:
            proof += 333

    data = {'proof': proof}
    print(f"This is being sent to mine {data}")
    response = requests.post(f"{url}mine/", headers=headers, data = json.dumps(data) )
    print(response.content)
