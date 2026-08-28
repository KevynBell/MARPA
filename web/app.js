const chat = document.getElementById("chat");
const promptInput = document.getElementById("prompt");
const sendButton = document.getElementById("send-button");
const profileSelect = document.getElementById("profile-select");
const newConversationButton = document.getElementById("new-conversation-button");

const ACTIVE_PROFILE_KEY = "marpa.activeProfile";

let currentUserId =
    localStorage.getItem(ACTIVE_PROFILE_KEY) || "kevyn";


function historyKey(userId) {
    return `marpa.chat.${userId}`;
}


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


function loadHistory(userId) {
    const stored = localStorage.getItem(
        historyKey(userId)
    );

    if (!stored) {
        return [];
    }

    try {
        return JSON.parse(stored);
    } catch (error) {
        console.error(
            "Unable to load MARPA chat history:",
            error
        );

        return [];
    }
}


function saveHistory(userId, history) {
    localStorage.setItem(
        historyKey(userId),
        JSON.stringify(history)
    );
}


function saveMessage(userId, role, text, timestamp) {
    const history = loadHistory(userId);

    history.push({
        role,
        text,
        timestamp,
    });

    saveHistory(userId, history);
}


function restoreConversation(userId) {
    chat.innerHTML = "";

    const history = loadHistory(userId);

    for (const item of history) {
        appendMessage(
            item.role,
            item.text,
            {
                timestamp: item.timestamp,
                markdown: item.role === "marpa",
            }
        );
    }

    scrollChatToBottom();
}


async function sendPrompt() {
    const text = promptInput.value.trim();

    if (!text || sendButton.disabled) {
        return;
    }

    const userTimestamp = new Date().toISOString();

    appendMessage(
        "user",
        text,
        {
            timestamp: userTimestamp,
        }
    );

    saveMessage(
        currentUserId,
        "user",
        text,
        userTimestamp
    );

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
                user_id: currentUserId,
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
            updateMarpaMarkdown(
                responseText,
                fullResponse
            );

            const marpaTimestamp =
                new Date().toISOString();

            saveMessage(
                currentUserId,
                "marpa",
                fullResponse,
                marpaTimestamp
            );
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
        responseText.classList.remove(
            "streaming-cursor"
        );

        setComposerBusy(false);
        scrollChatToBottom();
    }
}


function appendMessage(
    role,
    text,
    options = {}
) {
    const message = document.createElement("article");

    message.classList.add(
        "message",
        role
    );

    if (options.thinking) {
        message.classList.add("thinking");
    }

    const header = document.createElement("div");
    header.classList.add("message-header");

    const label = document.createElement("div");
    label.classList.add("message-label");

    label.textContent =
        role === "user"
            ? "You"
            : "MARPA";

    const timestamp = document.createElement("time");

    timestamp.classList.add("message-time");

    const timestampValue =
        options.timestamp ||
        new Date().toISOString();

    timestamp.dateTime = timestampValue;

    timestamp.textContent =
        formatTimestamp(timestampValue);

    const messageText =
        document.createElement("div");

    messageText.classList.add("message-text");

    if (
        role === "marpa" &&
        options.markdown
    ) {
        updateMarpaMarkdown(
            messageText,
            text
        );
    } else {
        messageText.textContent = text;
    }

    if (options.thinking) {
        messageText.classList.add(
            "thinking-dots"
        );
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
    profileSelect.disabled = isBusy;
    newConversationButton.disabled = isBusy;

    sendButton.textContent =
        isBusy
            ? "Working…"
            : "Send";

    if (!isBusy) {
        promptInput.focus();
    }
}


function formatTimestamp(timestamp) {
    return new Intl.DateTimeFormat([], {
        hour: "numeric",
        minute: "2-digit",
    }).format(new Date(timestamp));
}


function scrollChatToBottom() {
    chat.scrollTop = chat.scrollHeight;
}


async function startNewConversation() {
    if (newConversationButton.disabled) {
        return;
    }

    const confirmed = window.confirm(
        "Start a new conversation? Your saved history will be preserved."
    );

    if (!confirmed) {
        return;
    }

    setComposerBusy(true);

    try {
        const response = await fetch(
            "/conversation/reset",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    user_id: currentUserId,
                }),
            }
        );

        if (!response.ok) {
            const errorText = await response.text();

            throw new Error(
                errorText ||
                "Unable to reset conversation."
            );
        }

        localStorage.removeItem(
            historyKey(currentUserId)
        );

        chat.innerHTML = "";

    } catch (error) {
        console.error(
            "Unable to start a new MARPA conversation:",
            error
        );

        window.alert(
            "MARPA could not start a new conversation."
        );

    } finally {
        setComposerBusy(false);
    }
}


sendButton.addEventListener(
    "click",
    sendPrompt
);


promptInput.addEventListener(
    "keydown",
    (event) => {
        if (
            event.key === "Enter" &&
            !event.shiftKey &&
            !event.isComposing
        ) {
            event.preventDefault();
            sendPrompt();
        }
    }
);


profileSelect.addEventListener(
    "change",
    () => {
        currentUserId =
            profileSelect.value;

        localStorage.setItem(
            ACTIVE_PROFILE_KEY,
            currentUserId
        );

        restoreConversation(
            currentUserId
        );

        promptInput.focus();
    }
);


newConversationButton.addEventListener(
    "click",
    startNewConversation
);


profileSelect.value = currentUserId;

restoreConversation(currentUserId);

promptInput.focus();
