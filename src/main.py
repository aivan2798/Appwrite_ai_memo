import openai
from .utils import get_static_file, throw_if_missing
from appwrite.client import Client
from appwrite.services.databases import Databases
import appwrite
import os


proj_id = os.environ.get("PROJ_ID")
sec_key = os.environ.get("SECRET_KEY")
coll_id = os.environ.get("COLLECTION_ID")
db_id = os.environ.get("DB_ID")
key_stat = "123456789abcdeftcgeta23erdfhfkduw872"

client = Client()
client.set_endpoint('https://cloud.appwrite.io/v1')  # Replace with your Appwrite API endpoint
client.set_project(proj_id)  # Replace with your Appwrite project ID
client.set_key(sec_key)

gpt_temp = {
      "role": "user",
      "content": ""
    }

gpt_msg =[
    {
      "role": "system",
      "content": "hello brain, please act as a caring friend who has the capability of saving, recalling, understanding and digesting the memories i will be giving him.\neach memory will have a memory id which i will tell you via the key word use_mem_id: \"memory_id\" , each memory will also have a memory title which i will tell you using the key word use use_mem_header: \"memory_title\" , each memory will also contain the content which will be identified by the keyword use_mem_data: \"memory contents\" , each memory will also contain tags represented by use_mem_tags: [list of memory tags] . i will later ask you questions about the different memories so that you help me recall them. thanks."
    }]

def eatUser(user_data):
    return user_data

def gen_db_id(name):
    name_len = len(name)
    rem_len = (big_len - name_len)

    namex=name+key_stat[:rem_len]
    return namex

def awaddmem(mem_data):
    name = mem_data["nickname"]
    
    database = appwrite.services.databases.Databases(client)
    title = mem_data["title"]
    content = mem_data["content"]
    tags = mem_data["tags"]

    doc_id = gen_db_id(name)
    memory = f"use_title:'{title}' use_content:'{content}' use_tags:'{tags}'"
    
    doc_result = database.get_document(db_id,coll_id,doc_id)
    memories = doc_result['memories']

    memories.append(memory)

    data = {
        'memories': memories

    }
    #print(doc_result)
    #print(memory)
    
    result = database.update_document(db_id,coll_id,doc_id, data)
    res = {"ok":true}
    return res

def awgetmems(mem_data):
    name = mem_data["nickname"]
    
    database = appwrite.services.databases.Databases(client)
    
    doc_id = gen_db_id(name)
    doc_result = database.get_document(db_id,coll_id,doc_id)
    memories = doc_result['memories']

    return memories

def gptEat(json_std):
    mems = awgetmems(json_std)
    my_gpt_msg = gpt_msg
    for mem in mems:
        my_gpt = gpt_temp
        my_gpt['content']=mem
        my_gpt_msg.append(my_gpt)
    qtn = json_std["query"]
    xmy_gpt = gpt_temp
    xmy_gpt["content"] = "from my memories, "+str(qtn)
    my_gpt_msg.append(xmy_gpt)
    #print(my_gpt_msg)
    return my_gpt_msg



def awcreatedb(json_std):
    name = json_std["nickname"]

    # Initialize the database service
    database = appwrite.services.databases.Databases(client)

    collection_id = coll_id 
    
    namex = gen_db_id(name)
    data = {
        'nick_name': name,
        'memories': []
    }


    doc_id = namex
    result = database.create_document(db_id,collection_id,doc_id, data)
    return result["$id"]

def handlePrompt(prompt,context):
    try:
        #response = openai.ChatCompletion.create(
        #    model="gpt-3.5-turbo",
        #    max_tokens=int(os.environ.get("OPENAI_MAX_TOKENS", "512")),
        #    messages=[{"role": "user", "content": prompt}],
        #)
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            max_tokens=int(os.environ.get("OPENAI_MAX_TOKENS", "512")),
            messages=prompt,
        )
        completion = response.choices[0].message.content
        json_data= {"ok": True, "completion": completion}
        return json_data
    except Exception:
        json_error = {"ok": False, "error": "Failed to query model."}
        return json_error

def main(context):
    throw_if_missing(os.environ, ["OPENAI_API_KEY"])

    if context.req.method == "GET":
        return context.res.send(
            get_static_file("index.html"),
            200,
            {
                "content-type": "text/html",
            },
        )

    req_body = context.req.body
    command = req_body["cmd"]
    cmd_data = req_body["content"]

    if command == "eat_mem" :
        #prompt_dta = handlePrompt(cmd_data,context)
        awaddmem(cmd_data)
        #if prompt_dta["ok"]==True:
        #   return context.res.json(prompt_dta, 200)
        rst = {"ok":True}
        return context.res.json(rst, 200)
    elif command == "eat_user":
            #usr_data = eatUser(cmd_data)
            awcreatedb(cmd_data)
            return context.res.json(usr_data, 200)
    elif command == "buff_mem":
            my_prompt = gptEat(json_ct)
            handlePrompt(my_prompt,context)
            if prompt_dta["ok"]==True:
                return context.res.json(prompt_dta, 200)
    #try:
    #    throw_if_missing(context.req.body, ["prompt"])
    #except ValueError as err:
    #    return context.res.json({"ok": False, "error": err.message}, 400)

    #openai.api_key = os.environ["OPENAI_API_KEY"]

    #try:
        
    #    response = openai.ChatCompletion.create(
    #        model="gpt-3.5-turbo",
    #        max_tokens=int(os.environ.get("OPENAI_MAX_TOKENS", "512")),
    #        messages=[{"role": "user", "content": context.req.body["prompt"]}],
    #    )
    #    completion = response.choices[0].message.content
    #    return context.res.json({"ok": True, "completion": completion}, 200)

    #except Exception:
    #   return context.res.json({"ok": False, "error": "Failed to query model."}, 500)
