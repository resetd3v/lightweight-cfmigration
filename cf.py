import requests, time, argparse
from os import system

"""
this was so scuffed switching from a disc bot to normal ngl i added like 10 lines
my bots better ong
https://discord.gg/funkdAeGfZ
qoft i miss u
"""

# retrieved by config in main normally lmao
# cfFiggy = {
#         "apiKey" : "keyhere",
#         "zoneID" : "zoneidhere"
#     }

# cfheadersLmao = {"Authorization" : f"Bearer {cfFiggy['apiKey']}"}

# also async in bot cuz wait until returner
def cfswitch(ip):
    error = ""
    timer = time.time()
    # get dns records
    dnsresp = requests.get(f"https://api.cloudflare.com/client/v4/zones/{cfFiggy["zoneID"]}/dns_records?type=A", headers=cfheadersLmao)
    if dnsresp.status_code != 200: error = "getDNS"

    # purge dns records
    # cf add delete all to ur api mf
    # no list comp for u
    for record in dnsresp.json()["result"]:
        requests.delete(f"https://api.cloudflare.com/client/v4/zones/{cfFiggy["zoneID"]}/dns_records/{record['id']}", headers=cfheadersLmao)

    # upload records with new ip (replace placeholder with ip and upload)
    # requests.Request('POST', f"https://api.cloudflare.com/client/v4/zones/{cfzone}/dns_records/import", headers=uploadHeaders, files=upload).prepare().body.decode('utf8')
    try:
        upload = {
            "file" : ("confusing.dns.txt", open(f"{__file__.replace('cf.py', '')}records.txt").read().replace("REPLACEHERE", ip), "text/plain"),
            "proxied" : (None, "true")
            }
    except: error = "file"
    uploadresp = requests.post(f"https://api.cloudflare.com/client/v4/zones/{cfFiggy["zoneID"]}/dns_records/import", headers=cfheadersLmao, files=upload)
    if uploadresp.status_code != 200: error = "uploadRecs"

    # uploadresp["timing"]["process_time"] doesnt fucking exist anymore | cant use ternary on return :/
    if error != "": return {"success" : False, "error" : error}
    uploadresp = uploadresp.json()
    return {
        "success" : uploadresp["success"],
        "recordCount" : uploadresp["result"]["recs_added"],
        "originalCount" : dnsresp["result_info"]["count"],
        "timeElapsed" : time.time() - timer
        }

##@tasks.loop(minutes=30) | async
def changeCheck(automigrate=True):
    # get ip to switch to
    resp = requests.get("https://checkip.amazonaws.com/")
    if resp.status_code != 200: return {"error" : "invalidCheckIP"}
    # fuck u amazon
    respText = resp.text.replace("\n", "")

    # femboy arch check
    #delimter = "/" if platform != "nt" else "\\"
    # dont need method close here cuz "with" closes after finished but idc
    # cant use r+ for some reason | {__file__.replace(f'admin{delimter}cf{delimter}__init__.py', ''} | no cwd problems for u could also use split to remove filename
    with open(f"{__file__.replace(f'cf.py', '')}tmp.txt", "r") as fileLmao:
        iper = fileLmao.read()
        fileLmao.close()

    # up to date
    if iper == respText: return {"error" : "ipValid"}

    with open(f"{__file__.replace(f'cf.py', '')}tmp.txt", "w") as fileLmao:
        # clear file
        fileLmao.truncate(0)
        fileLmao.write(respText)
        fileLmao.close()
    
    if automigrate:
        try: switchresult = cfswitch(respText)
        except: return {"success" : False, "error" : "unknownDog"}
        if not switchresult["success"]: return {"success" : False, "error": switchresult["error"]}
        
        dnsmode = "switched" if switchresult["originalCount"] > 0 else "created"
        cfswitchText = f"cfswitch returned {switchresult["success"]} | {dnsmode} {switchresult["recordCount"]} records in {switchresult["timeElapsed"]}s"

    iptext = f"{iper.split('.')[0]}.*.*.* -> {respText.split('.')[0]}.*.*.*"
    # can do "{iptext} {f'| cf returned {success}' if automigrate}"" but cuz the second part we cant, atleast on python ver below 11
    return {"success" : True, "error" : "", "ip" : iptext, "cfResp" : cfswitchText if automigrate else ''}

# auto retrieve zone id soontm
parser = argparse.ArgumentParser()
parser.add_argument("apikey", help="cloudflare api key")
parser.add_argument("zone", help="cloudflare zone id for the domain")
args = parser.parse_args()

cfFiggy = {
        "apiKey" : args.apikey,
        "zoneID" : args.zone
    }

cfheadersLmao = {"Authorization" : f"Bearer {cfFiggy['apiKey']}"}

# bestest
system("cls || clear")
print(f"\ninit kys module 9000 | i kiss boys (ren)")
isdatmfvalidtho = changeCheck(cfFiggy["zoneID"])

# cba to do exception specfific errors fuck yoy
if isdatmfvalidtho["error"] != "":
    match isdatmfvalidtho["error"]:
        case "ipValid": errorText = "no action needed the ip is the same"
        case "invalidCheckIP": errorText = "could not retrieve ip from amazon servers (check internet connection)"
        case "getDNS": errorText = "could not retrieve dns records from cloudflare (check api key and zone)"
        case "uploadRecs": errorText = "idfk check ur records.txt ig"
        case "file": errorText = "could not retrieve file (possibly the file was not found)"
        case _: errorText = isdatmfvalidtho["error"]

# could else here | have to do this cuz double "" in formatted string
if isdatmfvalidtho["success"]: ip, cfresp = isdatmfvalidtho["ip"], isdatmfvalidtho["cfResp"]
print(f'\n  -> {f"new ip: {ip} | {cfresp}" if isdatmfvalidtho["success"] else f"False | {errorText}"}\n')
