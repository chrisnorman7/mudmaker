const output = document.getElementById("output")
let soc = null

const prompt = document.getElementById("prompt")
const text = document.getElementById("text")
const textarea = document.getElementById("textarea")
const status = document.getElementById("status")

let input = text

function writeMessage(text) {
    for (let line of text.split("\n")) {
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
        text.focus()
    } else {
        writeMessage("You are not connected. Please refresh the page and try again.")
    }
}

window.onload = () => {
    status.hidden = true
    textarea.hidden = true
    let req = new XMLHttpRequest()
    req.open("GET", `http://${window.location.host}/wsport`)
    req.onload = () => {
        let websocketPort = JSON.parse(req.response)
        soc = new WebSocket(`ws://${window.location.hostname}:${websocketPort}`)
        soc.onerror = () => {
            soc = null
            writeMessage("Unable to connect. Please refresh and try again.")
        }
        soc.onopen = () => {
            status.hidden = false
            writeMessage("*** Connected ***")
            text.focus()
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
            status.hidden = true
            soc = null
            writeMessage("*** Connection closed ***")
        }
    }
    req.send()
}

const functions = {
    "message": args => writeMessage(args[0]),
    "inputType": args => {
        let type = args[0]
        if (type != input.type) {
            if (type == "textarea") {
                input = textarea
                input.hidden = false
                input.focus()
                text.hidden = true
            } else {
                textarea.hidden = true
                text.hidden = false
                input = text
                input.focus()
                input.type = type
            }
        }
    },
    "promptText": (args) => {
        let text = args[0]
        if (text != prompt.innerText) {
            prompt.innerText = text
        }
    },
    "title": args => {
        let title = args[0]
        if (title != document.title) {
            document.title = title
        }
    },
    "inputText": args => {
        let value = args[0]
        if (input.value != value) {
            input.value = value
        }
    },
    "status": args => {
        let html = args[0]
        if (status.innerHTML != html) {
            status.innerHTML = html
        }
    },
}
