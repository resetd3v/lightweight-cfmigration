import requests, discord, time
from consts import consts, utils
from discord.ext import commands, tasks
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

    # idk if including the open in the ternary creates a new instance every iteration or not
    try:
        with open(f"{__file__.replace('__init__.py', '')}records.txt") as file:
            data = file.read()
    except Exception as e:
        error = "file"

    recordsList = [record for record in dnsresp.json()["result"] if record["name"] in data]

    originalCount, successCount, failCount = 0, 0, 0
    if not error:
        for record in recordsList:
            originalCount += 1
            if record["content"] != ip:
                newRecord = record
                newRecord["content"] = ip
                updateResp = requests.patch(f"https://api.cloudflare.com/client/v4/zones/{consts.cfZone}/dns_records/{record['id']}", headers=consts.cfheadersLmao, json=newRecord)
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
        if resp["error"] == "ipValid":
            if cfPrint.current_loop == 0: await utils.LOGGER.log(stack()[0][3], resp["error"], "debug")
            return
        else: await utils.LOGGER.log(stack()[0][3], f'cf returned {resp["error"]}', "ERROR")

    embed = discord.Embed(title="ermmm", color=0x0084d1)
    # can do {iptext + f' | cf returned {success}} but cuz the second part we cant atleast on python ver below 11
    embed.description = f'{resp["recordCount"]}/{resp["originalCount"]} switched in {resp["timeElapsed"]}' if resp["success"] else resp["error"]

    utils.LOGGER.log(stack()[0][3], embed.description)
    channel = consts.bot.get_channel(consts.vpschannel)
    await channel.send(embed=embed)
