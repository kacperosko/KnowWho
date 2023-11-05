document.addEventListener("DOMContentLoaded", () => {
    const roomCode = window.location.href.split('/').pop();

    const chatSocket = new WebSocket(`ws://${window.location.host}/ws/chat/${roomCode}/`);

    chatSocket.addEventListener("open", (event) => {
      console.log("The connection was set up successfully!");
      chatSocket.send(JSON.stringify({username: "{{request.user.username}}" }));
    });

    chatSocket.addEventListener("close", (event) => {
      console.log("Something unexpected happened!");
    });

    const messageInput = document.querySelector("#id_message_send_input");
    messageInput.focus();

    messageInput.addEventListener("keyup", (event) => {
      if (event.keyCode === 13) {
        document.querySelector("#id_message_send_button").click();
      }
    });

    document.querySelector("#id_message_send_button").addEventListener("click", (event) => {
      const messageInput = document.querySelector("#id_message_send_input");
      const message = messageInput.value.trim();
      if (message !== "") {
        chatSocket.send(JSON.stringify({ message, username: "{{request.user.username}}" }));
        messageInput.value = "";
      }
    });

    chatSocket.addEventListener("message", (event) => {
      const data = JSON.parse(event.data);
      const chatItemContainer = document.querySelector("#id_chat_item_container");
      const div = document.createElement("div");
      div.textContent = `${data.username} : ${data.message}`;
      chatItemContainer.appendChild(div);
    });
});