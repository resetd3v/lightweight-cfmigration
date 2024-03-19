import requests, discord, time
from discord.ext import commands, tasks
from os import name as platform
from urllib.parse import unquote
from inspect import stack

# could use dict but idc that much tbh
async def cfswitch(cfheadersLmao: dict, cfzone, ip):
    timer = time.time()
    # purge dns records
    dnsresp = requests.get(f"https://api.cloudflare.com/client/v4/zones/{cfzone}/dns_records?type=A", headers=cfheadersLmao)
    if dnsresp.status_code != 200: return (False, None, None, None)

    for record in dnsresp.json()["result"]:
        requests.delete(f"https://api.cloudflare.com/client/v4/zones/{cfzone}/dns_records/{record['id']}", headers=cfheadersLmao)

    # get records replace placeholder with ip and upload
    # with open(f"{__file__.replace('__init__.py', '')}confusing.wtf.txt") as dnsrecords:
    #     newdns = dnsrecords.read().replace("REPLACEHERE", ip)

    # upload
    # requests.Request('POST', f"https://api.cloudflare.com/client/v4/zones/{cfzone}/dns_records/import", headers=uploadHeaders, files=upload).prepare().body.decode('utf8')
    upload = {
        "file" : ("confusing.dns.txt", open(f"{__file__.replace('__init__.py', '')}confusing.wtf.txt").read().replace("REPLACEHERE", ip), "text/plain"),
        "proxied" : (None, "true")
        }
    uploadresp = requests.post(f"https://api.cloudflare.com/client/v4/zones/{cfzone}/dns_records/import", headers=cfheadersLmao, files=upload).json()

    # uploadresp["timing"]["process_time"] doesnt fucking exist anymore | cant user ternary on return
    if uploadresp["success"]: return (uploadresp["success"], uploadresp["result"]["recs_added"], dnsresp.json()["result_info"]["count"], time.time() - timer)
    else: return (False, None, None, None)
    


@tasks.loop(minutes=30)
async def changeCheck(bot: commands.Bot, cfheadersLmao, cfzone, vpschannel, auto=True):
    resp = requests.get("https://checkip.amazonaws.com/")
    if resp.status_code != 200: return
    respText = resp.text.replace("\n", "")

    # cant use r+ for some reason
    delimter = "/" if platform != "nt" else "\\"
    with open(f"{__file__.replace(f'admin{delimter}cf{delimter}__init__.py', '')}lmao.txt", "r") as fileLmao:
        iper = fileLmao.read()
        fileLmao.close()

    if iper == respText: return
    channel = bot.get_channel(vpschannel)
    with open(f"{__file__.replace(f'admin{delimter}cf{delimter}__init__.py', '')}lmao.txt", "w") as fileLmao:
        fileLmao.truncate(0)
        fileLmao.write(respText)
        fileLmao.close()
    
    if auto:
        success, recordCount, origdnscount, time = await cfswitch(cfheadersLmao, cfzone, respText)
        dnsmode = "switched" if origdnscount > 0 else "created"
        cfswitchText = f"{f'cf returned {success}'} {f'| {dnsmode} {recordCount} records in {time}s' if success else ''}"

    iptext = f"{iper.split('.')[0]}.\\*.\\*.* -> {respText.split('.')[0]}.\\*.\\*.*"
    embed = discord.Embed(title="ermmm", color=0x0084d1)
    # can do {iptext + f' | cf returned {success}} but cuz the second part we cant atleast on python ver below 11
    embed.description = f"{iptext} | {cfswitchText if auto else ''}"
    print(f"[{stack()[0][3].upper()}] new ip {iptext} | {cfswitchText if auto else ''}")
    await channel.send(embed=embed)