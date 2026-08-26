const chat = document.getElementById("chat");
const promptInput = document.getElementById("prompt");
const sendButton = document.getElementById("send-button");

function renderMarkdown(text) {
    const rendered = marked.parse(text, {
        breaks: true,
        gfm: true,
    });

    return DOMPurify.sanitize(rendered);
}

function updateMarpaMarkdown(element, text) {
    element.innerHTML = renderMarkdown(text);
}

async function sendPrompt() {
    const text = promptInput.value.trim();

    if (!text || sendButton.disabled) {
        return;
    }

    appendMessage("user", text);

    promptInput.value = "";
    setComposerBusy(true);

    const marpaMessage = appendMessage(
        "marpa",
        "MARPA is thinking",
        {
            thinking: true,
        }
    );

    const responseText =
        marpaMessage.querySelector(".message-text");

    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                prompt: text,
            }),
        });

        if (!response.ok) {
            const errorText = await response.text();

            throw new Error(
                errorText ||
                `Request failed with status ${response.status}`
            );
        }

        if (!response.body) {
            throw new Error(
                "The browser did not provide a response stream."
            );
        }

        marpaMessage.classList.remove("thinking");
        responseText.classList.remove("thinking-dots");
        responseText.classList.add("streaming-cursor");
        responseText.textContent = "";

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        let receivedText = false;
        let fullResponse = "";

        while (true) {
            const { value, done } = await reader.read();

            if (done) {
                break;
            }

            const chunk = decoder.decode(value, {
                stream: true,
            });

            if (chunk) {
                receivedText = true;
                fullResponse += chunk;
                responseText.textContent = fullResponse;
                scrollChatToBottom();
            }
        }

        const finalChunk = decoder.decode();

        if (finalChunk) {
            receivedText = true;
            fullResponse += finalChunk;
            responseText.textContent = fullResponse;
        }

        if (!receivedText) {
            responseText.textContent =
                "MARPA completed the request without returning text.";
        } else {
            updateMarpaMarkdown(responseText, fullResponse);
        } 

    } catch (error) {
        marpaMessage.classList.remove("thinking");
        marpaMessage.classList.add("error");

        responseText.classList.remove(
            "thinking-dots",
            "streaming-cursor"
        );

        responseText.textContent =
            `Unable to reach MARPA: ${error.message}`;

    } finally {
        responseText.classList.remove("streaming-cursor");
        setComposerBusy(false);
        scrollChatToBottom();
    }
}


function appendMessage(role, text, options = {}) {
    const message = document.createElement("article");
    message.classList.add("message", role);

    if (options.thinking) {
        message.classList.add("thinking");
    }

    const header = document.createElement("div");
    header.classList.add("message-header");

    const label = document.createElement("div");
    label.classList.add("message-label");
    label.textContent = role === "user" ? "You" : "MARPA";

    const timestamp = document.createElement("time");
    timestamp.classList.add("message-time");
    timestamp.dateTime = new Date().toISOString();
    timestamp.textContent = getCurrentTime();

    const messageText = document.createElement("div");
    messageText.classList.add("message-text");
    messageText.textContent = text;

    if (options.thinking) {
        messageText.classList.add("thinking-dots");
    }

    header.appendChild(label);
    header.appendChild(timestamp);

    message.appendChild(header);
    message.appendChild(messageText);

    chat.appendChild(message);
    scrollChatToBottom();

    return message;
}


function setComposerBusy(isBusy) {
    sendButton.disabled = isBusy;
    promptInput.disabled = isBusy;
    sendButton.textContent = isBusy ? "Working…" : "Send";

    if (!isBusy) {
        promptInput.focus();
    }
}


function getCurrentTime() {
    return new Intl.DateTimeFormat([], {
        hour: "numeric",
        minute: "2-digit",
    }).format(new Date());
}


function scrollChatToBottom() {
    chat.scrollTop = chat.scrollHeight;
}


sendButton.addEventListener("click", sendPrompt);

promptInput.addEventListener("keydown", (event) => {
    if (
        event.key === "Enter" &&
        !event.shiftKey &&
        !event.isComposing
    ) {
        event.preventDefault();
        sendPrompt();
    }
});

promptInput.focus();
