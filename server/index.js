const express = require("express");
const morgan = require("morgan");
var multer = require('multer');
const fs = require("fs");
var upload = multer({ path: multer.memoryStorage() });
const app = express();

app.use(morgan("dev"));

app.post("/upload", upload.single('archive.tar.gz'), function (req, res, next) {
    var file_buffer = req.file.buffer;
    var target_path = 'archives/' + req.query.project_name + ".tar.gz";
    var stream = fs.createWriteStream(target_path);
    stream.once('open', function (fd) {
        stream.write(file_buffer);
        stream.end();
    })
    res.send("OK");
});

app.get("/exists", (req, res) => {
    var project = req.query.project_name;
    if (fs.existsSync("archives/" + project + ".tar.gz")) {
        res.status(200);
        res.end();
    } else {
        res.status(404);
        res.end();
    }
})

app.get("/download", (req, res) => {
    var project = req.query.project_name;
    if (fs.existsSync("archives/" + project + ".tar.gz")) {
        res.statusCode(200);
        res.end();
    } else {
        res.statusCode(404);
        res.end();
    }
});

app.listen(3000, () => {
    console.log("Listening on port 3000");
});