"""
Christian Williams
Thesis
17 September 2022
This program takes the parsed q file and creates an oracle for the training and testing data.
"""
from os import getcwd
from json import load, loads, dumps
from random import randint, seed, shuffle





# Returns the input sentence for the oracle
def get_input_sentence(obj):
    output = ""
    keys = list(obj)
    shuffle(keys)
    for key in keys:
        if output != "":
            output += " "
        if key == "position":
            sep = " "
            output += f"{key} {sep.join(str(elem) for elem in obj[key])}"
        else:
            output += f"{key} {str(obj[key])}"
    return output




def get_direction(heading):
    if heading >= 337 or heading < 22:
        return "east"
    elif heading >= 22 and heading < 67:
        return "northeast"
    elif heading >= 67 and heading < 112:
        return "north"
    elif heading >= 112 and heading < 157:
        return "northwest"
    elif heading >= 157 and heading < 202:
        return "west"
    elif heading >= 202 and heading < 247:
        return "southwest"
    elif heading >= 247 and heading < 292:
        return "south"
    elif heading >= 292 and heading < 337:
        return "southeast"



# temporary work around input file format
def get_action_obj(action):
    action_obj = {}
    action_obj["throttle"] = action[0]
    action_obj["steer"] = action[1]
    action_obj["jump"] = action[5]
    action_obj["boost"] = action[6]
    action_obj["handbrake"] = action[7]
    return action_obj



def get_pos_ner_tags(pos_sentence):
    pos_sentence = pos_sentence.strip().replace(".", " .")
    tokens = pos_sentence.split()
    pos_labels = [
        "quadrant", "1", "2", "3", "4",
        "orange", "blue", "goal", "center",
        "wall", "north", "south", "east", "west"
    ]
    ner_tags = []
    for token in tokens:
        if token in pos_labels:
            ner_tags.append(16)
        else:
            ner_tags.append(0)
    return ner_tags




def get_position_sentence(x,y):
    pos = []
    if x >= 0 and y >= 0:
        pos.append("in quadrant 1")
    if x < 0 and y >= 0:
        pos.append("in quadrant 2")
    if x < 0 and y < 0:
        pos.append("in quadrant 3")    
    if x >= 0 and y < 0:
        pos.append("in quadrant 4")
    if x <= 1000 and x >= -1000 and y <= 1000 and y >= -1000:
        pos.append("near the center")
    if x <= 1000 and x >= -1000 and y <= -3120:
        pos.append("near the blue goal")
    if x <= 1000 and x >= -1000 and y >= 3120:
        pos.append("near the orange goal")
    if x <= -3096:
        pos.append("near the east wall")
    if x >= 3096:
        pos.append("near the west wall")
    if y <= -4120:
        pos.append("near the south wall")
    if y >= 4120:
        pos.append("near the north wall")
    sep = " and "
    sentence = f"I'm {pos[0]} {sep.join(pos[1:])}".strip() +"."
    ner_tags = get_pos_ner_tags(sentence)
    return sentence, ner_tags



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
    if key == "steer":
        if value == -1:
            return "left"
        else:
            return "right"
    if key == "throttle":
        if value == 1:
            return "forwards"
        else:
            return "backwards"



def replace_placeholder(text, value):
    return text.replace("*r", str(value))

def get_sentence(template, percept, index):
    return template[percept][index][0]


def get_ner_tags(template, percept, index):
    return template[percept][index][1]                              
                                    

def get_action_sentence(template, action, index):
    return template["action"][action][index][0]


def get_action_ner_tags(template, action, index):
    return template["action"][action][index][1]



def get_sentence_and_ner_tags(template, obj, percept=None, action=None):
    index = get_index()
    ner_tags = []
    if percept:
        sentence = get_sentence(template, percept, index)
        ner_tags = get_ner_tags(template, percept, index)
        if percept != "direction":
            value = obj[percept]
        else:
            value = get_direction(obj[percept])
    else:
        sentence = get_action_sentence(template, action, index)
        ner_tags = get_action_ner_tags(template, action, index)
        value = get_action(action, obj[action])
    return replace_placeholder(sentence, value), ner_tags



