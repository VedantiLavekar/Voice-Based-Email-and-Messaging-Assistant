const SpeechRecognition =
    window.SpeechRecognition || window.webkitSpeechRecognition;

const recognition = new SpeechRecognition();
recognition.lang = "en-US";

recognition.onresult = (event) => {
    const command = event.results[0][0].transcript.toLowerCase();
    console.log("Voice:", command);

    if (command.includes("login")) {
        window.location.href = "/login";
    }
    if (command.includes("register")) {
        window.location.href = "/register";
    }
};

recognition.start();

function goLogin() {
    window.location.href = "/login";
}

function goRegister() {
    window.location.href = "/register";
}
