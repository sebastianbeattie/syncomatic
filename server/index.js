const express = require("express");
const morgan = require("morgan");
var multer = require('multer');
const fs = require("fs");
var upload = multer({ path: multer.memoryStorage() });
const app = express();

app.use(morgan("dev"));

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
})

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

app.listen(3000, () => {
    console.log("Listening on port 3000");
});