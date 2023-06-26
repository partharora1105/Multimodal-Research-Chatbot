import json
from flask import Flask, request, render_template

app = Flask(__name__, static_folder="static")

localDomain = "http://localhost:5000"
publicDomain = "http://partharora1105.pythonanywhere.com/"
DOMAIN = localDomain

localPath = ""
publicPath = "/home/partharora1105/mysite/"
PATH = localPath


@app.route('/')
def hello_world():
    return 'Hello, World!'


def getData():
    json_file = PATH + "static/chat_data/data.json"
    with open(json_file, 'r') as file:
        return json.load(file)


def setData(data):
    json_file = PATH + "static/chat_data/data.json"
    with open(json_file, 'w') as file:
        json.dump(data, file, indent=4)





def checkSize(input):
    return len(input) > 5


def checkYes(input):
    if ("yes" in input.lower().strip()):
        return True
    elif ("no" in input.lower().strip()):
        return False
    else:
        return None


def typicalQuest(data, key, nextQuest, val, enableCheckSize = True):
    if enableCheckSize and not checkSize(val):
        data["text"].append(f"Can you elaborate?")
    else:
        data["vals"][key] = val
        data["text"].append(nextQuest)

    return data


@app.route("/chat/<id>", methods=["POST", "GET"])
def chat(id):
    parentData = getData()
    data = parentData[id]["chat"]
    if ("isStarted" not in data["vals"]):
        data["text"].append("Did you have any opportunities to interact with someone today, "
                            "like by talking to or hanging out with them? 'Yes' or 'No'")
        data["vals"]["isStarted"] = True
    else:
        try:
            userText = request.form["message"]
        except:
            userText = "Refreshed Page"
        data["text"].append(userText)
        if "isInteracted-one" not in data["vals"]:
            isYes = checkYes(userText)
            if isYes is None:
                data["text"].append("Sorry I didn't understand that, can you answer in 'Yes' or 'No'?")
            else:
                data["vals"]["isInteracted-one"] = isYes
                if isYes:
                    data["text"].append("Okay, can you tell me about the interactions you had? Write"
                                        " the name of the person you interacted with: ")
                else:
                    data["text"].append("Okay, what about anyone outside of your family? Like customers or "
                                        "family friends? Did you interact with them? 'Yes' or 'No'")
        elif "isInteracted-two" not in data["vals"] and "isInteracted-one" in data["vals"] and not data["vals"][
            "isInteracted-one"]:
            isYes = checkYes(userText)
            if isYes is None:
                data["text"].append("Sorry I didn't understand that, can you answer in 'Yes' or 'No'?")
            else:
                data["vals"]["isInteracted-two"] = isYes
                if isYes:
                    data["text"].append("Okay, can you tell me about the interactions you had? Write"
                                        " the name of the person you interacted with: ")
                else:
                    data["text"].append("What about people in your family or roommates?"
                                        " Did you interact with them? 'Yes' or 'No'")
        elif "isInteracted-three" not in data["vals"] and "isInteracted-two" in data["vals"] and not data["vals"][
            "isInteracted-two"]:
            isYes = checkYes(userText)
            if isYes is None:
                data["text"].append("Sorry I didn't understand that, can you answer in 'Yes' or 'No'?")
            else:
                data["vals"]["isInteracted-three"] = isYes
                if isYes:
                    data["text"].append("Okay, can you tell me about the interactions you had? Write"
                                        " the name of the person you interacted with: ")
                else:
                    data["text"].append("Since you didn't have any conversations, this "
                                        "conversation has ended.")
                    data['vals']['ended'] = True
        elif "name-check" not in data['vals']:
            name = userText[0].upper() + userText[1:].lower()
            data["text"].append(f"Is the name of the person (or what you call them) "
                                f"you interacted with {name}? Answer 'Yes' or 'No'.")
            data['vals']['name-check'] = name
        elif "name" not in data['vals']:
            isYes = checkYes(userText)
            if isYes is None:
                data["text"].append("Sorry I didn't understand that, can you answer in 'Yes' or 'No'?")
            else:
                if isYes:
                    name = data['vals']['name-check']
                    data["vals"]["name"] = name
                    data["text"].append(f"How did you feel about your time with {name}?")
                else:
                    del data['vals']['name-check']
                    data["text"].append("Okay, can you write the name of the person (or"
                                        " what you call them) you interacted with: ")

        elif "feeling" not in data['vals']:
            val = userText
            if checkSize(val):
                if "because" in val:
                    split = val.split("because")
                    data['vals']['feeling'] = split[0]
                    data['vals']['feeling-why'] = split[0]
                    data["text"].append("What was the best part of "
                                        f"interacting with {data['vals']['name']}?")
                else:
                    data['vals']['feeling'] = val
                    data["text"].append(f"Why did you feel that way?")
            else:
                data["text"].append(f"Can you elaborate?")

        elif "feeling-why" not in data['vals']:
            data = typicalQuest(data=data, key="feeling-why",
                                nextQuest=f"What was the best part of "
                                          f"interacting with {data['vals']['name']}?",
                                          val=userText)
        elif "best-part" not in data['vals']:
            data = typicalQuest(data=data, key="best-part",
                                nextQuest=f"What was the hardest part of "
                                          f"interacting with {data['vals']['name']}?",
                                          val=userText)
        elif "hardest-part" not in data['vals']:
            data = typicalQuest(data=data, key="hardest-part",
                                nextQuest=f"Do you wish that the {data['vals']['name']} "
                                          f"had done anything differently? Answer"
                                          f"'Yes' or 'No'.",
                                          val=userText,
                                        enableCheckSize= False)
        elif "opp-done-diff" not in data['vals']:
            isYes = checkYes(userText)
            if isYes is None:
                data["text"].append("Sorry I didn't understand that, can you answer in 'Yes' or 'No'?")
            else:
                if isYes:
                    data = typicalQuest(data=data, key="opp-done-diff",
                                        nextQuest=f"What do you think they should have done differently?",
                                          val=userText,
                                        enableCheckSize= False)
                else:
                    data = typicalQuest(data=data, key="opp-done-diff",
                                        nextQuest=f"Do you wish that you had done anything differently?"
                                                  f" Answer 'Yes' or 'No'.",
                                          val=userText,
                                        enableCheckSize= False)
                    data["vals"]["opp-done-diff-details"] = "NA"
        elif "opp-done-diff-details" not in data['vals']:
            data = typicalQuest(data=data, key="opp-done-diff-details",
                                nextQuest=f"Do you wish that you had done anything differently?",
                                          val=userText,
                                        enableCheckSize= False)
        elif "self-done-diff" not in data['vals']:
            isYes = checkYes(userText)
            if isYes is None:
                data["text"].append("Sorry I didn't understand that, can you answer in 'Yes' or 'No'?")
            else:
                if isYes:
                    data = typicalQuest(data=data, key="self-done-diff",
                                        nextQuest=f"What do you think you should have done differently?",
                                          val=userText,
                                        enableCheckSize= False)
                else:
                    data = typicalQuest(data=data, key="self-done-diff",
                                        nextQuest=f"Do you think you would want to interact"
                                                  f" with {data['vals']['name']} again? Answer"
                                                  f" 'Yes' or 'No'.",
                                          val=userText,
                                        enableCheckSize= False)
                    data["vals"]["self-done-diff-details"] = "NA"
        elif "self-done-diff-details" not in data['vals']:
            data = typicalQuest(data=data, key="self-done-diff-details",
                                nextQuest=f"Do you think you would want to interact"
                                          f" with {data['vals']['name']} again? Answer"
                                          f" 'Yes' or 'No'.",
                                          val=userText,
                                        enableCheckSize= False)
        elif "interact-again" not in data['vals']:
            data = typicalQuest(data=data, key="interact-again",
                                nextQuest=f"Why is that?",
                                          val=userText,
                                        enableCheckSize= False)
        elif "interact-again-detail" not in data['vals']:
            data["vals"]["interact-again-detail"] = userText
            data["text"].append("Is there anyone else with whom you had an interaction with? Answer"
                                          f" 'Yes' or 'No'.")
        elif "more-ppl" not in data['vals']:
            isYes = checkYes(userText)
            if isYes is None:
                data["text"].append("Sorry I didn't understand that, can you answer in 'Yes' or 'No'?")
            else:
                if isYes:
                    data['vals'] = {}
                    data["text"].append("Did you have any opportunities to interact with someone today, "
                                        "like by talking to or hanging out with them? 'Yes' or 'No'")
                    data["vals"]["isStarted"] = True
                else:
                    data["more-ppl"] = False
                    data["vals"]["ended"] = True
                    data["text"].append("Since you didn't have any conversations, this "
                                        "conversation has ended.")
    setData(parentData)
    chatData = data["text"]

    if ("ended" in data['vals']):
        data = getData()
        data[id]["data"].append(data[id]["chat"])
        data[id]["chat"] = {
            "vals": {},
            "text": [],
        }
        setData(data)

    return render_template('chat.html', totalMessages=len(chatData), chatList=chatData, session=0, id=id, domain=DOMAIN)


@app.route('/chat/admin/data', methods=['POST', 'GET'])
def api():
    json_file = PATH + "static/chat_data/data.json"
    with open(json_file, 'r') as file:
        data = json.load(file)
    return data


if DOMAIN != publicDomain:
    if __name__ == '__main__':
        app.debug = True
        app.run()
