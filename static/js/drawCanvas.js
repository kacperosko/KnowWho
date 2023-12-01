const canvas = document.getElementById('answer_canvas');

const ctx = canvas.getContext('2d');
canvas.width = 600;
canvas.height = 400;
ctx.lineJoin = 'round';
ctx.lineCap = 'round';
ctx.strokeStyle = "black";
ctx.lineWidth = '2'
let drawing = false;
let pathsry = [];
let points = [];


$(".color-selector").on("click", function () {

    $(this).siblings().removeClass("selected");
    $(this).addClass("selected");
    ctx.strokeStyle = $(this).css("background-color");
});

$(".width-selector").on("click", function () {
    // Deselect sibling elements
    $(this).siblings().removeClass("width-selected");
    // select clicked element
    $(this).addClass("width-selected");
    //cache current color
    const width = $(this).css("height");
    ctx.lineWidth = parseInt(width);
});


let mouse = {x: 0, y: 0};
let previous = {x: 0, y: 0};

canvas.addEventListener('mousedown', function (e) {
    drawing = true;
    previous = {x: mouse.x, y: mouse.y};
    mouse = oMousePos(canvas, e);
    points = [];
    points.push({x: mouse.x, y: mouse.y, color: ctx.strokeStyle, width: ctx.lineWidth})
});

canvas.addEventListener('mousemove', function (e) {
    if (drawing) {
        previous = {x: mouse.x, y: mouse.y};
        mouse = oMousePos(canvas, e);
// saving the points in the points array
        points.push({x: mouse.x, y: mouse.y, color: ctx.strokeStyle, width: ctx.lineWidth});
// drawing a line from the previous point to the current point
        ctx.beginPath();
        ctx.moveTo(previous.x, previous.y);
        ctx.lineTo(mouse.x, mouse.y);
        ctx.stroke();
    }
}, false);


canvas.addEventListener('mouseup', function () {
    drawing = false;
// Adding the path to the array or the paths
    pathsry.push(points);
}, false);

canvas.addEventListener('mouseleave', function () {
    drawing = false;
// Adding the path to the array or the paths
//     pathsry.push(points);
}, false);


document.getElementById('undo_button').addEventListener("click", Undo);
document.getElementById('clear_button').addEventListener("click", clear);


function drawPaths() {
    // delete everything
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    // draw all the paths in the paths array
    pathsry.forEach(path => {
        ctx.beginPath();
        ctx.strokeStyle = path[0].color;
        ctx.lineWidth = path[0].width;
        ctx.moveTo(path[0].x, path[0].y);
        for (let i = 1; i < path.length; i++) {
            ctx.strokeStyle = path[i].color;
            ctx.lineWidth = path[i].width;
            ctx.lineTo(path[i].x, path[i].y);
        }
        ctx.stroke();
    })
}

function clear() {
    ctx.clearRect(0,0,ctx.canvas.width,ctx.canvas.height);
    points = [];

}

function Undo() {
    pathsry.splice(-1, 1);
    drawPaths();
}


// a function to detect the mouse position
function oMousePos(canvas, evt) {
    var ClientRect = canvas.getBoundingClientRect();
    return { //objeto
        x: Math.round(evt.clientX - ClientRect.left),
        y: Math.round(evt.clientY - ClientRect.top)
    }
}