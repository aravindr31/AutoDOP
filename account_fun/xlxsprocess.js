const fs = require("fs");
const { spawnSync } = require("child_process");
const xlsFolder = "C:\\Users\\Aravind\\Documents\\RD\\xlsFile";
const xlsxFolder = "C:\\Users\\Aravind\\Documents\\RD\\xlsxFile";

module.exports = {
  getXlsFiles: () => {
    return new Promise(async (resolve, reject) => {
      const xlsFiles = fs.readdirSync(xlsFolder);
      let file = Object.assign({}, xlsFiles);
      resolve(file);
    });
  },
  getXlsxFiles: () => {
    console.log("here");
    return new Promise(async (resolve, reject) => {
      const xlsxFiles = fs.readdirSync(xlsxFolder);
      let file = Object.assign({}, xlsxFiles);
      resolve(file);
    });
  },
  xlsConverter: (FName) => {
    console.log(FName)
    return new Promise(async (resolve, reject) => {
      const pyConverter = await spawnSync("python", [
        "C:\\Users\\Aravind\\Documents\\DOP-Agent-Automator\\public\\pythonscripts\\converter.py",
        FName,
      ]);
      if (pyConverter.status != 0) {
      } else {
        resolve(`${pyConverter.stdout}`);
      }
    });
  },
  xlsxFormater: (FName, data) => {
    return new Promise(async (resolve, reject) => {
      console.log(FName, data);
      const pyFormater = spawnSync("python", [
        "C:\\Users\\Aravind\\Documents\\DOP-Agent-Automator\\public\\pythonscripts\\formator.py",
        FName,
        data,
      ]);
      console.log(`${pyFormater.stdout}`);
      resolve(`${pyFormater.stdout}`);
    });
  },
};
