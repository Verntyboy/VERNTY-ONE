import json
import os
import base64
import hmac
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs, quote_plus, quote, urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from core.brain import chat, history, clear_history
from tools.agent_tools import (
    dns_lookup, http_headers, tls_check, nmap_scan,
    create_python_file, check_python_file
)

HOST = "0.0.0.0" if os.environ.get("VERNTY_CLOUD") == "1" else "127.0.0.1"
PORT = int(os.environ.get("PORT", "8080"))

PAGE = r"""<!doctype html>
<html>
<head>
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="theme-color" content="#07111f">
<title>VERNTY ONE 3.0</title>
<style>
*{box-sizing:border-box}
:root{--bg:#07090f;--cyan:#00e5ff;--text:#edf5ff;--muted:#8493a9;--border:rgba(0,229,255,.15)}
body{margin:0;min-height:100vh;color:var(--text);font-family:Inter,Arial,sans-serif;background:radial-gradient(ellipse at 50% -20%,#123451 0%,transparent 55%),#07090f}
header{position:sticky;top:0;z-index:10;padding:19px 22px;background:rgba(7,11,20,.96);backdrop-filter:blur(20px);border-bottom:1px solid var(--border)}
h2{margin:0;color:var(--cyan);font-size:25px;letter-spacing:3px;text-shadow:0 0 18px #00bfff66}
header small{display:block;margin-top:6px;color:var(--muted)}
main{max-width:1050px;margin:auto;padding:18px}
.panel{background:linear-gradient(145deg,#141d2b,#0d121d);border:1px solid var(--border);border-radius:20px;padding:19px;margin:15px 0;box-shadow:0 12px 35px #0006}
.panel>b{font-size:15px;letter-spacing:.5px}
small{color:var(--muted);line-height:1.6}
.modes{display:grid;grid-template-columns:repeat(5,1fr);gap:9px}
button{border:1px solid #263b53;background:#151f2e;color:var(--text);border-radius:12px;padding:13px 10px;font-weight:600;cursor:pointer;transition:.2s}
button:active{transform:scale(.97)}
button:hover{border-color:var(--cyan);background:#163047}
.mode.active{background:linear-gradient(135deg,#075c78,#123d69);border-color:var(--cyan);box-shadow:0 0 18px #00d9ff25}
#chat{height:43vh;min-height:280px;overflow:auto;display:flex;flex-direction:column;gap:13px;padding:15px 3px;scroll-behavior:smooth}
.msg{padding:14px 16px;border-radius:17px;white-space:pre-wrap;overflow-wrap:anywhere;line-height:1.65;font-size:14px}
.user{background:linear-gradient(135deg,#075b79,#174b80);border:1px solid #00d9ff55;align-self:flex-end;max-width:88%;border-bottom-right-radius:5px}
.bot{background:#192334;border:1px solid #ffffff12;align-self:flex-start;max-width:96%;border-bottom-left-radius:5px}
textarea,input{width:100%;background:#090f1a;color:white;border:1px solid #293d55;border-radius:13px;padding:14px;margin:8px 0;outline:none;font-size:14px}
textarea:focus,input:focus{border-color:var(--cyan);box-shadow:0 0 13px #00d9ff22}
textarea{min-height:90px;resize:vertical}
.actions{display:flex;gap:9px;flex-wrap:wrap;margin-top:10px}
.actions button{flex:1;min-width:110px}
.toolgrid{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
#toolout{white-space:pre-wrap;overflow-wrap:anywhere;color:#9eeeff;background:#080e18;padding:13px;border-radius:12px;font-size:13px}
.status{color:#68efad;padding:10px 0}
hr{border:0;border-top:1px solid var(--border)}
#voiceStatus{color:var(--cyan)}
@media(max-width:650px){header{padding:17px}h2{font-size:22px}main{padding:10px}.panel{padding:15px;border-radius:17px}.modes{grid-template-columns:repeat(2,1fr)}#chat{height:43vh}button{padding:13px 8px;font-size:12px}}



/* VERNTY ONE NEXUS DESIGN */
:root {
 --bg:#080710;
 --panel:#12101e;
 --panel2:#19152a;
 --purple:#a855f7;
 --violet:#7c3aed;
 --text:#f5f1ff;
 --muted:#9690aa;
 --border:rgba(168,85,247,.20);
}
*{box-sizing:border-box}
body{
 margin:0;min-height:100vh;color:var(--text);
 font-family:Inter,Arial,sans-serif;
 background:radial-gradient(ellipse at 70% 0%,#281044 0%,transparent 38%),#080710;
}
.app-shell{display:flex;min-height:100vh}
.sidebar{
 width:235px;flex-shrink:0;padding:25px 16px;
 background:#0d0b16;border-right:1px solid var(--border);
 display:flex;flex-direction:column;gap:12px;
}
.brand{display:flex;align-items:center;gap:12px;padding:8px 5px 30px}
.brand-mark{
 width:43px;height:43px;border-radius:14px;
 display:grid;place-items:center;font-size:22px;font-weight:900;
 background:linear-gradient(135deg,#a855f7,#5b21b6);
 box-shadow:0 0 25px #9333ea55;
}
.brand b{letter-spacing:2px;font-size:15px}
.brand small{display:block;color:var(--muted);font-size:10px;margin-top:5px}
.side-label,.eyebrow{
 color:#a78bfa;font-size:10px;font-weight:800;
 letter-spacing:2px;margin:12px 8px;
}
.nav-item{
 display:block;text-decoration:none;color:#aaa2bd;
 padding:13px 14px;border-radius:12px;font-size:13px;
 border:1px solid transparent;
}
.nav-item:hover,.nav-item:focus{
 background:#21152f;color:white;border-color:var(--border)
}
.sidebar-footer{
 margin-top:auto;padding:15px 10px;color:#aaa2bd;
 border-top:1px solid var(--border);font-size:12px
}
.status-dot{display:inline-block;width:8px;height:8px;
 background:#4ade80;border-radius:50%;margin-right:8px}
.main-area{flex:1;min-width:0}
header.topbar{
 position:relative;top:auto;padding:23px 30px;
 background:rgba(10,8,17,.85);border-bottom:1px solid var(--border);
 display:flex;justify-content:space-between;align-items:center;
 backdrop-filter:blur(18px)
}
.topbar h1{margin:5px 0 0;font-size:23px;letter-spacing:1px}
.topbar .eyebrow{margin:0}
.top-pill{
 border:1px solid var(--border);background:#191329;
 color:#c4a5fd;padding:9px 13px;border-radius:30px;font-size:11px
}
.dashboard{max-width:1500px;margin:auto;padding:25px}
.hero{
 min-height:165px;padding:27px 30px;border-radius:22px;
 background:linear-gradient(115deg,#24123d,#171126 65%,#29134a);
 border:1px solid #8b5cf655;display:flex;
 align-items:center;justify-content:space-between;overflow:hidden;
 position:relative;margin-bottom:22px;
}
.hero .eyebrow{margin:0 0 10px}
.hero h2{color:white!important;text-shadow:none!important;
 font-size:27px;margin:0 0 8px;letter-spacing:0}
.hero p{color:#b9adcc;font-size:13px;margin:0}
.hero-orb{
 width:105px;height:105px;flex-shrink:0;border-radius:50%;
 display:grid;place-items:center;font-size:38px;font-weight:900;
 color:white;background:linear-gradient(145deg,#a855f7,#4c1d95);
 box-shadow:0 0 55px #9333ea77;
}
.workspace-grid{
 display:grid;grid-template-columns:minmax(0,1.65fr) minmax(260px,.85fr);
 gap:20px;align-items:start
}
.primary-column,.secondary-column{min-width:0}
.panel{
 background:linear-gradient(145deg,#171326,#100e1b);
 border:1px solid var(--border);border-radius:18px;
 padding:19px;margin:0 0 18px;box-shadow:0 12px 35px #0005
}
.panel>b{font-size:14px;letter-spacing:.5px}
.modes{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:8px}
button{
 border:1px solid #39284e;background:#21182f;color:var(--text);
 border-radius:11px;padding:12px 10px;font-weight:600;
 cursor:pointer;transition:.2s
}
button:hover{border-color:var(--purple);background:#38204e}
button:active{transform:scale(.97)}
.mode.active{
 background:linear-gradient(135deg,#8b35d2,#5425a0);
 border-color:#c084fc;box-shadow:0 0 18px #a855f733
}
#chat{
 height:42vh;min-height:280px;overflow:auto;display:flex;
 flex-direction:column;gap:13px;padding:15px 3px;
 scroll-behavior:smooth
}
.msg{padding:14px 16px;border-radius:16px;white-space:pre-wrap;
 overflow-wrap:anywhere;line-height:1.65;font-size:14px}
.user{background:linear-gradient(135deg,#7135a8,#49227b);
 border:1px solid #c084fc55;align-self:flex-end;
 max-width:88%;border-bottom-right-radius:5px}
.bot{background:#211a30;border:1px solid #ffffff12;
 align-self:flex-start;max-width:96%;border-bottom-left-radius:5px}
textarea,input{
 width:100%;background:#0b0913;color:white;
 border:1px solid #39284e;border-radius:12px;
 padding:14px;margin:8px 0;outline:none;font-size:14px
}
textarea:focus,input:focus{border-color:var(--purple);box-shadow:0 0 13px #a855f722}
textarea{min-height:90px;resize:vertical}
.actions{display:flex;gap:9px;flex-wrap:wrap;margin-top:10px}
.actions button{flex:1;min-width:105px}
.toolgrid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:9px}
#toolout{
 white-space:pre-wrap;overflow-wrap:anywhere;color:#d8b4fe;
 background:#0b0913;padding:13px;border-radius:12px;font-size:13px
}
.status{color:#68efad;padding:10px 0}
hr{border:0;border-top:1px solid var(--border)}
#voiceStatus{color:#c084fc}
.secondary-column .panel{padding:17px}
@media(max-width:850px){
 .sidebar{width:185px}
 .workspace-grid{grid-template-columns:1fr}
}
@media(max-width:600px){
 .sidebar{width:65px;padding:15px 7px}
 .brand{justify-content:center;padding:5px 0 20px}
 .brand>div:last-child,.side-label,.nav-item span,.sidebar-footer{display:none}
 .nav-item{text-align:center;padding:13px 3px;font-size:18px}
 header.topbar{padding:17px}
 .topbar h1{font-size:18px}
 .dashboard{padding:13px}
 .hero{padding:21px;min-height:140px}
 .hero h2{font-size:21px}
 .hero-orb{width:65px;height:65px;font-size:26px}
 .modes{grid-template-columns:repeat(2,minmax(0,1fr))}
 .panel{padding:15px}
 #chat{height:42vh}
 button{font-size:12px;padding:12px 7px}
}



/* VERNTY ONE NEXUS DESIGN */
:root {
 --bg:#080710;
 --panel:#12101e;
 --panel2:#19152a;
 --purple:#a855f7;
 --violet:#7c3aed;
 --text:#f5f1ff;
 --muted:#9690aa;
 --border:rgba(168,85,247,.20);
}
*{box-sizing:border-box}
body{
 margin:0;min-height:100vh;color:var(--text);
 font-family:Inter,Arial,sans-serif;
 background:radial-gradient(ellipse at 70% 0%,#281044 0%,transparent 38%),#080710;
}
.app-shell{display:flex;min-height:100vh}
.sidebar{
 width:235px;flex-shrink:0;padding:25px 16px;
 background:#0d0b16;border-right:1px solid var(--border);
 display:flex;flex-direction:column;gap:12px;
}
.brand{display:flex;align-items:center;gap:12px;padding:8px 5px 30px}
.brand-mark{
 width:43px;height:43px;border-radius:14px;
 display:grid;place-items:center;font-size:22px;font-weight:900;
 background:linear-gradient(135deg,#a855f7,#5b21b6);
 box-shadow:0 0 25px #9333ea55;
}
.brand b{letter-spacing:2px;font-size:15px}
.brand small{display:block;color:var(--muted);font-size:10px;margin-top:5px}
.side-label,.eyebrow{
 color:#a78bfa;font-size:10px;font-weight:800;
 letter-spacing:2px;margin:12px 8px;
}
.nav-item{
 display:block;text-decoration:none;color:#aaa2bd;
 padding:13px 14px;border-radius:12px;font-size:13px;
 border:1px solid transparent;
}
.nav-item:hover,.nav-item:focus{
 background:#21152f;color:white;border-color:var(--border)
}
.sidebar-footer{
 margin-top:auto;padding:15px 10px;color:#aaa2bd;
 border-top:1px solid var(--border);font-size:12px
}
.status-dot{display:inline-block;width:8px;height:8px;
 background:#4ade80;border-radius:50%;margin-right:8px}
.main-area{flex:1;min-width:0}
header.topbar{
 position:relative;top:auto;padding:23px 30px;
 background:rgba(10,8,17,.85);border-bottom:1px solid var(--border);
 display:flex;justify-content:space-between;align-items:center;
 backdrop-filter:blur(18px)
}
.topbar h1{margin:5px 0 0;font-size:23px;letter-spacing:1px}
.topbar .eyebrow{margin:0}
.top-pill{
 border:1px solid var(--border);background:#191329;
 color:#c4a5fd;padding:9px 13px;border-radius:30px;font-size:11px
}
.dashboard{max-width:1500px;margin:auto;padding:25px}
.hero{
 min-height:165px;padding:27px 30px;border-radius:22px;
 background:linear-gradient(115deg,#24123d,#171126 65%,#29134a);
 border:1px solid #8b5cf655;display:flex;
 align-items:center;justify-content:space-between;overflow:hidden;
 position:relative;margin-bottom:22px;
}
.hero .eyebrow{margin:0 0 10px}
.hero h2{color:white!important;text-shadow:none!important;
 font-size:27px;margin:0 0 8px;letter-spacing:0}
.hero p{color:#b9adcc;font-size:13px;margin:0}
.hero-orb{
 width:105px;height:105px;flex-shrink:0;border-radius:50%;
 display:grid;place-items:center;font-size:38px;font-weight:900;
 color:white;background:linear-gradient(145deg,#a855f7,#4c1d95);
 box-shadow:0 0 55px #9333ea77;
}
.workspace-grid{
 display:grid;grid-template-columns:minmax(0,1.65fr) minmax(260px,.85fr);
 gap:20px;align-items:start
}
.primary-column,.secondary-column{min-width:0}
.panel{
 background:linear-gradient(145deg,#171326,#100e1b);
 border:1px solid var(--border);border-radius:18px;
 padding:19px;margin:0 0 18px;box-shadow:0 12px 35px #0005
}
.panel>b{font-size:14px;letter-spacing:.5px}
.modes{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:8px}
button{
 border:1px solid #39284e;background:#21182f;color:var(--text);
 border-radius:11px;padding:12px 10px;font-weight:600;
 cursor:pointer;transition:.2s
}
button:hover{border-color:var(--purple);background:#38204e}
button:active{transform:scale(.97)}
.mode.active{
 background:linear-gradient(135deg,#8b35d2,#5425a0);
 border-color:#c084fc;box-shadow:0 0 18px #a855f733
}
#chat{
 height:42vh;min-height:280px;overflow:auto;display:flex;
 flex-direction:column;gap:13px;padding:15px 3px;
 scroll-behavior:smooth
}
.msg{padding:14px 16px;border-radius:16px;white-space:pre-wrap;
 overflow-wrap:anywhere;line-height:1.65;font-size:14px}
.user{background:linear-gradient(135deg,#7135a8,#49227b);
 border:1px solid #c084fc55;align-self:flex-end;
 max-width:88%;border-bottom-right-radius:5px}
.bot{background:#211a30;border:1px solid #ffffff12;
 align-self:flex-start;max-width:96%;border-bottom-left-radius:5px}
textarea,input{
 width:100%;background:#0b0913;color:white;
 border:1px solid #39284e;border-radius:12px;
 padding:14px;margin:8px 0;outline:none;font-size:14px
}
textarea:focus,input:focus{border-color:var(--purple);box-shadow:0 0 13px #a855f722}
textarea{min-height:90px;resize:vertical}
.actions{display:flex;gap:9px;flex-wrap:wrap;margin-top:10px}
.actions button{flex:1;min-width:105px}
.toolgrid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:9px}
#toolout{
 white-space:pre-wrap;overflow-wrap:anywhere;color:#d8b4fe;
 background:#0b0913;padding:13px;border-radius:12px;font-size:13px
}
.status{color:#68efad;padding:10px 0}
hr{border:0;border-top:1px solid var(--border)}
#voiceStatus{color:#c084fc}
.secondary-column .panel{padding:17px}
@media(max-width:850px){
 .sidebar{width:185px}
 .workspace-grid{grid-template-columns:1fr}
}
@media(max-width:600px){
 .sidebar{width:65px;padding:15px 7px}
 .brand{justify-content:center;padding:5px 0 20px}
 .brand>div:last-child,.side-label,.nav-item span,.sidebar-footer{display:none}
 .nav-item{text-align:center;padding:13px 3px;font-size:18px}
 header.topbar{padding:17px}
 .topbar h1{font-size:18px}
 .dashboard{padding:13px}
 .hero{padding:21px;min-height:140px}
 .hero h2{font-size:21px}
 .hero-orb{width:65px;height:65px;font-size:26px}
 .modes{grid-template-columns:repeat(2,minmax(0,1fr))}
 .panel{padding:15px}
 #chat{height:42vh}
 button{font-size:12px;padding:12px 7px}
}



/* VERNTY ONE AI CORE */
body {
 background:radial-gradient(ellipse at 50% 0%,#24103e 0%,#0b0815 48%,#07060c 100%);
 color:#f8f4ff;
}
.ai-shell {max-width:1150px;margin:auto;padding:25px 18px}
header.topbar {
 position:relative;top:auto;text-align:center;
 justify-content:center;padding:22px;
 background:transparent;border:0;
}
.topbar h1 {font-size:24px;letter-spacing:4px}
.top-pill {display:none}
.topbar .eyebrow {text-align:center}
.ai-hero {
 text-align:center;padding:15px 10px 25px;
}
.ai-orb {
 width:125px;height:125px;margin:5px auto 20px;
 border-radius:50%;display:grid;place-items:center;
 background:radial-gradient(circle at 35% 30%,#e9d5ff,#a855f7 35%,#4c1d95 75%,#170b2b);
 border:2px solid #d8b4fe;
 box-shadow:0 0 20px #a855f7,0 0 55px #7e22ce88,inset 0 0 25px #fff5;
 animation:orbPulse 3s ease-in-out infinite;
 color:white;font-size:38px;font-weight:900;
}
@keyframes orbPulse {
 0%,100%{transform:scale(1);box-shadow:0 0 20px #a855f7,0 0 45px #7e22ce66}
 50%{transform:scale(1.06);box-shadow:0 0 35px #c084fc,0 0 75px #9333ea99}
}
.ai-hero h2 {font-size:25px;margin:0 0 8px;color:white;letter-spacing:1px}
.ai-hero p {color:#a99abf;font-size:13px;margin:0}
.ai-state {
 display:inline-flex;align-items:center;gap:8px;
 padding:8px 15px;border:1px solid #7135a866;
 border-radius:30px;background:#1b1029;
 color:#d8b4fe;font-size:11px;margin-top:17px;
}
.ai-state i {
 width:7px;height:7px;background:#4ade80;
 border-radius:50%;box-shadow:0 0 10px #4ade80;
}
.ai-panel {
 background:linear-gradient(145deg,#171126,#100c1b);
 border:1px solid #7135a844;border-radius:22px;
 padding:20px;margin-bottom:17px;
 box-shadow:0 15px 50px #0006;
}
.ai-panel-title {
 display:flex;align-items:center;justify-content:space-between;
 gap:10px;margin-bottom:13px;
}
.ai-panel-title b {font-size:14px;letter-spacing:1px}
.modes {
 display:flex;gap:8px;overflow-x:auto;padding:3px 1px 8px;
}
.mode {flex:1;min-width:95px;white-space:nowrap}
.mode.active {
 background:linear-gradient(135deg,#a855f7,#6425a4);
 border-color:#d8b4fe;
 box-shadow:0 0 18px #9333ea44;
}
#chat {
 height:45vh;min-height:300px;max-height:570px;
 overflow-y:auto;display:flex;flex-direction:column;
 gap:14px;padding:15px 3px;scroll-behavior:smooth;
}
.msg {
 padding:14px 17px;border-radius:17px;
 white-space:pre-wrap;overflow-wrap:anywhere;
 line-height:1.7;font-size:14px;
}
.user {
 background:linear-gradient(135deg,#7836b2,#492276);
 border:1px solid #c084fc55;align-self:flex-end;
 max-width:88%;border-bottom-right-radius:5px;
}
.bot {
 background:#21182f;border:1px solid #ffffff12;
 align-self:flex-start;max-width:96%;
 border-bottom-left-radius:5px;
}
textarea#message {
 min-height:75px;max-height:180px;resize:vertical;
 background:#0b0813;border:1px solid #54346e;
 border-radius:15px;padding:15px;color:white;
}
textarea#message:focus {
 border-color:#c084fc;box-shadow:0 0 18px #a855f733;
}
.actions {display:flex;gap:9px;flex-wrap:wrap;margin-top:10px}
.actions button {
 flex:1;min-width:100px;background:#251735;
 border:1px solid #583477;
}
.actions button:first-child {
 background:linear-gradient(135deg,#9333ea,#6425a4);
 border-color:#c084fc;
}
.actions button:hover {filter:brightness(1.2)}
#voiceStatus {color:#c4a5fd;font-size:12px}
#status {
 color:#86efac;font-size:12px;text-align:center;
 padding:12px;
}
.ai-footer {
 text-align:center;color:#746985;font-size:10px;
 letter-spacing:2px;padding:12px;
}
@media(max-width:600px) {
 .ai-shell{padding:10px}
 header.topbar{padding:14px 5px}
 .topbar h1{font-size:20px}
 .ai-orb{width:105px;height:105px;font-size:32px}
 .ai-hero h2{font-size:21px}
 .ai-panel{padding:14px;border-radius:17px}
 #chat{height:43vh;min-height:270px}
 .mode{min-width:105px}
 button{font-size:12px;padding:12px 8px}
}


/* VERNTY ONE LIVING AI CORE */
.ai-orb.thinking{
 animation:orbThink .75s ease-in-out infinite;
}
.ai-orb.speaking{
 animation:orbSpeak .5s ease-in-out infinite;
}
.ai-orb.listening{
 animation:orbListen 1s ease-in-out infinite;
}
@keyframes orbThink{
 0%,100%{transform:scale(1);filter:brightness(1)}
 50%{transform:scale(1.12);filter:brightness(1.6)}
}
@keyframes orbSpeak{
 0%,100%{transform:scale(1);box-shadow:0 0 25px #a855f7,0 0 50px #9333ea}
 50%{transform:scale(1.09);box-shadow:0 0 45px #e9d5ff,0 0 90px #a855f7}
}
@keyframes orbListen{
 0%,100%{transform:scale(1);filter:hue-rotate(0deg)}
 50%{transform:scale(1.08);filter:hue-rotate(35deg) brightness(1.4)}
}

/* VERNTY IMAGE STUDIO */
.image-studio textarea {
 min-height:105px;resize:vertical;
 background:#090f1a;color:white;
 border:1px solid #293d55;border-radius:13px;
 padding:14px;width:100%;margin:8px 0;
}
.image-options {
 display:grid;grid-template-columns:1fr 1fr;gap:10px;
}
.image-options label {
 display:block;color:var(--muted);font-size:12px;
}
.image-options select {
 width:100%;padding:12px;margin-top:6px;
 border-radius:10px;background:#090f1a;
 border:1px solid #293d55;color:white;
}
.image-studio button {
 width:100%;margin-top:12px;
 background:linear-gradient(135deg,#075c78,#123d69);
 border:1px solid var(--cyan);
}
#imageStatus {
 color:var(--muted);font-size:12px;
 margin:12px 0;overflow-wrap:anywhere;
}
#imagePreview {
 display:none;width:100%;height:auto;
 max-height:650px;object-fit:contain;
 border-radius:14px;border:1px solid var(--border);
 margin-top:12px;background:#090f1a;
}
#downloadImage {
 display:none;text-align:center;margin-top:12px;
 color:var(--cyan);font-weight:bold;
}
@media(max-width:420px) {
 .image-options{grid-template-columns:1fr}
}

</style>

<link rel="manifest" href="/manifest.json">
<link rel="icon" href="/icon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/icon.svg">
</head>
<body>
<div class="ai-shell">
<header class="topbar">
 <div>
  <div class="eyebrow">PERSONAL ARTIFICIAL INTELLIGENCE</div>
  <h1>⚡ VERNTY ONE</h1>
 </div>
</header>

<section class="ai-hero">
 <div class="ai-orb">V</div>
 <h2>Your AI. Your Intelligence.</h2>
 <p>Think • Create • Learn • Build</p>
 <div class="ai-state"><i></i> VERNTY AI CORE</div>
</section>

<section class="ai-panel" id="agents">
 <div class="ai-panel-title">
  <b>CHOOSE INTELLIGENCE MODE</b>
  <small>AI MODES</small>
 </div>
 <div class="modes">
  <button class="mode active" data-mode="general">🤖 General</button>
  <button class="mode" data-mode="code">💻 Developer</button>
  <button class="mode" data-mode="security">🛡️ Security</button>
  <button class="mode" data-mode="creator">🎬 Creator</button>
  <button class="mode" data-mode="research">🔎 Researcher</button>
 </div>
</section>

<section class="ai-panel" id="conversation">
 <div class="ai-panel-title">
  <b>◉ CONVERSATION</b>
  <button onclick="clearChat()">Clear chat</button>
 </div>
 <div id="chat"></div>
 <textarea id="message" placeholder="Talk to VERNTY ONE..."></textarea>
 <div class="actions">
  <button onclick="send()">➤ Send message</button>
  <button onclick="listen()">🎙️ Speak</button>
  <button onclick="stopVoice()">■ Stop voice</button>
  <button onclick="readLast()">🔊 Read reply</button>
 </div>
 <p id="voiceStatus">Voice assistant ready to use.</p>
</section>


<section class="ai-panel image-studio" id="image-studio">
 <div class="ai-panel-title">
  <b>🎨 VERNTY IMAGE STUDIO</b>
  <small>AI IMAGE GENERATOR</small>
 </div>

 <p><small>Describe the image you want VERNTY to create.</small></p>

 <textarea id="imagePrompt"
  maxlength="1200"
  placeholder="Example: A futuristic African city at sunset, cinematic lighting, ultra detailed..."></textarea>

 <div class="image-options">
  <label>Image style
   <select id="imageStyle">
    <option>Photorealistic</option>
    <option>Cinematic</option>
    <option>Anime</option>
    <option>Digital art</option>
    <option>3D</option>
   </select>
  </label>

  <label>Aspect ratio
   <select id="imageRatio">
    <option value="1:1">Square (1:1)</option>
    <option value="16:9">Landscape (16:9)</option>
    <option value="9:16">Portrait (9:16)</option>
   </select>
  </label>
 </div>

 <button id="generateImageButton" onclick="generateImage()">
  ✨ Generate image
 </button>

 <p id="imageStatus">Ready to create.</p>

 <img id="imagePreview" alt="Your generated image">

 <a id="downloadImage" href="#" download="vernty-image.png">
  ⬇ Download generated image
 </a>
</section>

<section class="ai-panel">
 <div class="ai-panel-title">
  <b>◈ SYSTEM CONNECTION</b>
 </div>
 <div id="status">Checking AI connection...</div>
</section>

<div class="ai-footer">VERNTY ONE 3.0 · BUILT FOR INTELLIGENCE</div>
</div>
<script>
let mode="general";
let lastReply="";
const chatbox=document.getElementById("chat");
function add(role,text){
 const d=document.createElement("div");
 d.className="msg "+(role==="user"?"user":"bot");
 d.textContent=text;
 chatbox.appendChild(d);chatbox.scrollTop=chatbox.scrollHeight;
}
document.querySelectorAll(".mode").forEach(b=>{
 b.onclick=()=>{
  mode=b.dataset.mode;
  document.querySelectorAll(".mode").forEach(x=>x.classList.remove("active"));
  b.classList.add("active");
  document.getElementById("message").placeholder="Message "+mode+" agent...";
 };
});
function setOrbState(state){
 const orb=document.querySelector(".ai-orb");
 if(!orb)return;
 orb.classList.remove("thinking","speaking","listening");
 if(state && state!=="idle")orb.classList.add(state);
}
async function send(){
 const box=document.getElementById("message");
 const text=box.value.trim();
 if(!text)return;

 setOrbState("thinking");
 box.value="";
 add("user",text);

 const prefix={general:"",code:"/code ",security:"/security ",creator:"/creator ",research:"/research "}[mode] || "";
 add("bot","VERNTY ONE is thinking...");
 const pending=chatbox.lastChild;

 try{
  const r=await fetch("/api/chat",{
   method:"POST",
   headers:{"Content-Type":"application/json"},
   body:JSON.stringify({message:prefix+text})
  });

  const raw=await r.text();
  let data;

  try{
   data=JSON.parse(raw);
  }catch(parseError){
   throw new Error("Invalid server response: "+raw.slice(0,200));
  }

  if(!r.ok)throw new Error("Server HTTP "+r.status+": "+(data.error||raw));

  pending.textContent=data.reply||data.error||"No response from AI.";
  lastReply=pending.textContent;
  setOrbState("idle");

  try{readLast();}catch(voiceError){console.log("Voice error:",voiceError);}

 }catch(e){
  pending.textContent="Chat error: "+e.message;
  setOrbState("idle");
  console.log("VERNTY chat error:",e);
 }

 chatbox.scrollTop=chatbox.scrollHeight;
}
document.getElementById("message").addEventListener("keydown",e=>{
 if(e.key==="Enter"&&!e.shiftKey){e.preventDefault();send();}
});
async function callTool(action,extra={}){
 const target=document.getElementById("target").value.trim();
 document.getElementById("toolout").textContent="Running "+action+"...";
 try{
  const r=await fetch("/api/tool",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({action,target,...extra})});
  const data=await r.json();
  document.getElementById("toolout").textContent=data.result||data.error||"No result";
 }catch(e){document.getElementById("toolout").textContent="Tool error: "+e;}
}
function tool(action){if(!document.getElementById("target").value.trim()){alert("Enter a hostname first.");return;}callTool(action);}
function scan(){
 if(!document.getElementById("target").value.trim()){alert("Enter a hostname first.");return;}
 if(confirm("Confirm you own this system or have explicit permission to scan it?"))callTool("nmap",{authorized:true});
}
function createFile(){
 callTool("create_python",{filename:document.getElementById("filename").value,code:document.getElementById("source").value});
}
function checkFile(){callTool("check_python",{filename:document.getElementById("filename").value});}
function searchWeb(){
 const q=document.getElementById("searchq").value.trim();
 if(q)window.open("https://html.duckduckgo.com/html/?q="+encodeURIComponent(q),"_blank");
}
async function clearChat(){
 if(!confirm("Start a new chat? This permanently deletes saved conversations."))return;
 try{
  const r=await fetch("/api/clear",{method:"POST"});
  const data=await r.json();
  if(!r.ok || !data.ok)throw new Error(data.error||"Could not clear chat");
  chatbox.innerHTML="";
  lastReply="";
  setOrbState("idle");
 }catch(e){alert("New chat failed: "+e.message);}
}
function readLast(){
 if(!lastReply){alert("There is no reply to read yet.");return;}
 if(!("speechSynthesis" in window)){setOrbState("idle");alert("Speech output is not supported in this browser.");return;}
 speechSynthesis.cancel();
 const u=new SpeechSynthesisUtterance(lastReply);
 u.onstart=()=>setOrbState("speaking");
 u.onend=()=>setOrbState("idle");
 u.onerror=()=>setOrbState("idle");
 u.lang="en-US";speechSynthesis.speak(u);
}
function stopVoice(){if("speechSynthesis" in window)speechSynthesis.cancel();setOrbState("idle");}
function listen(){
 const SR=window.SpeechRecognition||window.webkitSpeechRecognition;
 if(!SR){document.getElementById("voiceStatus").textContent="Speech recognition is not supported here. Try Chrome.";return;}
 const rec=new SR();rec.lang="en-US";rec.interimResults=false;rec.maxAlternatives=1;
 rec.onstart=()=>{setOrbState("listening");document.getElementById("voiceStatus").textContent="Listening...";};
 rec.onresult=e=>{document.getElementById("message").value=e.results[0][0].transcript;document.getElementById("voiceStatus").textContent="Speech captured. Press Send.";};
 rec.onerror=e=>{setOrbState("idle");document.getElementById("voiceStatus").textContent="Voice error: "+e.error;};
 rec.onend=()=>setOrbState("idle");
 rec.start();
}

async function generateImage(){
 const prompt=document.getElementById("imagePrompt").value.trim();
 const status=document.getElementById("imageStatus");
 const button=document.getElementById("generateImageButton");
 const preview=document.getElementById("imagePreview");
 const download=document.getElementById("downloadImage");

 if(!prompt){
  status.textContent="Please describe the image first.";
  return;
 }

 button.disabled=true;
 button.textContent="⏳ Creating image...";
 status.textContent="Connecting to VERNTY IMAGE STUDIO...";
 preview.style.display="none";
 download.style.display="none";

 try{
  const response=await fetch("/api/image",{
   method:"POST",
   headers:{"Content-Type":"application/json"},
   body:JSON.stringify({
    prompt:prompt,
    style:document.getElementById("imageStyle").value,
    ratio:document.getElementById("imageRatio").value
   })
  });

  const data=await response.json();
  if(!response.ok)throw new Error(data.error||"Image generation failed.");
  if(!data.image)throw new Error("No image was returned.");

  preview.src=data.image;
  preview.style.display="block";
  download.href=data.image;
  download.download="vernty-image."+
   (data.mime==="image/png"?"png":
    data.mime==="image/webp"?"webp":"jpg");
  download.style.display="block";
  status.textContent="Image created successfully.";
 }catch(error){
  status.textContent="Image generation failed: "+error.message;
 }finally{
  button.disabled=false;
  button.textContent="✨ Generate image";
 }
}


async function init(){
 try{
  const r=await fetch("/api/history");const data=await r.json();
  (data.messages||[]).forEach(m=>add(m.role,m.content));
  document.getElementById("status").textContent="Dashboard online • local server active";
 }catch(e){document.getElementById("status").textContent="Could not load status";}
}
init();
</script>

<script>
if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("/sw.js", {scope: "/"})
      .catch(err => console.log("PWA registration:", err));
  });
}
</script>
</body>
</html>"""


