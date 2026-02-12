let recognition;
let emails = [];
let currentFolder = "";
let isStopped = false;
let currentLang = "en-IN";
let isSpeaking = false;

/* ---------- SPEAK ---------- */
function speak(text, afterSpeak) {
    if (isStopped) return;

    // 🛑 STOP listening before assistant speaks
    if (recognition) {
        try { recognition.stop(); } catch (e) {}
    }

    isSpeaking = true;
    speechSynthesis.cancel();

    const u = new SpeechSynthesisUtterance(text);
    u.lang = currentLang;

    u.onend = () => {
        isSpeaking = false;

        // ▶️ Resume listening AFTER speech
        if (!isStopped && recognition) {
            try { recognition.start(); } catch (e) {}
        }

        if (afterSpeak) afterSpeak();
    };

    speechSynthesis.speak(u);
    document.getElementById("assistantText").innerText = text;
}

/* ---------- NUMBER EXTRACTION ---------- */
function extractNumber(text) {
    if (text.includes("first")) return 1;
    if (text.includes("second")) return 2;
    if (text.includes("third")) return 3;
    if (text.includes("fourth")) return 4;
    if (text.includes("fifth")) return 5;

    const n = text.match(/\d+/);
    return n ? parseInt(n[0]) : null;
}

/* ---------- COMMAND HANDLER ---------- */
function handleCommand(cmd) {
    if (isStopped || isSpeaking) return;

    if (cmd.includes("inbox")) fetchFolder("inbox");

    else if (cmd.includes("sent") || cmd.includes("saint") || cmd.includes("send"))
        fetchFolder("sent");

    else if (cmd.includes("trash")) fetchFolder("trash");

    else if (cmd.includes("read")) {
        const n = extractNumber(cmd);

        if (!currentFolder || emails.length === 0) {
            speak("Please open inbox, sent, or trash first");
            return;
        }

        if (!n || !emails[n - 1]) {
            speak("Invalid email number");
            return;
        }

        const m = emails[n - 1];
        speak(`From ${m.from}. Subject ${m.subject}. Message says ${m.body}`);
    }

    else if (cmd.includes("summary")) {
        fetch(`/api/email/ai/0`)
            .then(r => r.json())
            .then(d => speak("Summary. " + d.summary));
    }

    else if (cmd.includes("reply") || cmd.includes("suggest")) {
        fetch(`/api/email/ai/0`)
            .then(r => r.json())
            .then(d => speak("Suggested reply. " + d.reply));
    }

    else if (cmd.includes("hindi")) {
        currentLang = "hi-IN";
        speak("भाषा हिंदी में बदल दी गई है");
    }

    else if (cmd.includes("english")) {
        currentLang = "en-IN";
        speak("Language switched to English");
    }

    else if (cmd.includes("compose")) {
        speak("Opening compose email", () => {
            window.location.href = "/voice-mail";
        });
    }

    else if (cmd.includes("logout")) {
        speak("Logging out", () => {
            location.href = "/logout";
        });
    }

    else {
        speak("Command not recognized");
    }
}

/* ---------- FETCH FOLDER ---------- */
function fetchFolder(folder) {
    speak(`Opening ${folder}`);

    fetch(`/api/gmail/${folder}`)
        .then(r => r.json())
        .then(d => {
            if (!d.success) {
                speak("Unable to fetch emails");
                return;
            }

            emails = d.emails;
            currentFolder = folder;

            const panel = document.getElementById("sectionContent");
            panel.innerHTML = "";

            if (emails.length === 0) {
                panel.innerHTML = "<p>No emails found.</p>";
                speak(`No emails in ${folder}`);
                return;
            }

            emails.forEach((m, i) => {
                panel.innerHTML += `
                  <div class="email-item">
                    <b>${i + 1}. ${m.subject || "No subject"}</b><br>
                    <small>From: ${m.from}</small>
                  </div>`;
            });

            speak(
                `You have ${emails.length} emails in ${folder}. 
                 Say read first email, read second email, and so on.`
            );
        });
}

/* ---------- CONTINUOUS LISTENING ---------- */
function startContinuousListening() {
    const API = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new API();
    recognition.lang = currentLang;
    recognition.continuous = true;
    recognition.interimResults = false;

    recognition.onresult = (event) => {
        if (isSpeaking) return;

        const speech =
            event.results[event.results.length - 1][0]
                .transcript
                .toLowerCase()
                .trim();

        document.getElementById("recognizedText").innerText = speech;
        handleCommand(speech);
    };

    recognition.onend = () => {
        if (!isStopped && !isSpeaking) {
            recognition.start();
        }
    };

    recognition.start();
}

/* ---------- START ---------- */
window.onload = () => {
    startContinuousListening();
};






function loadTelegram() {
  fetch("/api/telegram/messages")
    .then(res => res.json())
    .then(data => {
      const box = document.getElementById("telegramBox");
      box.innerHTML = "";

      if (!data.messages || data.messages.length === 0) {
        box.innerHTML = "<p>No Telegram messages yet.</p>";
        return;
      }

      data.messages.slice().reverse().forEach(m => {
        box.innerHTML += `
          <div class="email-item">
            <b>User:</b> ${m.user}<br>
            <b>Message:</b> ${m.message}<br>
            <b>Summary:</b> ${m.summary}<br>
            <b>AI Reply:</b> ${m.reply}
          </div>
        `;
      });
    });
}