# Accepts the measures and action as an input
# returns the target sentence
def get_target_sentence(obj, action):
    pos = obj["position"]
    sentence = ""
    template = get_sentences_template()
    ner_tags = []

    # select sentences from the template and replace the attributes as necessary
    if obj["is_demoed"]:
        index = get_index()
        col = "is_demoed"
        return get_sentence(template, col, index), get_ner_tags(template, col, index)

    # Create sentences for each percept and action
    num_sentences = 7
    nums = [i for i in range(num_sentences)]
    shuffle(nums)

    for num in nums:

        match num:
            # Percept (boost_amount)
            case 0:
                if obj["boost_amount"] > 0:
                    text = get_sentence_and_ner_tags(template, obj, "boost_amount")
                    sentence += f" {text[0]}"
                    ner_tags += text[1]

            # Percept(on_ground)
            case 1:
    
                if obj["on_ground"]:
                    index = get_index()
                    col = "on_ground"
                    sentence += f" {get_sentence(template, col, index)}"
                    ner_tags += get_ner_tags(template, col, index)
            # Percept(speed)
            case 2:
                text = get_sentence_and_ner_tags(template, obj, "speed")
                sentence += f" {text[0]}"
                ner_tags += text[1]

            # Percept(Direction)
            case 3:
                text = get_sentence_and_ner_tags(template, obj, "direction")
                sentence += f" {text[0]}"
                ner_tags += text[1]

            # Percept(Position)
            case 4:
                text = get_position_sentence(pos[0], pos[1])
                sentence += f" {text[0]}"
                ner_tags += text[1]

            # Action(Brake) or (Action(Steer) and/or Action(Throttle))
            case 5:
                if action["handbrake"]:
                    index = get_index()
                    col = "handbrake"
                    sentence += f" {get_action_sentence(template, col, index)}"
                    ner_tags += get_action_ner_tags(template, col, index)
                else:
                    text1 = get_sentence_and_ner_tags(template, action, action="steer")
                    text2 = get_sentence_and_ner_tags(template, action, action="throttle")

                    temp1 = f" {text1[0]}".replace(".", "")
                    temp2 = f"{text2[0]}"
                    sep = ' and '
                    sentence += f" {sep.join([temp1, temp2])}"

                    ner_tags += text1[1]
                    ner_tags += text2[1]

            # Action(Boost)
            case 6:
                if action["boost"]:
                    index = get_index()
                    col = "boost"
                    sentence += f" {get_action_sentence(template, col, index)}"
                    ner_tags += get_action_ner_tags(template, col, index)

    sentence = sentence.replace("  ", " ").strip()
    # print(sentence.split(" "), len(ner_tags), len(sentence.split(" ")))
    return sentence, ner_tags



def get_ner_id_map():
    ner_id_map = {
        0: "O",
        1: "L-DEMO",
        2: "L-BA",
        3: "V-BA",
        4: "L-GROUND",
        5: "L-BALL",
        6: "L-SPEED",
        7: "V-SPEED",
        8: "L-DIR",
        9: "V-DIR",
        10: "L-BRAKE",
        11: "L-STEER",
        12: "V-STEER",
        13: "L-THROTTLE",
        14: "V-THROTTLE",
        15: "L-BOOST",
        16: "L-POS"
    }
    return ner_id_map


def get_ner_tag_map():
    ner_tag_map = {
        "O": 0,
        "L-DEMO": 1,
        "L-BA": 2,
        "V-BA": 3,
        "L-GROUND": 4,
        "L-BALL": 5,
        "L-SPEED": 6,
        "V-SPEED": 7,
        "L-DIR": 8,
        "V-DIR": 9,
        "L-BRAKE": 10,
        "L-STEER": 11,
        "V-STEER": 12,
        "L-THROTTLE": 13,
        "V-THROTTLE": 14,
        "L-BOOST": 15,
        "L-POS": 16
    }
    return ner_tag_map



# returns the sentences template
def get_sentences_template():
    template = {
        "is_demoed": [
            ["My car has been demolished.", [0,0,1,0,1,0]],
            ["My car has exploded!", [0,0,1,1,0]],
            ["I crashed my car!", [0,1,0,0,0]],
            ["I wrecked my car.", [0,1,0,0,0]]
        ],
        "boost_amount": [
            ["My current boost is *r.", [0,2,2,0,3,0]],
            ["I currenly have *r percent boost.", [0,2,0,3,0,2,0]],
            ["I have *r boost.", [0,0,3,2,0]],
            ["My boost is *r percent.", [0,2,0,3,0,0]],
        ],
        "on_ground": [
            ["My car is on the ground.", [0,0,0,4,0,4,0]],
            ["I'M on the ground.", [0,4,0,4,0]],
            ["I'M not in the air.", [0,4,0,0,4,0]],
            ["I'M currently driving on the ground.", [0,0,0,4,0,4,0]]
        ],
        "ball_touched": [
            ["I have the ball!", [0,5,0,5,0]],
            ["I've got the ball!", [0,5,0,5,0]],
            ["I currently have the ball.", [0,0,5,0,5,0]],
            ["The ball is in my possession.", [0,5,0,0,5,5,0]],
        ],
        "speed": [
            ["My current speed is *r.", [0,0,6,0,7,0]],
            ["I'm travelling *r miles per hour.", [0,0,7,6,6,6,0]],
            ["My current speed is *r mph.", [0,0,6,0,7,6,0]],
            ["My current speed is *r miles per hour.", [0,0,6,0,7,6,6,6,0]]
        ],
        "direction": [
            ["I'M currently travelling *r.", [0,8,8,9,0]],
            ["I'M heading in the *r direction.", [0,8,0,0,9,8,0]],
            ["My current direction is *r.", [0,8,8,0,9,0]],
            ["I'M heading *r.", [0,8,9,0]],
        ],
        "position": [],
        "action": {
            "handbrake": [
                ["I'M currently braking.", [0,10,10,0]],
                ["I pressed the brakes.", [0,10,0,10,0]],
                ["I'M stopping", [0,10,0]],
                ["I stopped.", [0,10,0]],
            ],
            "steer": [
                ["I'M steering *r.", [0,11,12,0]],
                ["I'M turning *r.", [0,11,12,0]],
                ["I turned *r.", [0,11,12,0]],
                ["I'M about to turn *r.", [0,0,0,11,12,0]],
            ],
            "throttle": [
                ["I'M driving *r.", [0,13,14,0]],
                ["I'M going *r.", [0,13,14,0]],
                ["I'M moving *r.", [0,13,14,0]],
                ["I'M travelling *r.", [0,13,14,0]]
            ],
            "boost": [
                ["I've used boost.", [0,15,15,0]],
                ["I'M using boost.", [0,15,15,0]],
                ["I've used the speed up.", [0,15,0,15,15,0]],
                ["I have boosted.", [0,15,15,0]]
            ]
        }        
    }
    return template



