let letters =
			"ABCDEFGHIJKLMNOPQRSTUVXYZABCDEFGHIJKLMNOPQRSTUVXYZABCDEFGHIJKLMNOPQRSTUVXYZABCDEFGHIJKLMNOPQRSTUVXYZABCDEFGHIJKLMNOPQRSTUVXYZABCDEFGHIJKLMNOPQRSTUVXYZ";
letters = letters.split("");

let canvas = document.getElementById('matrix-canvas')

const ctx = canvas.getContext("2d");


// canvas.width = window.innerWidth;
// canvas.height = window.innerHeight;
canvas.style.position = "absolute";
canvas.style.zIndex = -1;
// document.body.style.background = "transparent";

let bw = document.getElementById('body').offsetWidth;
let bh = document.getElementById('body').offsetHeight;
canvas.width = (bw * 81) / 100;
canvas.height = (bh * 71) / 100;

// alert(canvas.width + " " + canvas.height);

let fontSize = 10,
    columns = canvas.width / fontSize;

// Setting up the drops
let drops = [];
for (var i = 0; i < columns; ++i) {
    drops.push(canvas.height * Math.random());
}

const draw = () => {

    if (
        canvas === null
    )
        return;
    ctx.fillStyle = "rgba(0, 0, 0, 0.1)";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    for (let i = 0; i < drops.length; ++i) {
        let rand = Math.random();
        let character =
            letters[Math.floor(Math.random() * letters.length)];
        ctx.fillStyle = "#39FF14";
        ctx.fillText(character, i * fontSize, drops[i] * fontSize);
        if (
            drops[i] * fontSize > canvas.height &&
            Math.random() > 0.95
        ) {
            drops[i] = 0;
        }
        ++drops[i];
    }
};
let intervalId = setInterval(draw, 40);

