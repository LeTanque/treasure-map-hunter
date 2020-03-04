import json
import requests
import hashlib

headers = {'Authorization': 'Token <your token>',
           'Content-Type': 'application/json'}

while True:
    proof_response = requests.get('https://lambda-treasure-hunt.herokuapp.com/api/bc/last_proof/',
                                headers=headers
                                )
    proof_data = json.loads(proof_response.content)
    last_proof = proof_data['proof']
    difficulty = proof_data['difficulty']
    proof = 13333337

    while True:
        hash = hashlib.sha256((f'{last_proof}'+f'{proof}').encode()).hexdigest()
        if hash[:difficulty] == '000000':
            print(f'proof found {proof}')
            break
        else:
            proof += 1337

    data = {'proof': proof}
    response = requests.post('https://lambda-treasure-hunt.herokuapp.com/api/bc/mine/',
                             headers=headers,
                             data = json.dumps(data)
                             )
    print(response.content)