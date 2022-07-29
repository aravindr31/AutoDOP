const { Service } = require("node-windows")

const svc = new Service({
    name:"DOP_Service",
    description:"service for running dop server",
    script:'C:\\Users\\Aravind\\Documents\\DOP-Agent-Automator\\bin\\www'
})

svc.on('install',()=>{
    svc.start()
})
svc.install()