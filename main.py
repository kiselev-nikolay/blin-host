import asyncio
import datetime
import json
from pathlib import Path

import requests
import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import (HTMLResponse, PlainTextResponse,
                                 RedirectResponse)

from blines import known_blins, named_blin

app = Starlette()
USERS = [
    "Zmeй",
    "akotkot",
    "Felstra",
    "utyurin",
    "asilkin",
    "airev",
    "nterehin",
    "nsidyakin",
    "mplakhin",
]
SCORE = {u: set() for u in USERS}

MAKER_URL = "https://maker.ifttt.com/trigger/kbranal/with/key/o_VFlM88mum6RmOKCm4WMLb7Pj6d7ZpvJIR2ryV2eYg?value1={}&value2={}&value3={}"
TOUCHES = 0

STORE_PATH = Path("./backups/")
STORE_PATH.mkdir(exist_ok=True)


def send(a, b="", c=""):
    print(c)
    requests.get(MAKER_URL.format(str(a) + "<br>", str(b) + "<br>", str(c)))


async def resnyci():
    global TOUCHES
    while True:
        await asyncio.sleep(60 * 120)
        mynum = len([i for i in STORE_PATH.iterdir()])
        jsonable = {k: list(v) for k, v in SCORE.items()}
        with open(STORE_PATH / f"{mynum}.json", "w") as file:
            json.dump(jsonable, file)
        ledrbrd = ""
        for user, em_score in SCORE.items():
            scoretable = []
            for k, v in known_blins.items():
                scoretable.append("=" if v in em_score else "-")
            ledrbrd += f"{''.join(scoretable)} {user}<br>"
        send(f"Touch ya: {TOUCHES}", "<code>" + ledrbrd + "</code>",
             json.dumps(jsonable))
        TOUCHES = 0


@app.on_event("startup")
async def startup():
    global SCORE
    mynum = len([i for i in STORE_PATH.iterdir()]) - 1
    if (STORE_PATH / f"{mynum}.json").exists():
        with open(STORE_PATH / f"{mynum}.json", "r") as file:
            last_backup = json.load(file)
        SCORE = {k: set(v) for k, v in last_backup.items()}
    asyncio.create_task(resnyci())


@app.route("/submit_blin", methods=['POST'])
async def submit_blin(request: Request):
    global TOUCHES
    TOUCHES += 1
    await asyncio.sleep(1)
    try:
        form = await request.form()
        if (form.get("user") is not None) and (form.get("blin") is not None):
            texttt = ""
            if SCORE.get(form.get("user")) is not None:
                if known_blins.get(form.get("blin")):
                    if known_blins.get(
                            form.get("blin")) in SCORE[form.get("user")]:
                        texttt = "Allready accepted."
                    else:
                        SCORE[form.get("user")].add(
                            known_blins.get(form.get("blin")))
                        texttt = "Accept."
                        mynum = len([i for i in STORE_PATH.iterdir()])
                        jsonable = {k: list(v) for k, v in SCORE.items()}
                        with open(STORE_PATH / f"{mynum}.json", "w") as file:
                            json.dump(jsonable, file)
                else:
                    texttt = "Declined."
            else:
                texttt = "User name is wrong."
            if ';' in (form.get("user", "") + form.get("blin", "")):
                texttt += "\nNice injection, honey\n"
                texttt += named_blin("drop")
            return PlainTextResponse(texttt)
        else:
            await asyncio.sleep(3)
            return PlainTextResponse("Declined.")
    except Exception:
        return PlainTextResponse("Declined.")


@app.route("/static/index.html")
async def index(request: Request):
    global TOUCHES
    TOUCHES += 1
    await asyncio.sleep(.45)
    with open('index.html') as file:
        html = file.read()
    html_score = []
    for k, v in sorted(SCORE.items(), key=lambda kv: -len(kv[1])):
        i = list(SCORE.keys()).index(k)
        i += 2
        html_score.append(
            f"<li class='list-item'><a href='?uid={i}'>{k} ({len(v)} flag)</li>"
        )
    html = html.replace("<!-- leaderboard -->", "".join(html_score))
    try:
        uid = request.query_params.get("uid")
        if uid is not None:
            uid = int(uid)
            user_info = '<h3 class="title is-3">User Score</h3>'
            if uid >= 2:
                uid = int(uid) - 2
                user_info += f"<p>{USERS[uid]}</p><br>"
                scoretable = []
                for k, v in known_blins.items():
                    scoretable.append("X" if v in
                                      SCORE[USERS[uid]] else "&middot;")
                user_info += f"<pre>{''.join(scoretable)}</pre>"
            else:
                user_info += ["admin", "user"][uid]
                if uid == 0:
                    user_info += "<br><blin>" + named_blin(
                        'jwt') + "</blin>"
        else:
            user_info = ""
    except Exception as e:
        print(e)
        user_info = ""
    html = html.replace("<!-- user -->", str(user_info))
    resp = HTMLResponse(html)
    resp.headers.append("ETag", 'W/"{}"'.format(named_blin('etagblin')))
    return resp


@app.route("/admin")
@app.route("/admin/")
async def admin(request):
    global TOUCHES
    TOUCHES += 1
    await asyncio.sleep(.2)
    with open('admin.html') as file:
        html = file.read()
    return HTMLResponse(html)


@app.route("/admin/panel.php", methods=["POST"])
async def adminpanel(request: Request):
    global TOUCHES
    TOUCHES += 1
    await asyncio.sleep(2)
    try:
        form_data = await request.form()
        if form_data['user'] == "user":
            return PlainTextResponse(named_blin('userlogin'))
    except Exception:
        pass
    return RedirectResponse("/")


@app.route("/static//")
async def pathfinder(request):
    global TOUCHES
    TOUCHES += 1
    await asyncio.sleep(.45)
    return PlainTextResponse(
        "You know how mafia works. {}".format(named_blin('pathfinder')), 200)


@app.route("/robots.txt")
@app.route("/static/robots.txt")
async def robotstxt(request):
    global TOUCHES
    TOUCHES += 1
    await asyncio.sleep(.14)
    return PlainTextResponse("Sitemap: /sitemap.xml\nI like: you", 200)


@app.route("/sitemap.xml")
@app.route("/static/sitemap.xml")
async def sitemap(request):
    global TOUCHES
    TOUCHES += 1
    await asyncio.sleep(.45)
    return PlainTextResponse(
        "Where there's a will there's a way. {}".format(named_blin('sitemap')),
        200)


@app.route("/static/main.py")
@app.route("/static/server.py")
async def pythonysta(request):
    global TOUCHES
    TOUCHES += 1
    await asyncio.sleep(.45)
    return PlainTextResponse(
        "432 Only blin found. {}".format(named_blin('pyhack')), 432)


@app.route("/static/{path:path}")
async def all_static(request):
    global TOUCHES
    TOUCHES += 1
    await asyncio.sleep(.45)
    return PlainTextResponse("404 Not Found...", 404)


@app.route("/")
async def root(request):
    global TOUCHES
    TOUCHES += 1
    await asyncio.sleep(.15)
    resp = RedirectResponse('/static/index.html')
    resp.headers.append("x-blin", named_blin("xblin"))
    return resp


@app.route("/{path:path}")
async def patherrorpip(request):
    global TOUCHES
    TOUCHES += 1
    await asyncio.sleep(2.5)
    return PlainTextResponse("404 Not Found.", 404)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)
