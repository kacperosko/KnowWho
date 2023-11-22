
const draggable_elements_space = document.getElementById("draggable_elements");
let draggableElements;
let droppableElements;

initiateGame();

function initiateGame() {

  draggableElements = document.querySelectorAll(".draggable");
  droppableElements = document.querySelectorAll(".droppable");

  draggableElements.forEach(elem => {
    elem.addEventListener("dragstart", dragStart);
    // elem.addEventListener("drag", drag);
    // elem.addEventListener("dragend", dragEnd);
  });

  droppableElements.forEach(elem => {
    elem.addEventListener("dragenter", dragEnter);
    elem.addEventListener("dragover", dragOver);
    elem.addEventListener("dragleave", dragLeave);
    elem.addEventListener("drop", drop);
  });

}


function dragStart(event) {
    event.dataTransfer.setData("id", event.target.id);
}


function dragEnter(event) {
  if(event.target.classList && event.target.classList.contains("droppable")) {
    event.target.classList.add("border-pink__c")
    event.target.classList.remove("border-colors-white")

  }
}

function dragOver(event) {
  if(event.target.classList && event.target.classList.contains("droppable") && !event.target.classList.contains("dropped")) {
    event.preventDefault();

  }
}

function dragLeave(event) {
  if(event.target.classList && event.target.classList.contains("droppable") && !event.target.classList.contains("dropped")) {
    event.target.classList.remove("border-pink__c")
    event.target.classList.add("border-colors-white")
  }
}

function drop(event) {
    event.preventDefault();
    const draggableElementBrand = event.dataTransfer.getData("id");

    if (event.target.getAttribute('drop_space') !== 'answer'){
        draggable_elements_space.appendChild(document.getElementById(draggableElementBrand));
        return;
    }

    const dropped_elements = event.target.childNodes;
    for(let i=0; i<dropped_elements.length; i++) {
        draggable_elements_space.appendChild(dropped_elements[i]);
    }
    event.target.appendChild(document.getElementById(draggableElementBrand));

}