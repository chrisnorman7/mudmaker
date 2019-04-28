"""Provides html and js sources."""


html = """<!doctype html>
<html lang="en">
    <head>
        <title>MudMaker</title>
    </head>
    <body>
        <div id="output" aria-live="polite" aria-atomic="false" aria-relevant=\
"additions text"></div>
        <hr>
        <form id="inputForm">
            <p><label>Command: <input type="text" autocomplete="off" id=\
"command"></label></p>
            <p><input type="submit" value="Send"></p>
        </form>
        <script src="/static/main.js"></script>
    </body>
</html>"""

js = """const output = document.getElementById("output")
let soc = null

const input = document.getElementById("command")

function writeMessage(text) {
    for (let line of text.split("\\n")) {
        let p = document.createElement("p")
        let t = document.createTextNode(line)
        p.appendChild(t)
        output.appendChild(p)
    }window.scrollTo(0,document.body.scrollHeight)
}

document.getElementById("inputForm").onsubmit = (e) => {
    e.preventDefault()
    if (soc !== null) {
        soc.send(input.value)
        input.value = ""
        input.focus()
    } else {
        writeMessage("You are not connected. Please refresh the page and try \
again.")
    }
}

window.onload = () => {
    let req = new XMLHttpRequest()
    req.open("GET", `http://${window.location.host}/wsport`)
    req.onload = () => {
        let websocketPort = JSON.parse(req.response)
        soc = new WebSocket(`ws://${window.location.hostname}:${websocketPort}\
`)
        soc.onerror = () => {
            soc = null
            writeMessage("Unable to connect. Please refresh and try again.")
        }
        soc.onopen = () => {
            writeMessage("*** Connected ***")
            input.focus()
        }
        soc.onmessage = (e) => {
            let data = JSON.parse(e.data)
            let name = data.name
            let func = functions[name]
            if (func === undefined) {
                writeMessage(`Unrecognised command: ${name}.`)
            } else {
                func(data.args)
            }
        }
        soc.onclose = () => {
            soc = null
            writeMessage("*** Connection closed ***")
        }
    }
    req.send()
}

const functions = {
    "message": args => writeMessage(args[0])
}
"""