MANIFEST = r"""{
  "id": "/",
  "name": "VERNTY ONE AI",
  "short_name": "VERNTY ONE",
  "description": "Your personal AI assistant",
  "start_url": "/?source=pwa",
  "scope": "/",
  "display": "standalone",
  "orientation": "portrait",
  "background_color": "#100c1b",
  "theme_color": "#100c1b",
  "icons": [
    {
      "src": "/icon.svg",
      "sizes": "any",
      "type": "image/svg+xml",
      "purpose": "any"
    }
  ]
}"""

ICON = r"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
<defs>
 <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="#d8b4fe"/>
  <stop offset="1" stop-color="#7e22ce"/>
 </linearGradient>
 <filter id="glow"><feGaussianBlur stdDeviation="12"/></filter>
</defs>
<rect width="512" height="512" rx="112" fill="#100c1b"/>
<circle cx="256" cy="256" r="166" fill="#9333ea" opacity=".35" filter="url(#glow)"/>
<circle cx="256" cy="256" r="150" fill="url(#g)"/>
<circle cx="256" cy="256" r="128" fill="#171027"/>
<path d="M160 350V162h42l108 126V162h42v188h-40L202 220v130z" fill="#fff"/>
<circle cx="256" cy="256" r="190" fill="none" stroke="#c084fc" stroke-width="5" opacity=".7"/>
</svg>"""

SERVICE_WORKER = r"""
const CACHE = "vernty-one-shell-v1";
const SHELL = ["/", "/icon.svg", "/manifest.json"];

