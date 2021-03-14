const { promisify } = require("util");
const getPixels = promisify(require("get-pixels"));
const ATCQ = require("./atcq");
import "regenerator-runtime/runtime"; //? idk

new QWebChannel(qt.webChannelTransport, function (channel) {
  window.backend = channel.objects.atcq;
});

window.setStatus = (str) => {
  document.getElementById("submit-text").innerHTML = str;
};

// this will not work with local files as we cannot get the real filepath? will have to
// take a url or a full local filepath as a string
document.getElementById("submit-url").addEventListener("click", function () {
  document.getElementById("submit-text").innerHTML = "Submitted URL";
  submit();
});

async function submit() {
  let file = document.getElementById("url").value;
  if (!file) {
    file = "file:///" + window.defaultImage; // use the default image if empty
  }
//   backend.print(file);

  backend.resize(file, async function (y) {
    function setStatus(str) {
      document.getElementById("submit-text").innerHTML = str;
    }

    let f =
      "file:///C:/Users/NickTR2/Dropbox/1_HOUDINI/04_Plugins/ATCQ_Python/QWebChannel_ATCQ_Test/atcq_image.png";
    // f = "file:///" + window.defaultImage;
    let { data } = await getPixels(f); // load your image data as RGBA array

    backend.print("quantizing...");
    const maxColors = document.getElementById("maxcol").value;
    const targetColors = document.getElementById("targetcol").value;
    const atcq = ATCQ({
      maxColors,
      disconnects: false,
      maxIterations: 4,
      progress(t) {
        let pr = Math.floor(t * 100);
        setStatus(
          "Image Processing Done. Quantizing Colours: " + String(pr) + "%"
        );
      },
    });
    atcq.addData(data);
    await atcq.quantizeAsync();

    setStatus("Quantizing Done - Reducing Palette");
    let cols = [];
    let wts = [];
    const palette = atcq.getWeightedPalette(targetColors).map((p) => {
      cols.push(p.color);
      wts.push(p.weight);
    });
    backend.send_palette(JSON.stringify(cols), JSON.stringify(wts));
    setStatus("Reducing Palette - Done");
  });
}
