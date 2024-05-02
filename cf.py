import requests, time, argparse
from os import system

"""
this was so scuffed switching from a disc bot to cli
my bots better ong
https://discord.gg/confusing
backup:
https://discord.gg/funkdAeGfZ
"""

# retrieved by config in main normally lmao
# cfFiggy = {
#         "apiKey" : "keyhere",
#         "zoneID" : "zoneidhere"
#     }

# also async in bot cuz wait until returner
def cfswitch():
    error = None
    timer = time.time()
    resp = requests.get("https://checkip.amazonaws.com/")
    if resp.status_code != 200: return {"success" : False, "error" : "invalidCheckIP"}
    # fuck u amazon
    ip = resp.text.replace("\n", "")

    dnsresp = requests.get(f"https://api.cloudflare.com/client/v4/zones/{cfZone}/dns_records?type=A", headers=cfheadersLmao)
    if dnsresp.status_code != 200: error = "getDNS"

    # idk if including the open in the ternary creates a new instance every iteration or not
    try:
        with open(f"{__file__.replace('__init__.py', '')}records.txt") as file:
            data = file.read()
    except Exception as e:
        error = "file"

    recordsList = [record for record in dnsresp.json()["result"] if record["name"] in data]
    
    # aids but idc holky nested | i dont update original record for debugging
    originalCount, successCount, failCount = 0, 0, 0
    if not error:
        for record in recordsList:
            if record["content"] != ip:
                newRecord = record
                newRecord["content"] = ip
                updateResp = requests.patch(f"https://api.cloudflare.com/client/v4/zones/{cfZone}/dns_records/{record['id']}", headers=cfheadersLmao, json=newRecord)
                if updateResp.status_code == 200 and updateResp.json()["success"]: successCount += 1
                else: failCount += 1

        if successCount == 0 and failCount == 0: error = "ipValid"

    # theres a reason i dont use else but im not explainging it
    if error: return {"success" : False, "error" : error}

    dnsresp = dnsresp.json()
    return {
        "success" : True,
        "recordCount" : successCount,
        "failedCount" : failCount,
        "originalCount" : originalCount,
        "totalCount" : dnsresp["result_info"]["count"],
        "timeElapsed" : time.time() - timer
        }

# auto retrieve zone id soontm
parser = argparse.ArgumentParser()
parser.add_argument("apikey", help="cloudflare api key")
parser.add_argument("zone", help="cloudflare zone id for the domain")
# can use vars() here to have it as members of a class type shi
args = parser.parse_args()

cfFiggy = {
        "apiKey" : args.apikey,
        "zoneID" : args.zone
    }

cfheadersLmao = {"Authorization" : f"Bearer {cfFiggy['apiKey']}"}
cfZone = cfFiggy["zoneID"]

# bestest
system("cls || clear")
print(f"\ninit kys module 9000 | i kiss boys (ren)")
isdatmfvalidtho = cfswitch()

# cba to do exception specfific errors fuck yoy
if not isdatmfvalidtho["success"]:
    match isdatmfvalidtho["error"]:
        case "ipValid": errorText = "no action needed the ip is the same"
        case "invalidCheckIP": errorText = "could not retrieve ip from amazon servers (check internet connection)"
        case "getDNS": errorText = "could not retrieve dns records from cloudflare (check api key and zone)"
        case "file": errorText = "could not retrieve file (possibly the file was not found)"
        case _: errorText = isdatmfvalidtho["error"]

# could else here | have to do this cuz double "" in formatted string
if isdatmfvalidtho["success"]: recordCount, originalCount, timeElapsed = isdatmfvalidtho["recordCount"], isdatmfvalidtho["originalCount"], isdatmfvalidtho["timeElapsed"]
print(f'\n  -> {f"{recordCount}/{originalCount} switched in {timeElapsed}" if isdatmfvalidtho["success"] else f"False | {errorText}"}\n')
