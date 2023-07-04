'''
Christian Williams
Thesis
17 September 2022
This program takes the parsed q file and creates an oracle for the training and testing data.
'''


from os import getcwd
from json import load, dump, loads, dumps
from datetime import datetime
from random import randint, seed, shuffle


INPUT_PATH = getcwd() + '\\input\\state-records-v2_2.json'
TEST_OUTPUT_PATH = getcwd() + '\\output\\oracle-test.json'
TRAIN_OUTPUT_PATH = getcwd() + '\\output\\oracle-train.json'

VALID_OUTPUT_PATH = getcwd() + '\\output\\oracle-valid.json'


OUTPUT_PATH = getcwd() + '\\output\\oracle-v1.json'





# Returns the input sentence for the oracle
def get_input_sentence(obj):
    output = ''
    keys = list(obj)
    shuffle(keys)
    for key in keys:
        if output != '':
            output += ' '
        if key == 'position':
            output += f"{key} {' '.join(str(elem) for elem in obj[key])}"
        else:
            output += f'{key} {str(obj[key])}'

    return output






def get_direction(heading):
    if heading >= 337 or heading < 22:
        return "east"
    elif heading >= 22 and heading < 67:
        return 'northeast'
    elif heading >= 67 and heading < 112:
        return 'north'
    elif heading >= 112 and heading < 157:
        return 'northwest'
    elif heading >= 157 and heading < 202:
        return 'west'
    elif heading >= 202 and heading < 247:
        return 'southwest'
    elif heading >= 247 and heading < 292:
        return 'south'
    elif heading >= 292 and heading < 337:
        return 'southeast'



        
    


# temporary work around input file format
def get_action_obj(action):
    action_obj = {}
    action_obj['throttle'] = action[0]
    action_obj['steer'] = action[1]
    action_obj['jump'] = action[5]
    action_obj['boost'] = action[6]
    action_obj['handbrake'] = action[7]
    return action_obj




def get_position_sentence(x,y):
    pos = []
    if x >= 0 and y >= 0:
        pos.append('in quadrant 1')
    if x < 0 and y >= 0:
        pos.append('in quadrant 2')
    if x < 0 and y < 0:
        pos.append('in quadrant 3')    
    if x >= 0 and y < 0:
        pos.append('in quadrant 4')
    if x <= 1000 and x >= -1000 and y <= 1000 and y >= -1000:
        pos.append('near the center')
    if x <= 1000 and x >= -1000 and y <= -3120:
        pos.append('near the blue goal')
    if x <= 1000 and x >= -1000 and y >= 3120:
        pos.append('near the orange goal')
    if x <= -3096:
        pos.append('near the east wall')
    if x >= 3096:
        pos.append('near the west wall')
    if y <= -4120:
        pos.append('near the south wall')
    if y >= 4120:
        pos.append('near the north wall')
    sentence = f"I'm {pos[0]} {' and '.join(pos[1:])}".strip() +'.'
    return sentence






def get_interval():
    mid = randint(2, 99)
    low = randint(1, mid-1)
    high = randint((mid+1), 100)
    return low, mid, high




def get_index():
    low, mid, high = get_interval()
    rand_num = randint(1, 100)
    if rand_num <= low:
        return 0
    elif rand_num > low and rand_num <= mid:
        return 1
    elif rand_num > mid and rand_num <= high:
        return 2
    elif rand_num > high:
        return 3



def get_action(key, value):
    if key == 'steer':
        if value == -1:
            return 'left'
        else:
            return 'right'
    if key == 'throttle':
        if value == 1:
            return 'forwards'
        else:
            return 'backwards'



def replace_placeholder(text, value):
    return text.replace("*r", str(value))



# Accepts the measures and action as an input
# returns the target sentence
def get_target_sentence(obj, action):
    pos = obj['position']
    sentence = ''
    template = get_sentences_template()


    # select sentences from the template and replace the attributes as necessary
    if obj['is_demoed']:
        index = get_index()
        return template['is_demoed'][index]
    
    num_sentences = 7
    nums = [i for i in range(num_sentences)]
    shuffle(nums)

    for num in nums:


        match num:

            case 0:
                if obj['boost_amount'] > 0:
                    index = get_index()
                    text = template['boost_amount'][index]
                    value = obj['boost_amount']
                    sentence += f" {replace_placeholder(text, value)}"

            case 1:
    
                if obj['on_ground']:
                    index = get_index()
                    sentence += f" {template['on_ground'][index]}"

            case 2:
                index = get_index()
                text = template["speed"]["index"]
                value = obj['speed']
                sentence += f" {replace_placeholder(text, value)}"

            case 3:
                index = get_index()
                text = template['direction'][index]
                value = get_direction(obj['direction'])
                sentence += f" {replace_placeholder(text, value)}"

            case 4:
                index = get_index()
                sentence += f" {get_position_sentence(pos[0], pos[1])}"

            case 5:
                if action['handbrake']:
                    index = get_index()
                    sentence += f" {template['action']['handbrake'][index]}"
                else:
                    index1 = get_index()
                    text1 = template['action']['steer'][index1]
                    value1 = get_action('steer', action['steer'])

                    index2 = get_index()
                    text2 = template['action']['throttle'][index2]
                    value2 = get_action('throttle', action['throttle'])

                    temp1 = f" {replace_placeholder(text1, value1)}".replace('.', '')
                    temp2 = f"{replace_placeholder(text2, value2)}"
                    sentence += f" {' and '.join([temp1, temp2])}"

            case 6:
                if action['boost']:
                    index = get_index()
                    sentence += f" {template['action']['boost'][index]}"


    return sentence.strip()




