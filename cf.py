import requests, discord, time
from consts import consts, utils
from discord.ext import tasks
from os import name as platform
from inspect import stack

# ".	"
async def cfcheck():
    error = None
    timer = time.time()
    resp = requests.get("https://checkip.amazonaws.com/")
    if resp.status_code != 200: return {"success" : False, "error" : "invalidCheckIP"}
    # fuck u amazon
    ip = resp.text.replace("\n", "")

    dnsresp = requests.get(f"https://api.cloudflare.com/client/v4/zones/{consts.cfZone}/dns_records?type=A", headers=consts.cfheadersLmao)
    if dnsresp.status_code != 200: error = "getDNS"

    try:
        with open(f"{__file__.replace('__init__.py', '')}records.txt") as file:
            data = file.read()
    except Exception as e:
        error = "file"
    
    # idc
    if error: return {"success" : False, "error" : error}

    recordsList = [record for record in dnsresp.json()["result"] if record["name"] in data]

    originalCount, successCount, failCount = 0, 0, 0

    for record in recordsList:
        originalCount += 1
        # breakpoint here to see original
        if record["content"] == ip: continue
        record["content"] = ip
        updateResp = requests.patch(f"https://api.cloudflare.com/client/v4/zones/{consts.cfZone}/dns_records/{record['id']}", headers=consts.cfheadersLmao, json=record)
        if updateResp.status_code == 200 and updateResp.json()["success"]: successCount += 1
        else: failCount += 1

    if successCount == 0 and failCount == 0: error = "ipValid"

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




@tasks.loop(minutes=5)
async def cfPrint():
    resp = await cfcheck()
    if not resp["success"]:

        match resp["error"]:
            case "ipValid":
                if cfPrint.current_loop == 0: await utils.LOGGER.log(stack()[0][3], resp["error"], "debug")
            case _: await utils.LOGGER.log(stack()[0][3], f'cf returned {resp["error"]}', "ERROR")
        return

    embed = discord.Embed(title="ermmm", color=0x0084d1)
    embed.description = f'{resp["recordCount"]}/{resp["originalCount"]} switched in {resp["timeElapsed"]}' if resp["success"] else resp["error"]

    # epic naming
    utils.LOGGER.discEphemeral(stack()[0][3], embed.description)
    channel = consts.bot.get_channel(consts.vpschannel)
    await channel.send(embed=embed)


# embed.description = f'{resp["ip"]} | {resp["cfResp"]}' if resp["success"] else resp["error"]
# # python version moment
# ip, cfresp, success = resp["ip"], resp["cfResp"], resp["success"]
# if not success: error = resp["error"]

# print(f'[{stack()[0][3]}] {f"new ip: {ip} | {cfresp}" if success else f"False | {error}"}')
# channel = consts.bot.get_channel(consts.vpschannel)
# await channel.send(embed=embed)

# async def changeCheck(auto=True):
#     # get ip to switch to
#     resp = requests.get("https://checkip.amazonaws.com/")
#     if resp.status_code != 200: return {"success" : False, "error" : "invalidCheckIP"}
#     # fuck u amazon
#     respText = resp.text.replace("\n", "")

#     # femboy arch check
#     #delimter = "/" if platform != "nt" else "\\"
#     # dont need method close here cuz "with" closes after finished but idc
#     # cant use r+ for some reason | {__file__.replace(f'admin{delimter}cf{delimter}__init__.py', ''} | no cwd problems for u could also use split to remove filename
#     with open(f"{__file__.replace(f'__init__.py', '')}tmp.txt", "r") as fileLmao:
#         iper = fileLmao.read()
#         fileLmao.close()

#     # up to date
#     if iper == respText: return {"success" : False, "error" : "ipValid"}

#     with open(f"{__file__.replace(f'__init__.py', '')}tmp.txt", "w") as fileLmao:
#         # clear file
#         fileLmao.truncate(0)
#         fileLmao.write(respText)
#         fileLmao.close()
    
#     try: switchresult = await cfswitch(respText)
#     except: return {"success" : False, "error" : "unknownDog"}
#     if not switchresult["success"]: return {"success" : False, "error": switchresult["error"]}
    
#     dnsmode = "switched" if switchresult["originalCount"] > 0 else "created"
#     cfswitchText = f'cfswitch returned {switchresult["success"]} | {dnsmode} {switchresult["recordCount"]} records in {switchresult["timeElapsed"]}s'

#     iptext = f"{iper.split('.')[0]}.\*.\*.\* -> {respText.split('.')[0]}.\*.\*.\*"
#     return {"success" : switchresult["success"], "ip" : iptext, "cfResp" : cfswitchText}

# async def cfswitch(ip):
#     error = ""
#     timer = time.time()
#     # get dns records
#     dnsresp = requests.get(f"https://api.cloudflare.com/client/v4/zones/{consts.cfZone}/dns_records?type=A", headers=consts.cfheadersLmao)
#     if dnsresp.status_code != 200: error = "getDNS"

#     # purge dns records
#     # cf add delete all to ur api mf
#     # no list comp for u
#     # for record in dnsresp.json()["result"]:
#     #     if record['name'] in open(f"{__file__.replace('__init__.py', '')}records.txt").read():
#     #         requests.delete(f"https://api.cloudflare.com/client/v4/zones/{consts.cfZone}/dns_records/{record['id']}", headers=consts.cfheadersLmao)

#     lmao = [requests.delete(f"https://api.cloudflare.com/client/v4/zones/{consts.cfZone}/dns_records/{record['id']}", headers=consts.cfheadersLmao) for record in dnsresp.json()["result"] if record['name'] in open(f"{__file__.replace('__init__.py', '')}records.txt").read()]

#     # upload records with new ip (replace placeholder with ip and upload)
#     # requests.Request('POST', f"https://api.cloudflare.com/client/v4/zones/{cfzone}/dns_records/import", headers=uploadHeaders, files=upload).prepare().body.decode('utf8')
#     try:
#         upload = {
#             "file" : ("confusing.dns.txt", open(f"{__file__.replace('__init__.py', '')}records.txt").read().replace("REPLACEHERE", ip), "text/plain"),
#             "proxied" : (None, "true")
#             }
#     except: error = "file"
#     uploadresp = requests.post(f"https://api.cloudflare.com/client/v4/zones/{consts.cfZone}/dns_records/import", headers=consts.cfheadersLmao, files=upload)
#     if uploadresp.status_code != 200: error = "uploadRecs"

#     # uploadresp["timing"]["process_time"] doesnt fucking exist anymore | cant use ternary on return :/
#     if error != "": return {"success" : False, "error" : error}
#     uploadresp = uploadresp.json()
#     dnsresp = dnsresp.json()
#     return {
#         "success" : uploadresp["success"],
#         "recordCount" : uploadresp["result"]["recs_added"],
#         "originalCount" : dnsresp["result_info"]["count"],
#         "timeElapsed" : time.time() - timer
#         }