import json
import openai
from flask import Flask, request, render_template

app = Flask(__name__, static_folder="static")

global OPEN_AI_KEY
OPEN_AI_KEY = "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"

localDomain = "http://localhost:5000"
publicDomain = "http://www.gtxr.club"
DOMAIN = localDomain

localPath = ""
publicPath = "/home/GTXR/mysite/"
PATH = localPath

def checkList(currChat):
    instruction = "Based on the following converstation, return a comma seperarted list of the people" \
                  "interacted with just the list nothing else" \
                  ", if you didn't find any, return 'NO'"
    prompt = instruction
    for i in range(len(currChat)):
        if i % 2 == 0:
            prompt += f"Bot : {currChat[i]}\n"
        else:
            prompt += f"User : {currChat[i]}\n"
    openai.api_key = OPEN_AI_KEY
    chat_completion = openai.ChatCompletion.create(model="gpt-3.5-turbo",
                                                   messages=[{"role": "user", "content": prompt}])
    gptOutput = chat_completion["choices"][0]["message"]["content"]
    print(gptOutput)
    if "NO" in gptOutput:
        return None
    else:
        return gptOutput.split(",")

def quest(userText, chatData, id, data, person, json_file, currKey, nextKey, question):
    interactions = data[id]["current"]["interactions"]
    if len(userText) < 10:
        chatData.append("Tell me more.")
    else:
        interactions[person][currKey] = userText
        chatData.append(question)
        interactions[person][nextKey] = ""

    with open(json_file, 'w') as file:
        json.dump(data, file, indent=4)
    return render_template('chat.html', totalMessages=len(chatData), chatList=chatData, session=0, id=id, domain=DOMAIN)

@app.route("/chat/<id>", methods=["POST", "GET"])
def chat(id):
    # Fetch Data
    json_file = PATH + "static/chat_data/data.json"
    with open(json_file, 'r') as file:
        data = json.load(file)
    chatData = data[id]["current"]["chat"]

    # Fetch User Input
    try:
        userText = request.form["message"]
        chatData.append(userText)
    except:
        userText = ""

    # Load First Page
    if (len(chatData) <= 1):
        # Initialize
        firstQuest = f"Did you have any opportunities to interact with {data[id]['opposite']} " \
                     f"people today, like by talking to or hanging out with them? "
        chatData = [firstQuest]
        data[id]["current"]["chat"] = chatData
        with open(json_file, 'w') as file:
            json.dump(data, file, indent=4)
        print("ayo")
        return render_template('chat.html', totalMessages=len(chatData), chatList=chatData, session=0, id=id, domain=DOMAIN)


    print("no")
    # If No Interactions
    if len(data[id]["current"]["interactions"]) == 0:
        interactionList = checkList(chatData)
        if interactionList:
            data[id]["current"]["interactions"] = {person: {'started': ""} for person in interactionList}
        else:
            if len(chatData) == 2:
                chatData.append("Okay, what about anyone outside of your family? Like customers or family friends?")
                data[id]["current"]["chat"] = chatData
            elif len(chatData) == 4:
                chatData.append("What about people in your family or roommates?")
                data[id]["current"]["chat"] = chatData
            else:
                chatData.append("Thank You, since you didn't have any interactions, this "
                                "conversation has ended")
                data[id]["current"]["chat"] = chatData
                data[id]["conversations"].append(data[id]["current"])
                data[id]["current"] = {"interactions": {}, "chat": [], "data": {}}
            with open(json_file, 'w') as file:
                json.dump(data, file, indent=4)
            return render_template('chat.html', totalMessages=len(chatData), chatList=chatData, session=0, id=id, domain=DOMAIN)

    # If they had Interactions
    interactions = data[id]["current"]["interactions"]
    for person in interactions:
        keys = ["started", "feeling", "whyFeeling", "bestPart", "hardestPart", "personRemedy", "selfRemedy",
                "interactAgain"]
        questions = [f"How did you feel about your time with {person}?",
                     f"Why did you feel that way?",
                     f"What was the best part of interacting with {person}?",
                     f"What was the hardest part of interacting with {person}?",
                     f"Do you wish that the {person} had done anything differently? Give details.",
                     f"Do you wish that you had done anything differently? Give details.",
                     f"Do you think you would want to interact with {person} again? If yes, why? If no, why not?"]
        for i in range(7):
            if (interactions[person][keys[i]] == ""):
                return quest(userText, chatData, id, data, person, json_file,
                             keys[i], keys[i + 1], questions[i])
        if (interactions[person][keys[7]] == "" and interactions[person][keys[6]] != ""):
            interactions[person][keys[7]] = userText

    final = "Okay, that gives me a good idea of what you did today. " \
            "Thanks for sharing your interactions with me. If there are" \
            "any other interactions you would like to log, you may refresh" \
            "the page and restart the conversation. Have a good rest of " \
            "your day"
    chatData.append(final)
    data[id]["current"]["chat"] = chatData
    #Restart
    data[id]["conversations"].append(data[id]["current"])
    data[id]["current"] = {"interactions": {}, "chat": [], "data": {}}
    with open(json_file, 'w') as file:
        json.dump(data, file, indent=4)
    return render_template('chat.html', totalMessages=len(chatData), chatList=chatData, session=0, id=id, domain=DOMAIN)

@app.route('/chat/admin/data',methods = ['POST', 'GET'])
def api():
    json_file = PATH + "static/chat_data/data.json"
    with open(json_file, 'r') as file:
        data = json.load(file)
    return data


def gpt(currChat, input):
    if input == "":
        return currChat
    currChat.append(input)
    instruction = "You are the daily diary of user logging the details of user's interactions, you want to" \
                  "know the details of interactions the user had lately. You want details like the " \
                  "how did they feel about their coversation with the person and why did they feel that way," \
                  "what was the best and hardest part," \
                  "did they wish they had done something differently and details," \
                  "did they wish the person had done something differently and details," \
                  "and if they want to have the interaction again." \
                  "Once done you say 'DONE'," \
                  "If not, return the your next dialogue, only 1 dialogue of the daily diary, nothing else." \
                  "This should be a 2 line dialogue at the max. Also note you must get at least one interaction," \
                  "if they refuse, you must ask again"

    prompt = instruction
    for i in range(len(currChat)):
        if i % 2 == 0:
            prompt += f"Daily Diary : {currChat[i]}\n"
        else:
            prompt += f"User : {currChat[i]}\n"
    prompt += f"Daily Diary : "
    openai.api_key = OPEN_AI_KEY
    chat_completion = openai.ChatCompletion.create(model="gpt-3.5-turbo",
                                                   messages=[{"role": "user", "content": prompt}])

    gptOutput = chat_completion["choices"][0]["message"]["content"]
    currChat.append(gptOutput)
    print(prompt)
    return currChat


if __name__ == '__main__':
    app.debug = True
    app.run()