# returns the sentences template
def get_sentences_template():
    template = {
        'is_demoed': [
            'My car has been demolished.', 
            'My car has exploded!',
            'I crashed my car!', 
            'I wrecked my car.'
            ],
        'boost_amount': [
            'My current boost is *r.', 
            'I currenly have *r percent boost.', 
            'I have *r boost.', 
            'My boost is *r percent.'
            ],
        'on_ground': [
            'My car is on the ground.', 
            "I'm on the ground.", 
            "I'm not in the air.",
            "I'm currently driving on the ground."
            ],
        'ball_touched': [
            'I have the ball!', 
            "I've got the ball!",
            "I currently have the ball.",
            "The ball is in my possession."
            ],
        'speed': [
            'My current speed is *r.', 
            "I'm travelling *r miles per hour.", 
            'My current speed is *r mph.', 
            'My current speed is *r miles per hour.'
            ],
        'direction': [
            "I'm currently travelling *r.",
            "I'm heading in the *r direction.",
            'My current direction is *r.',
            "I'm heading *r."
            ],
        'position': [],
        'action': {
            'handbrake': [
                "I'm currently braking.",
                "I pressed the brakes.", 
                "I'm stopping",
                "I stopped."
                ],
            'steer': [
                "I'm steering *r.",
                "I'm turning *r.",
                'I turned *r.',
                 "I'm about to turn *r."
                 ],
            'throttle': [
                "I'm driving *r.",
                "I'm going *r.",
                "I'm moving *r.",
                "I'm travelling *r."
                ],
            'boost': [
                "I've used boost.",
                "I'm using boost.",
                "I've used the speed up.",
                "I have boosted."
                ]
        },
        "relation": {
            "is_demoed": [

            ],

        }

        
    }
    return template







def get_relation_sentence(data, action):
    print(f'Data: {data}\nAction: {action}')


def remove_duplicates(dataset):
    set_of_jsons = set([dumps(d, sort_keys=True) for d in dataset])
    return [loads(t) for t in set_of_jsons]


# returns the oracle from the data set
def get_oracle(dataset):
    num_iter = 64
    oracle = {}
    data_list = []
    oracle['all_data'] = []
    oracle['data'] = {}
    for i in range(num_iter):
        for data in dataset:
            obj = {}
            action = get_action_obj(data['action'])
            data = data['state']['measurements']
            # obj['input'] = f"{get_input_sentence(data)} {' '.join(f'{key} {action[key]}' for key in action.keys())}".replace('  ', ' ')

            obj['relation'] = get_relation_sentence(data, action)



    #         obj['target'] = get_target_sentence(data, action).replace('  ', ' ')
    #         data_list.append(obj)
    # print(len(data_list))
    # oracle['all_data'] = remove_duplicates(data_list)
    # print(len(oracle['all_data']))
    # return split_dataset(oracle['all_data'])
    



def split_dataset(dataset):
    i = len(dataset)
    training_len = int(i*0.7)
    validation_len = int(i*0.2)

    training = dataset[0:training_len]
    testing = dataset[training_len+validation_len:i]
    validation = dataset[training_len:training_len+validation_len]
    ds = {
        'train': training,
        'valid': validation,
        'test':testing
    }
    return ds



def get_dataset(file_path):
    with open(file_path) as f:
        dataset = load(f)
    return dataset['data']



def write_train_oracle(oracle):
    num_of_segs = 10
    seg = len(oracle['train'])//num_of_segs
    for i in range(num_of_segs):
        with open(TRAIN_OUTPUT_PATH.replace('.', f'{i+1}.'), 'w') as f:
            dump({'data':oracle['train'][i*seg:(i+1)*seg]}, f, indent=2)   


def write_oracle(oracle):
    write_train_oracle(oracle)
    with open(TEST_OUTPUT_PATH, 'w') as f:
        dump({'data':oracle['test']}, f, indent=2)
    with open(VALID_OUTPUT_PATH, 'w') as f:
        dump({'data':oracle['valid']}, f, indent=2)



def main():
    seed(10)
    dataset = get_dataset(INPUT_PATH)
    oracle = get_oracle(dataset)
    # print(oracle)
    write_oracle(oracle)





if __name__ == '__main__':
    main()



    