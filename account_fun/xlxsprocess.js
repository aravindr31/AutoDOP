const readXlsxFile = require('read-excel-file/node')

// File path.

const path =  "C:\\Users\\Aravind\\Documents\\DOP-Agent-Automator\\RDInstallmentReport17-07-2022 (6).xls"
readXlsxFile(path).then((rows) => {
console.table(rows)
})

// // Readable Stream.
// readXlsxFile(fs.createReadStream(path)).then((rows) => {
// console.table(rows)
// })