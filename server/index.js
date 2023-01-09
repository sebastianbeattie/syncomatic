const express = require("express");
const morgan = require("morgan");
var multer = require('multer');
const fs = require("fs");
const config = require("./config.json")
var upload = multer({ path: multer.memoryStorage() });
const app = express();

app.use(morgan("dev"));
app.use(express.static('public'));

app.get("/", (req, res) => {
    res.redirect("/index.html");
})

app.post("/upload", upload.single('archive.tar.gz'), function (req, res, next) {
    var fileBuffer = req.file.buffer;
    var targetPath = 'archives/' + req.query.project_name + ".tar.gz";
    var stream = fs.createWriteStream(targetPath);
    stream.once('open', function (fd) {
        stream.write(fileBuffer);
        stream.end();
    })
    res.send("OK");
});

app.get("/exists", (req, res) => {
    var project = req.query.project_name;
    var fileName = __dirname + "/archives/" + project + ".tar.gz";
    if (fs.existsSync(fileName)) {
        res.status(200);
        res.end();
    } else {
        res.status(404);
        res.end();
    }
});

app.get("/list", (req, res) => {
    var fileList = fs.readdirSync(__dirname + "/archives");
    res.setHeader("Content-Type", "application/json");
    fileList = fileList.map(file => file.replace(".tar.gz", ""));
    res.end(JSON.stringify({projects: fileList}));
});

app.get("/download", (req, res) => {
    var project = req.query.project_name;
    var fileName = __dirname + "/archives/" + project + ".tar.gz";
    if (fs.existsSync(fileName)) {
        res.status(200);
        res.sendFile(fileName);
    } else {
        res.status(404);
        res.end();
    }
});

app.listen(config.port, () => {
    console.log(`Syncomatic Server available on port ${config.port}`);
});