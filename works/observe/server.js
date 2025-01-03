const express = require('express');
const app = express();
const http = require('http');
const WebSocket = require('ws');
const wss = new WebSocket.Server({ noServer: true });
const host = "192.168.1.6";//enter your ip
const port = 8000;//enter port you like
const server = http.createServer(app);

const fs = require('fs');
const path = require('path');
const txt = path.join(__dirname, "log.json");

const axios = require('axios');
const {JSDOM} = require('jsdom');

async function fetchTitle(url) {
    //console.log('from fetchTitle');
    try {
        const response = await axios.get(url);
        const html = response.data;
        const dom = new JSDOM(html);
        const title = dom.window.document.querySelector('title');
        //console.log(title.textContent);
        return title.textContent;
    } catch (error) {
        throw error;
    }
}

function sysLog(content) {
    //console.log("sysLog");
    let log = fs.readFileSync(txt, 'utf8');
    //console.log(log.length);
    if(log.length == 0) log = JSON.stringify([]);
    log = JSON.parse(log);
    log.unshift(content);
    log = JSON.stringify(log);
    fs.writeFileSync(txt, log, "utf8");
}

function send(data) {
    /*for(let i=0;i<clients.length;i++) {
        clients[i].send(data);
    }*/
    const keys = Object.keys(clients);
    keys.forEach((key) => {
        clients[key].send(data);
    });
}

let ids = 0;
let clients = {};

// WebSocket接続の処理
wss.on('connection', (ws) => {
    console.log('new client connected!');
    ids++;    
    const id = ids;    
    ws[id] = ids;
    clients[id] = ws;

    ws.on('close', () => {
        delete clients[id];
        console.log(`a client ${id} has left. there are ${Object.keys(clients)} clients now.`);
    });

    // クライアントからのメッセージ受信
    ws.on('message', (message) => {
        console.log(`受信したメッセージ: ${message}`);

        const data = JSON.parse(message);
        switch(data.type) {
            case "log": 
                const exe = (async () => {
                    console.log('from exe');
                    /*fetchTitle(data.detail)
                    .then(title => {
                        data.label = title;
                         sysLog(data);
                        send(JSON.stringify({type: "list", detail: fs.readFileSync('log.json','utf8')}));
                    })
                    .catch(error => {
                        console.log(`error: ${error}`);
                        data.label = data.detail;
                        sysLog(data);
                    });*/

                    try {
                        const title = await fetchTitle(data.detail);
                        data.label = title;
                    } catch(error) {
                        console.log("title can't be gotten.");
                        data.label = data.detail;
                    }

                    sysLog(data);
                    send(JSON.stringify({type: "list", detail: fs.readFileSync('log.json','utf8')}));
                })();
                break;

            case "event": 
                sysLog(data);
                send(JSON.stringify(data));
                send(JSON.stringify({type: "list", detail: fs.readFileSync('log.json','utf8')}));
                break;

            case "request": 
                /*switch(data.label) {
                    case "log": ws.send(JSON.stringify({type: "list", detail: fs.readFileSync('log.json','utf8')}));
                }*/
            case "system": sysLog(data);
            default: 
                send(JSON.stringify({type: "list", detail: fs.readFileSync('log.json','utf8')}));
                
        }
    });

    ws.send(JSON.stringify({type: "greeting", detail: "here is server."}));
    ws.send(JSON.stringify({type: "list", detail: fs.readFileSync('log.json','utf8')}));
});

// HTTPサーバーのアップグレード処理
server.on('upgrade', (request, socket, head) => {
    wss.handleUpgrade(request, socket, head, (ws) => {
        wss.emit('connection', ws, request);
    });
});

app.get('/', (req, res) => {
    res.sendFile(__dirname + "/admin.html");
})

server.listen(port, host, () => {
    console.log(`server is running on http://${host}:${port}`);
});
