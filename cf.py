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
    timer = time.time()
    # get dns records
    dnsresp = requests.get(f"https://api.cloudflare.com/client/v4/zones/{cfFiggy["zoneID"]}/dns_records?type=A", headers=cfheadersLmao)
    if dnsresp.status_code != 200: raise BufferError

    # purge dns records
    # cf add delete all to ur api mf
    for record in dnsresp.json()["result"]:
        requests.delete(f"https://api.cloudflare.com/client/v4/zones/{cfFiggy["zoneID"]}/dns_records/{record['id']}", headers=cfheadersLmao)

    # upload records with new ip (replace placeholder with ip and upload)
    # requests.Request('POST', f"https://api.cloudflare.com/client/v4/zones/{cfzone}/dns_records/import", headers=uploadHeaders, files=upload).prepare().body.decode('utf8')
    upload = {
        "file" : ("confusing.dns.txt", open(f"{__file__.replace('cf.py', '')}records.txt").read().replace("REPLACEHERE", ip), "text/plain"),
        "proxied" : (None, "true")
        }
    uploadresp = requests.post(f"https://api.cloudflare.com/client/v4/zones/{cfFiggy["zoneID"]}/dns_records/import", headers=cfheadersLmao, files=upload).json()

    # uploadresp["timing"]["process_time"] doesnt fucking exist anymore | cant use ternary on return :/
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
        except: switchresult = {"success" : False}
        
        dnsmode = "switched" if switchresult["success"] and switchresult["originalCount"] > 0 else "created"
        cfswitchText = f"cfswitch returned {switchresult["success"]} {f'| {dnsmode} {switchresult["recordCount"]} records in {switchresult["timeElapsed"]}s' if switchresult['success'] else ''}"

    iptext = f"{iper.split('.')[0]}.*.*.* -> {respText.split('.')[0]}.*.*.*"
    # can do "{iptext} {f'| cf returned {success}' if automigrate}"" but cuz the second part we cant, atleast on python ver below 11
    return {"error" : "", "resp" : f"new ip {iptext} | {cfswitchText if automigrate else ''}"}

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
print(f"\ninit kys module 9000 | no input loop or manual input for u")
isdatmfvalidtho = changeCheck(cfFiggy["zoneID"])

if isdatmfvalidtho["error"] != "":
    match isdatmfvalidtho["error"]:
        case "ipValid": errorText = "no action needed the ip is the same"
        case "invalidCheckIP": errorText = "could not retrieve ip from amazon servers (check internet connection)"
        case _: errorText = isdatmfvalidtho["error"]

print(f'\n  -> {isdatmfvalidtho["resp"] if isdatmfvalidtho["error"] == "" else f"False | {errorText}"}\n')
