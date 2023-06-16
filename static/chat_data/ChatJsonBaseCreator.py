import json


def create():
    given = {"111111": "ND",
             "222222": "ND",
             "333333": "ND",
             "444444": "ND"}
    data = {}
    for id,type in given.items():
        data[id] = {
        "type": type,
        "opposite" : "neurotypical" if type == "ND" else "neurodiverse",
        "current": {
            "interactions": {},
            "chat": [],
            "data": {}
        },
        "conversations": []
    }
    with open("data.json", 'w') as file:
        json.dump(data, file, indent=4)

if __name__ == '__main__':
    create()
