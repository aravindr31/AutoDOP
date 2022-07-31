const fs = require("fs");
const { spawnSync } = require("child_process");
const xlsFolder = "C:\\Users\\aravi\\Documents\\RD\\xlsFile";
const xlsxFolder = "C:\\Users\\aravi\\Documents\\RD\\xlsxFile";

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
    return new Promise(async (resolve, reject) => {
      const pyConverter = spawnSync("python", [
        "C:\\Users\\aravi\\Documents\\xlAuto\\converter.py",
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
        "C:\\Users\\aravi\\Documents\\xlAuto\\formator.py",
        FName,
        data,
      ]);
      console.log(`${pyFormater.stdout}`);
      resolve(`${pyFormater.stdout}`);
    });
  },
};
