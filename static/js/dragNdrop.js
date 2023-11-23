
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

function saveAnswers() {
    let draggable_elements = document.querySelectorAll(".draggable");
    let success = true;
    let answers = [];

    draggable_elements.forEach(elem => {
        const player_code = elem.parentNode.getAttribute('player-code');
        if (player_code === null || player_code === "") {
            success = false;
        } else {
            const temp_json = {
                "player_code": player_code,
                "answer_code": elem.getAttribute("answer-code")
            }
            answers.push(temp_json);
        }
    });

    if (!success) {
        $('#error_message').text("You must assign all answers to players before save");
        return;
    }

    console.log("success");
    console.log(answers);

    $.ajax({
        url: '/game/know_who',
        type: 'POST',
        data: {
            'answers': JSON.stringify(answers),  // Serialize answers array to JSON
            'mode': "multiple",
            csrfmiddlewaretoken: $(csrf_token).val(),
        },
        dataType: 'json',
        success: function(response) {
            if (response.success) {
                console.log("multiple_anwer success");
                chatSocket.send(JSON.stringify({'action':ACTIONS.ANSWER, player_code}));
              window.location.href = `/game/waitroom?room_code=${roomCode}&status=after`;
            } else {
                console.log("multiple_anwer error");
                console.log(response);
            }
        },
        error: function(error) {
            console.log("Ajax request failed");
            console.log(error);
        }
    });
}