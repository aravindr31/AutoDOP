const fs = require('fs'),
PDFParser = require("pdf2json");

const pdfParser = new PDFParser();

pdfParser.on("pdfParser_dataError", errData => console.error(errData.parserError) );
pdfParser.on("pdfParser_dataReady", pdfData => {
    fs.writeFile("C://Users//Aravind//Documents//DOP-Agent-Automator//pdfjson.json", JSON.stringify(pdfData));
});

pdfParser.loadPDF("C://Users//Aravind//Documents//DOP-Agent-Automator//rdAll.pdf");

// const inputStream = fs.createReadStream("C://Users//Aravind//Documents//DOP-Agent-Automator//rdAll.pdf", {bufferSize: 64 * 1024});
// const outputStream = fs.createWriteStream("C://Users//Aravind//Documents//DOP-Agent-Automator//pdfjson.json");

// inputStream.pipe(new PDFParser()).pipe(new StringifyStream()).pipe(outputStream);