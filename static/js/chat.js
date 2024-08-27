// Function to add typing effect to text
function typeText(element, text, callback) {
    let index = 0;
    function type() {
        if (index < text.length) {
            element.textContent += text.charAt(index);
            index++;
            setTimeout(type, 50); // Typing speed
        } else if (callback) {
            callback();
        }
    }
    type();
}

// Function to get the CSRF token from meta tag
function getCsrfToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.getAttribute('content') : null;
}

const csrfToken = getCsrfToken();

// Function to get the current time in HH:MM format
function getCurrentTime() {
    const now = new Date();
    const hours = now.getHours().toString().padStart(2, '0'); // Add leading zero if needed
    const minutes = now.getMinutes().toString().padStart(2, '0'); // Add leading zero if needed
    return `${hours}:${minutes}`;
}

// Function to handle sending messages
function sendMessage() {
    const userInput = document.getElementById("user-input").value;
    const chatBox = document.getElementById("chat-box");

    if (userInput.trim() === "") {
        return;
    }

    // Add the User Message
    const userMessageDiv = document.createElement("div");
    userMessageDiv.className = "chat-message-right pb-4";
    userMessageDiv.innerHTML = `
        <div class="flex-shrink-1 rounded py-2 px-3 mr-3">
            <div class="font-weight-bold mb-1">You</div>
            ${userInput}
        </div>
    `;
    chatBox.appendChild(userMessageDiv);

    document.getElementById("user-input").value = "";

    chatBox.scrollTop = chatBox.scrollHeight;

    // Request
    fetch("/llm/scout/chat_response/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken // Include the CSRF token here
        },
        body: JSON.stringify({ message: userInput })
    })
    .then(response => response.json())
    .then(data => {
        const botMessageDiv = document.createElement("div");
        botMessageDiv.className = "chat-message-left pb-4";
        botMessageDiv.innerHTML = `
        <div style="padding-right: 10px;">
            <img src="${window.avatarImageUrl}" class="rounded-circle mr-1" width="40" height="40" alt="Bot Avatar">
            <div class="text-muted small text-nowrap mt-2">${getCurrentTime()}</div>
        </div>
        <div class="flex-shrink-1 rounded py-2 px-3 ml-3">
            <div class="font-weight-bold mb-1">Scouty</div>
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
}

// Add event listener for the send button
document.getElementById("send-button").addEventListener("click", function(event) {
    event.preventDefault();
    sendMessage();
});

// Add event listener for the Enter key in the input field
document.getElementById("user-input").addEventListener("keypress", function(event) {
    if (event.key === 'Enter') {
        event.preventDefault();
        document.getElementById("send-button").click();
    }
});
