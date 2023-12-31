let currentPlayersList = null;
let roomCode = null;
let chatSocket = null;
const ACTIONS = {
    ANSWER:'answer',
    JOIN:'join',
    CLOSE:'close',
    QUESTION:'question',
    SHUFFLE_PLAYERS:'shuffle_players',
    RESULT:'result',
    FINISH:'finish',
};


document.addEventListener("DOMContentLoaded", () => {
    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
    roomCode =  urlParams.get('room_code')

    chatSocket = new WebSocket(`ws://${window.location.host}/ws/chat/${roomCode}/`);
    console.log('websocket');
    console.log(chatSocket);
    console.log(JSON.stringify(chatSocket));

    chatSocket.addEventListener("open", (event) => {
      console.log('The connection was set up successfully to room ' + roomCode + ' for player ' + player_code);
      // document.cookie = 'chatsocket=' + chatSocket;
      const action = ACTIONS.JOIN;
      // console.log(JSON.stringify({nickname, action, player_id, player_code}));
      chatSocket.send(JSON.stringify({nickname, action, player_id, player_code}));
      // let result = document.cookie.match(new RegExp('chatsocket' + '=([^;]+)'));
      // console.log(result)
      // result && (result = JSON.parse(result[1]));
    });

    chatSocket.addEventListener("close", (event) => {
      console.log("Something unexpected happened!");
      const action = ACTIONS.CLOSE;
      chatSocket.send(JSON.stringify({nickname, action}));
      // try {
      //     chatSocket = new WebSocket(`ws://${window.location.host}/ws/chat/${roomCode}/`);
      // } catch (e) {
      //     console.log(e);
      // }

    });


    chatSocket.onmessage = function (e) {
        console.log("chatSocket.onmessage");
        const data = JSON.parse(e.data);

        console.log('data');
        console.log('data action ->' + data.action);
        console.log(data);
        if (data.action === 'join' && (player_code === ''  || player_code === 'null' || player_code === null)) {
            console.log('player_code -> ' + player_code);
            player_code = data.player_code;
            updateSessionVariable('player_code', data.player_code, function () {
                updateSessionVariable('player_id',  data.player_id, function (){});
            }
            );
        }
        if ((data.action === 'join' || data.action === 'close') && currentPlayersList !== data.players){
            if(window.location.href.indexOf("lobby") !== -1) {
                currentPlayersList = data.players;
                generatePlayersList(currentPlayersList);
            }
        }
        if (data.action === 'question'){
            console.log("question action");
            updateSessionVariable('current_question', data.question, function () {
                updateSessionVariable('current_question_id', data.question_id, function (){
                    console.log('HREF QUESTION');
                    window.location.href = `/game/question?room_code=${roomCode}`;
                });
            });
        }
        if (data.action === ACTIONS.ANSWER){
            console.log(data.player_code + ' answered question');
            updateWaitList(data.player_code);
        }
        if (data.action === ACTIONS.SHUFFLE_PLAYERS){
            console.log('SHUFFLE_PLAYERS');
            window.location.href = `/game/know_who?room_code=${roomCode}`;
        }
        if (data.action === ACTIONS.RESULT){
            console.log('RESULT');
            window.location.href = `/game/results?room_code=${roomCode}`;
        }
        if (data.action === ACTIONS.
            FINISH){
            console.log('FININSH');
            window.location.href = `/game/finish?room_code=${roomCode}`;
        }
    };
});


function updateWaitList(player_code){
    console.log('updateWaitList -> waitroom_status_'+player_code);
    $( "#waitroom_status_"+player_code).addClass( 'answered');
}

function generatePlayersList(playersList) {
    if (playersList === null){
        return;
    }
    console.log('playersList' + playersList)
    const gamePlayersContainer = document.getElementById("game_players_container");
    gamePlayersContainer.innerHTML = '';
    playersList.forEach(player => {
        if (player.player_code !== player_code) {
            console.log('adding DIV for -> ' + player.player_code);
            const playerDiv = document.createElement("div");
            playerDiv.className = "mb-3 bg-light_aqua__c rounded-xl py-2 px-5 flex items-center";

            // Create an image element
            const imgElement = document.createElement("img");
            imgElement.src = profile_picture_url;
            imgElement.className = "w-8 mr-3";
            imgElement.alt = "user profile";

            // Create a paragraph element for the player's nickname
            const pElement = document.createElement("p");
            pElement.textContent = player.nickname;

            // Append the image and paragraph elements to the player's div
            playerDiv.appendChild(imgElement);
            playerDiv.appendChild(pElement);

            // Add the player's div to the parent container
            gamePlayersContainer.appendChild(playerDiv);
        }
    });
}

function getQuestion(action) {
    $.ajax({
        type: "GET",
        url: '/get_question',
        data: {
            room_code: roomCode,
            action: action
        },
        success: function (d) {
            console.log(d);
            if (d.status === ACTIONS.FINISH){
                chatSocket.send(JSON.stringify({'action': ACTIONS.FINISH}));
            }else {
                console.log(d.question);
                const action = 'question';
                chatSocket.send(JSON.stringify({'question': d.question, action, 'question_id': d.question_id}));
            }
        },
    });
}

function shufflePlayers(action) {
    $.ajax({
        type: "GET",
        url: '/shuffle_players',
        data: {
            room_code: roomCode,
        },
        success: function (d) {
            console.log('shufflePlayers success');
            console.log(d);
            const action = ACTIONS.SHUFFLE_PLAYERS
            chatSocket.send(JSON.stringify({action}));
        },
    });
}

function updateSessionVariable(session_name, session_value, _callback) {
    console.log('calling  updateSessionVariable');
    console.log('session_name -> ' + session_name);
    console.log('session_value -> ' + session_value);
    $.ajax({
        type: "GET",
        url: '/update_session_variable',
        data: {
            // csrfmiddlewaretoken: $(csrf_token).val(),
            session_name: session_name,
            session_value: session_value
        },
        success: function (d) {
            console.log('updateSessionVariable success');
            console.log(d);
            _callback()
        },
    });
}

$(function() {
    $('#answer_question_form').on('submit', function(event) {
      event.preventDefault();
      $.ajax({
        url: '/game/question',
        type: 'POST',
        data: $(this).serialize(),
        dataType: 'json',
        success: function(response) {
          if (response.success) {
              console.log("answer_question_form success");
              chatSocket.send(JSON.stringify({'action':ACTIONS.ANSWER, player_code}));
              window.location.href = `/game/waitroom?room_code=${roomCode}&status=before`;
          } else {
            console.log("answer_question_form error");
            console.log(response);
          }
        }
      });
    });
  });

$(function() {
    $('#answer_assign_form').on('submit', function(event) {
      event.preventDefault();
      $.ajax({
        url: '/game/know_who',
        type: 'POST',
        data: $(this).serialize(),
        dataType: 'json',
        success: function(response) {
          if (response.success) {
              console.log("answer_assign_form success");
              chatSocket.send(JSON.stringify({'action':ACTIONS.ANSWER, player_code}));
              window.location.href = `/game/waitroom?room_code=${roomCode}&status=after`;
          } else {
            console.log("answer_question_form error");
            console.log(response);
          }
        }
      });
    });
  });

function showResults(){
    chatSocket.send(JSON.stringify({'action':ACTIONS.RESULT}));
}