self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE).then(cache => cache.addAll(SHELL))
  );
  self.skipWaiting();
});

self.addEventListener("activate", event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener("fetch", event => {
  const req = event.request;
  const url = new URL(req.url);

  if (req.method !== "GET" ||
      url.origin !== self.location.origin ||
      url.pathname.startsWith("/api/")) return;

  if (req.mode === "navigate") {
    event.respondWith(
      fetch(req).then(response => {
        if (response.ok) {
          const copy = response.clone();
          caches.open(CACHE).then(cache => cache.put("/", copy));
        }
        return response;
      }).catch(() => caches.match("/"))
    );
    return;
  }

  event.respondWith(
    caches.match(req).then(cached =>
      cached || fetch(req).then(response => {
        if (response.ok) {
          const copy = response.clone();
          caches.open(CACHE).then(cache => cache.put(req, copy));
        }
        return response;
      })
    )
  );
});
"""



def generate_image(prompt, style="Photorealistic", ratio="1:1"):
    api_key = os.environ.get("CLOUDFLARE_API_TOKEN", "").strip()
    account_id = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "").strip()

    if not api_key or not account_id:
        raise RuntimeError(
            "Cloudflare image AI is not configured. "
            "Check CLOUDFLARE_API_TOKEN and CLOUDFLARE_ACCOUNT_ID "
            "in your server environment."
        )

    prompt = str(prompt).strip()
    if not prompt:
        raise ValueError("Please enter an image description.")
    if len(prompt) > 1200:
        raise ValueError("Image description must be 1200 characters or less.")

    styles = {
        "Photorealistic": "Photorealistic, highly detailed photography",
        "Cinematic": "Cinematic lighting, dramatic composition, film still",
        "Anime": "High quality anime illustration",
        "Digital art": "Professional digital artwork, detailed illustration",
        "3D": "High quality 3D render, detailed materials and lighting",
    }

    dimensions = {
        "1:1": (1024, 1024),
        "16:9": (1280, 720),
        "9:16": (720, 1280),
    }

    if style not in styles:
        raise ValueError("Please choose a supported image style.")
    if ratio not in dimensions:
        raise ValueError("Please choose a supported image format.")

    width, height = dimensions[ratio]
    full_prompt = styles[style] + ". " + prompt

    url = (
        "https://api.cloudflare.com/client/v4/accounts/"
        + account_id
        + "/ai/run/@cf/black-forest-labs/flux-1-schnell"
    )

    payload = json.dumps({
        "prompt": full_prompt,
        "width": width,
        "height": height,
    }).encode("utf-8")

    request = Request(
        url,
        data=payload,
        headers={
            "Authorization": "Bearer " + api_key,
            "Content-Type": "application/json",
            "Accept": "application/json, image/*",
            "User-Agent": "VERNTY-ONE/3.0",
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=180) as response:
            content_type = response.headers.get(
                "Content-Type", ""
            ).split(";")[0].strip().lower()

            response_bytes = response.read(16 * 1024 * 1024 + 1)

        if len(response_bytes) > 16 * 1024 * 1024:
            raise RuntimeError("Cloudflare returned an image that is too large.")

        if content_type.startswith("image/"):
            image_bytes = response_bytes
            mime = content_type
        else:
            result_data = json.loads(response_bytes.decode("utf-8"))
            result = result_data.get("result") or {}

            if not result_data.get("success", True):
                errors = result_data.get("errors") or []
                detail = errors[0].get("message", "") if errors else ""
                raise RuntimeError(
                    "Cloudflare image generation failed. "
                    + (str(detail)[:300] if detail else "Check your Cloudflare settings.")
                )

            encoded = result.get("image") if isinstance(result, dict) else result

            if not encoded:
                raise RuntimeError("Cloudflare did not return an image.")

            if encoded.startswith("data:"):
                mime = encoded.split(";", 1)[0].split(":", 1)[1]
                encoded = encoded.split(",", 1)[1]
            else:
                mime = "image/png"

            image_bytes = base64.b64decode(encoded, validate=True)

        if not image_bytes:
            raise RuntimeError("Cloudflare returned an empty image.")

        if len(image_bytes) > 8 * 1024 * 1024:
            raise RuntimeError("Generated image is too large to display.")

        return {
            "image": "data:" + mime + ";base64,"
                     + base64.b64encode(image_bytes).decode("ascii"),
            "mime": mime,
        }

    except HTTPError as exc:
        if exc.code in (401, 403):
            raise RuntimeError(
                "Cloudflare rejected the API token. Check its Workers AI permissions."
            ) from None

        raise RuntimeError(
            "Cloudflare returned HTTP " + str(exc.code)
            + ". Check your account, permissions and AI availability."
        ) from None

    except URLError:
        raise RuntimeError(
            "Could not connect to Cloudflare. Check your server connection."
        ) from None

    except (ValueError, KeyError, TypeError):
        raise RuntimeError(
            "Cloudflare returned an invalid image response."
        ) from None

class Handler(BaseHTTPRequestHandler):
    def send_json(self, data, status=200):
        raw = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(raw)

    def send_asset(self, body, content_type):
        raw = body.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-cache")
        if content_type == "application/javascript; charset=utf-8":
            self.send_header("Service-Worker-Allowed", "/")
        self.end_headers()
        self.wfile.write(raw)


    def authorized(self):
        if os.environ.get("VERNTY_CLOUD") != "1":
            return True

        username = os.environ.get("VERNTY_USERNAME", "")
        password = os.environ.get("VERNTY_PASSWORD", "")

        if not username or not password:
            self.send_json({"error": "Cloud login is not configured"}, 503)
            return False

        header = self.headers.get("Authorization", "")
        try:
            if header.startswith("Basic "):
                decoded = base64.b64decode(header[6:]).decode("utf-8")
                supplied_user, supplied_password = decoded.split(":", 1)

                if (hmac.compare_digest(supplied_user, username)
                    and hmac.compare_digest(supplied_password, password)):
                    return True
        except Exception:
            pass

        self.send_response(401)
        self.send_header(
            "WWW-Authenticate",
            'Basic realm="VERNTY ONE", charset="UTF-8"'
        )
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        return False

    def do_GET(self):
        path = urlparse(self.path).path
        if path != "/api/health" and not self.authorized():
            return
        if path == "/manifest.json":
            self.send_asset(MANIFEST, "application/manifest+json; charset=utf-8")
        elif path == "/sw.js":
            self.send_asset(SERVICE_WORKER, "application/javascript; charset=utf-8")
        elif path == "/icon.svg":
            self.send_asset(ICON, "image/svg+xml")
        elif path == "/":
            raw = PAGE.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)
        elif path == "/api/history":
            self.send_json({"messages": history(60)})
        elif path == "/api/health":
            self.send_json({"ok": True, "app": "VERNTY ONE 3.0"})
        else:
            self.send_json({"error": "Not found"}, 404)

    def do_POST(self):
        if not self.authorized():
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length > 30000:
                self.send_json({"error": "Request too large"}, 413)
                return
            data = json.loads(self.rfile.read(length).decode("utf-8"))
            path = urlparse(self.path).path

            if path == "/api/clear":
                clear_history()
                self.send_json({"ok": True})
                return

            if path == "/api/chat":
                reply = chat(data.get("message", ""))
                self.send_json({"reply": reply})
                return

            if path == "/api/image":
                result = generate_image(
                    data.get("prompt", ""),
                    data.get("style", "Photorealistic"),
                    data.get("ratio", "1:1"),
                )
                self.send_json(result)
                return

            if path == "/api/tool" and os.environ.get("VERNTY_CLOUD") != "1":
                action = data.get("action", "")
                target = data.get("target", "")
                if action == "dns":
                    result = dns_lookup(target)
                elif action == "headers":
                    result = http_headers(target)
                elif action == "tls":
                    result = tls_check(target)
                elif action == "nmap":
                    result = nmap_scan(target, authorized=(data.get("authorized") is True))
                elif action == "create_python":
                    result = create_python_file(data.get("filename", ""), data.get("code", ""))
                elif action == "check_python":
                    result = check_python_file(data.get("filename", ""))
                else:
                    self.send_json({"error": "Unknown tool"}, 400)
                    return
                self.send_json({"result": result})
                return

            self.send_json({"error": "Not found"}, 404)
        except Exception as e:
            self.send_json({"error": str(e)}, 500)

    def log_message(self, fmt, *args):
        print("[VERNTY REQUEST]", fmt % args)

if __name__ == "__main__":
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"VERNTY ONE 3.0 running on {HOST}:{PORT}")
    print("Press CTRL+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nVERNTY ONE stopped.")
        server.server_close()
