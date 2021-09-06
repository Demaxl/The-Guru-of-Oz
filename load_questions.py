"""
This module will take care of the loading of the questions
that are in json format
"""
import json
import base64
import random

def loadEasy():
    with open('questions/easy.json', 'r+') as file:
        data = json.load(file)['results']
    
    easy = []
    for dic in data:
        q = base64.b64decode(dic['question']).decode()
        ans = base64.b64decode(dic['correct_answer']).decode()

        options = [ans]
        for o in dic['incorrect_answers']:
            options.append(base64.b64decode(o).decode())
        random.shuffle(options)
        
        easy.append({'question': q, 'answer': ans, 'options' : options})

    random.shuffle(easy)
    return easy

#----------------------------------------------------------------------------------------------------------------------------------------------
def loadMedium():
    with open('questions/medium.json', 'r+') as file:
        data = json.load(file)['results']

    medium = []
    for dic in data:
        q = base64.b64decode(dic['question']).decode()
        ans = base64.b64decode(dic['correct_answer']).decode()

        options = [ans]
        for o in dic['incorrect_answers']:
            # Please ignore this :D
            if base64.b64decode(o).decode() == 'Lying Is The Most Fun A Girl Can Have Without Taking Her Clothes Off':
                options.append('Lying is Fun for Girls')
            else:
                options.append(base64.b64decode(o).decode())
        random.shuffle(options)
        
        medium.append({'question': q, 'answer': ans, 'options' : options})

    random.shuffle(medium)
    return medium

def loadHard():
    with open('questions/hard.json', 'r+') as file:
        data = json.load(file)['results']
        
    hard = []
    for dic in data:
        q = base64.b64decode(dic['question']).decode()
        ans = base64.b64decode(dic['correct_answer']).decode()
        
        options = [ans]
        for o in dic['incorrect_answers']:
            options.append(base64.b64decode(o).decode())
        random.shuffle(options)
        
        hard.append({'question': q, 'answer': ans, 'options' : options})

    random.shuffle(hard)
    return hard
