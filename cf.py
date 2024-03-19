import requests, discord, time
from discord.ext import commands, tasks
from os import system, name as platform
from urllib.parse import unquote
from inspect import stack

"""
this was so scuffed switching from a disc bot to normal ngl i added like 10 lines
my bots better ong
https://discord.gg/funkdAeGfZ
qoft i miss u
"""

# retrieved by config in main normally lmao
global cfheadersLmao, cfFiggy
cfFiggy = {
        "apiKey" : "keyhere",
        "zoneID" : "zoneidhere"
    }

cfheadersLmao = {"Authorization" : f"Bearer {cfFiggy['apiKey']}"}

# also async in bot idk y tbh
def cfswitch(cfheadersLmao: dict, cfzone, ip):
    timer = time.time()
    # get dns records
    dnsresp = requests.get(f"https://api.cloudflare.com/client/v4/zones/{cfzone}/dns_records?type=A", headers=cfheadersLmao)
    if dnsresp.status_code != 200: raise BufferError

    #purge dns records
    # cf add delete all to ur api mf
    # for record in dnsresp.json()["result"]:
    #     requests.delete(f"https://api.cloudflare.com/client/v4/zones/{cfzone}/dns_records/{record['id']}", headers=cfheadersLmao)

    # get records replace placeholder with ip and upload
    # with open(f"{__file__.replace('__init__.py', '')}confusing.wtf.txt") as dnsrecords:
    #     newdns = dnsrecords.read().replace("REPLACEHERE", ip)

    # upload records with new ip
    # requests.Request('POST', f"https://api.cloudflare.com/client/v4/zones/{cfzone}/dns_records/import", headers=uploadHeaders, files=upload).prepare().body.decode('utf8')
    upload = {
        "file" : ("confusing.dns.txt", open(f"{__file__.replace('cf.py', '')}domain.com.txt").read().replace("REPLACEHERE", ip), "text/plain"),
        "proxied" : (None, "true")
        }
    uploadresp = requests.post(f"https://api.cloudflare.com/client/v4/zones/{cfzone}/dns_records/import", headers=cfheadersLmao, files=upload).json()

    # uploadresp["timing"]["process_time"] doesnt fucking exist anymore | cant use ternary on return :/
    return {
        "success" : uploadresp["success"],
        "recordCount" : uploadresp["result"]["recs_added"],
        "originalCount" : dnsresp["result_info"]["count"],
        "timeElapsed" : time.time() - timer
        }
    


##@tasks.loop(minutes=30) | async
def changeCheck(bot: commands.Bot, cfheadersLmao, cfzone, vpschannel, automigrate=True):
    # get ip to switch to
    resp = requests.get("https://checkip.amazonaws.com/")
    if resp.status_code != 200: return
    # fuck u amazon
    respText = resp.text.replace("\n", "")

    # femboy arch check
    delimter = "/" if platform != "nt" else "\\"
    # cant use r+ for some reason | {__file__.replace(f'admin{delimter}cf{delimter}__init__.py', ''} | no cwd problems for u could also use split to remove filename
    with open(f"{__file__.replace(f'cf.py', '')}tmp.txt", "r") as fileLmao:
        iper = fileLmao.read()
        fileLmao.close()

    # up to date
    if iper == respText: return False
    # get logging channel (also in config)
    ##channel = bot.get_channel(vpschannel)
    with open(f"{__file__.replace(f'cf.py', '')}tmp.txt", "w") as fileLmao:
        # clear
        fileLmao.truncate(0)
        fileLmao.write(respText)
        fileLmao.close()
    
    if automigrate:
        try: switchresult = cfswitch(cfheadersLmao, cfzone, respText)
        except: switchresult = {"success" : False}
        # scuffed this isnt in orignal lmao i dont use dict i use tuple
        dnsmode = "switched" if switchresult["success"] and switchresult["recordCount"] > 0 else "created"
        cfswitchText = f"{f'cfswitch returned {switchresult["success"]}'} {f'| {dnsmode} {switchresult["recordCount"]} records in {switchresult["timeElapsed"]}s' if switchresult['success'] else ''}"

    # me when * in discord
    ##iptext = f"{iper.split('.')[0]}.\\*.\\*.* -> {respText.split('.')[0]}.\\*.\\*.*"
    iptext = f"{iper.split('.')[0]}.*.*.* -> {respText.split('.')[0]}.*.*.*"
    ##embed = discord.Embed(title="ermmm", color=0x0084d1)
    # can do "{iptext} {f'| cf returned {success}' if automigrate}"" but cuz the second part we cant, atleast on python ver below 11
    ##embed.description = f"{iptext} | {cfswitchText if automigrate else ''}"
    ##print(f"[{stack()[0][3].upper()}] new ip {iptext} | {cfswitchText if automigrate else ''}")
    return f"[{stack()[0][3].upper()}] new ip {iptext} | {cfswitchText if automigrate else ''}"
    ##await channel.send(embed=embed)

# bestest
system("cls || clear")
print(f"\ninit kys module 9000 | no input loop or manual input for u")
isdatmfvalidtho = changeCheck(None, cfheadersLmao, cfFiggy["zoneID"], None)
print(f"\n  -> {isdatmfvalidtho if isdatmfvalidtho else "False (possible the ip is the same check tmp.txt)"}\n")
