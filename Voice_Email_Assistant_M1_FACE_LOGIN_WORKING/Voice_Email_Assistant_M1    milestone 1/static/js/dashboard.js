const startBtn = document.getElementById("startListening");
const stopBtn = document.getElementById("stopListening");

const transcriptBox = document.getElementById("recognizedText");
const responseBox = document.getElementById("assistantText");

let recognition;
let audioUnlocked = false;

/* ---------- FORCE AUDIO UNLOCK ---------- */
function unlockAudio() {
    const utter = new SpeechSynthesisUtterance(
        "Voice assistant enabled. You can now give commands."
    );
    utter.lang = "en-US";
    utter.volume = 1;
    utter.rate = 1;
    utter.pitch = 1;

    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(utter);

    audioUnlocked = true;
}

/* ---------- SPEECH RECOGNITION ---------- */
const SpeechRecognition =
    window.SpeechRecognition || window.webkitSpeechRecognition;

recognition = new SpeechRecognition();
recognition.lang = "en-US";
recognition.continuous = false;
recognition.interimResults = false;

/* ---------- ENABLE ASSISTANT (ONE CLICK) ---------- */
startBtn.onclick = () => {
    unlockAudio();           // 🔊 MUST SPEAK HERE
    recognition.start();     // 🎙 THEN listen
};

stopBtn.onclick = () => {
    recognition.stop();
};

/* ---------- WHEN USER SPEAKS ---------- */
recognition.onresult = e => {
    const command = e.results[0][0].transcript
        .toLowerCase()
        .replace(".", "")
        .replace(",", "")
        .trim();

    transcriptBox.innerText = command;
    sendCommand(command);
};

/* ---------- BACKEND ---------- */
function sendCommand(command) {
    fetch("/api/voice-command", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ command })
    })
    .then(res => res.json())
    .then(data => {
        responseBox.innerText = data.response;
        speak(data.response);

        if (data.action === "logout") {
            window.location.href = "/logout";
        }
    })
    .catch(() => {
        speak("Error processing command");
    });
}

/* ---------- TEXT TO SPEECH ---------- */
function speak(text) {
    if (!audioUnlocked) return;

    const utter = new SpeechSynthesisUtterance(text);
    utter.lang = "en-US";
    utter.volume = 1;
    utter.rate = 1;
    utter.pitch = 1;

    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(utter);
}
