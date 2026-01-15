const startBtn = document.getElementById("startListening");
const stopBtn = document.getElementById("stopListening");

const recognizedText = document.getElementById("recognizedText");
const assistantText = document.getElementById("assistantText");
const speakBtn = document.getElementById("speakBtn");

let recognition;
let lastResponse = "";
let listening = false;

/* ---------- SPEECH SYNTHESIS ---------- */
function speak(text) {
  if (!text) return;

  // IMPORTANT: clear queue
  window.speechSynthesis.cancel();

  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = "en-US";
  utterance.rate = 1;
  utterance.pitch = 1;
  utterance.volume = 1;

  const voices = window.speechSynthesis.getVoices();
  if (voices.length > 0) {
    utterance.voice =
      voices.find(v => v.lang === "en-US") || voices[0];
  }

  window.speechSynthesis.speak(utterance);
}

// Required for Chrome
window.speechSynthesis.onvoiceschanged = () => {};

/* ---------- SPEECH RECOGNITION SETUP ---------- */
const SpeechRecognition =
  window.SpeechRecognition || window.webkitSpeechRecognition;

if (!SpeechRecognition) {
  alert("Speech Recognition not supported in this browser");
}

recognition = new SpeechRecognition();
recognition.lang = "en-US";
recognition.continuous = true;
recognition.interimResults = false;

/* ---------- START LISTENING ---------- */
startBtn.onclick = () => {
  if (listening) return;

  recognition.start();
  listening = true;

  startBtn.disabled = true;
  stopBtn.disabled = false;

  assistantText.innerText = "🎤 Listening...";
};

/* ---------- STOP LISTENING ---------- */
stopBtn.onclick = () => {
  recognition.stop();
};

/* ---------- WHEN RECOGNITION STOPS ---------- */
recognition.onend = () => {
  listening = false;
  startBtn.disabled = false;
  stopBtn.disabled = true;
};

/* ---------- ON SPEECH RESULT ---------- */
recognition.onresult = (event) => {
  const speech =
    event.results[event.results.length - 1][0].transcript
      .toLowerCase()
      .trim();

  recognizedText.innerText = speech;

  fetch("/api/voice-command", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ command: speech }),
  })
    .then(res => res.json())
    .then(data => {
      assistantText.innerText = data.response;
      lastResponse = data.response;

      // 🔊 SPEAK AUTOMATICALLY
      speak(data.response);

      // 🔁 PERFORM ACTION
      if (data.action === "inbox") openSection("inbox");
      if (data.action === "sent") openSection("sent");
      if (data.action === "trash") openSection("trash");
      if (data.action === "compose") openSection("compose");
      if (data.action === "logout") window.location.href = "/logout";
    })
    .catch(() => {
      assistantText.innerText = "Error processing command.";
    });
};

/* ---------- SPEAK RESPONSE BUTTON ---------- */
speakBtn.onclick = () => {
  speak(lastResponse);
};
