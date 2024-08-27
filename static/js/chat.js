function typeText(element, text, callback) {
    let index = 0;
    function type() {
        if (index < text.length) {
            element.textContent += text.charAt(index);
            index++;
            setTimeout(type, 50);
        } else if (callback) {
            callback();
        }
    }
    type();
}

document.getElementById("send-button").addEventListener("click", function(event) {
    event.preventDefault();
    const userInput = document.getElementById("user-input").value;
    const chatBox = document.getElementById("chat-box");

    if (userInput.trim() === "") {
        return;
    }

    // Add the User Message
    const userMessageDiv = document.createElement("div");
    userMessageDiv.className = "chat-message-right pb-4";
    userMessageDiv.innerHTML = `
        <div>
            <img src="https://bootdey.com/img/Content/avatar/avatar1.png" class="rounded-circle mr-1" alt="Chris Wood" width="40" height="40">
            <div class="text-muted small text-nowrap mt-2">Now</div>
        </div>
        <div class="flex-shrink-1 rounded py-2 px-3 mr-3">
            <div class="font-weight-bold mb-1">You</div>
            ${userInput}
        </div>
    `;
    chatBox.appendChild(userMessageDiv);

    document.getElementById("user-input").value = "";

    chatBox.scrollTop = chatBox.scrollHeight;
    
    // Request
    fetch("{% url 'chat_response' %}", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": "{{ csrf_token }}"
        },
        body: JSON.stringify({ message: userInput })
    })
    .then(response => response.json())
    .then(data => {
        const botMessageDiv = document.createElement("div");
        botMessageDiv.className = "chat-message-left pb-4";
        botMessageDiv.innerHTML = `
        <div>
            <img src="https://bootdey.com/img/Content/avatar/avatar3.png" class="rounded-circle mr-1" alt="Sharon Lessman" width="40" height="40">
            <div class="text-muted small text-nowrap mt-2">Now</div>
        </div>
        <div class="flex-shrink-1 rounded py-2 px-3 ml-3">
            <div class="font-weight-bold mb-1">Bot</div>
            <div class="text"></div>
        </div>
        `;
        chatBox.appendChild(botMessageDiv);

        const botTextElement = botMessageDiv.querySelector('.text');
        const botResponse = data.response || "Error: No response";

        typeText(botTextElement, botResponse, function() {});

        chatBox.scrollTop = chatBox.scrollHeight;
    })
    .catch(error => console.error('Error:', error));
});