def get_ner_input_sentence(sentence, ner_tags):
    ner_input = ""
    sentence = sentence.replace(".", " .").replace("!", " !")
    tokens = sentence.split(" ")
    for token in tokens:
        if ner_tags[tokens.index(token)] != 0:
            ner_input += f" {token}"
    return ner_input.strip()




def remove_duplicates(dataset):
    set_of_jsons = set([dumps(d, sort_keys=True) for d in dataset])
    return [loads(t) for t in set_of_jsons]

def get_ner_tag_str(ner_tag):
    return get_ner_id_map()[ner_tag]


# returns the oracle from the data set
def get_oracle(dataset, num_iters):
    oracle = {}
    data_list = []
    oracle["all_data"] = []
    oracle["data"] = {}
    for i in range(num_iters):
        for data in dataset:
            obj = {}
            action = get_action_obj(data["action"])
            data = data["state"]["measurements"]
            action_string = " ".join(f"{key} {action[key]}" for key in action.keys())
            obj["state"] = f"{get_input_sentence(data)} {action_string}".replace("  ", " ")
            obj["sentence"], obj["ner_tags"] = get_target_sentence(data, action)
            obj["sentence"] = obj["sentence"].replace("  ", " ")
            obj["ner_tags"] = list(map(get_ner_tag_str, obj["ner_tags"]))
            obj["ner_sentence"] = get_ner_input_sentence(obj["sentence"], obj["ner_tags"])
            data_list.append(obj)
    print(len(data_list))
    oracle["all_data"] = remove_duplicates(data_list)
    oracle["ner_tag_map"] = get_ner_tag_map()
    oracle["ner_id_map"] = get_ner_id_map()
    print(len(oracle["all_data"]))
    return split_dataset(oracle)



def split_dataset(oracle):
    dataset = oracle["all_data"]
    i = len(dataset)
    training_len = int(i*0.7)
    validation_len = int(i*0.2)

    training = dataset[0:training_len]
    testing = dataset[training_len+validation_len:i]
    validation = dataset[training_len:training_len+validation_len]
    ds = {
        "train": training,
        "valid": validation,
        "test":testing,
        "ner_id_map": oracle["ner_id_map"],
        "ner_tag_map": oracle["ner_tag_map"]
    }
    return ds



def get_dataset(file_path):
    with open(file_path) as f:
        dataset = load(f)
    return dataset["data"]


def write_oracle(oracle, path, ds_type, num_of_segs):
    seg = len(oracle[ds_type])//num_of_segs
    for i in range(num_of_segs):
        file_path = path.replace(".", f"-{i+1}.")
        output = oracle[ds_type][i*seg:(i+1)*seg]
        output_str = dumps(output, indent=4)
        print(f"Writing {path.replace('.', f'{i+1}.')} to disk...")
        with open(file_path, "w") as f:
            f.write(output_str)




def main():
    input_path = f"{getcwd()}\\input\\state-records-v2_2.json"
    test_output_path = f"{getcwd()}\\output\\oracle-test.jsonl"
    train_output_path = f"{getcwd()}\\output\\oracle-train.jsonl"
    valid_output_path = f"{getcwd()}\\output\\oracle-valid.jsonl"

    train_type = "train"
    valid_type = "valid"
    test_type = "test"

    num_iters = 8

    train_file_div = 10
    valid_file_div = 3
    test_file_div = 1

    seed(10)

    dataset = get_dataset(input_path)
    oracle = get_oracle(dataset, num_iters)

    write_oracle(oracle, train_output_path, train_type, train_file_div)
    write_oracle(oracle, valid_output_path, valid_type, valid_file_div)
    write_oracle(oracle, test_output_path, test_type, test_file_div)





if __name__ == "__main__":
    main()


