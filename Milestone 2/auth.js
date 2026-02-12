const emailInput = document.getElementById("email");
const passwordInput = document.getElementById("password");
const registerBtn = document.getElementById("registerBtn");
const captureBtn = document.getElementById("captureBtn");

const video = document.getElementById("video");
const canvas = document.getElementById("canvas");
const previewImg = document.getElementById("capturedImage");

let faceImage = null;
let cameraReady = false;

/* ---------- CAMERA START ---------- */
navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
        video.srcObject = stream;
        video.onloadedmetadata = () => {
            video.play();
            cameraReady = true;
        };
    })
    .catch(() => alert("Camera permission required"));

/* ---------- CAPTURE FACE (ONE TIME) ---------- */
function captureFace() {
    if (!cameraReady) {
        alert("Camera not ready");
        return;
    }

    if (faceImage) {
        alert("Face already captured");
        return;
    }

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    canvas.getContext("2d").drawImage(video, 0, 0);
    faceImage = canvas.toDataURL("image/jpeg");

    previewImg.src = faceImage;
    previewImg.style.display = "block";
    video.style.display = "none";

    // stop camera
    video.srcObject.getTracks().forEach(t => t.stop());

    captureBtn.disabled = true;
    alert("Face captured successfully");
}

/* ---------- REGISTER ---------- */
registerBtn.onclick = () => {
    const email = emailInput.value.trim();
    const password = passwordInput.value.trim();

    if (!email || !password || !faceImage) {
        alert("Email, password and face are required");
        return;
    }

    fetch("/api/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password, image: faceImage })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            alert("Registration successful");
            window.location.href = "/login";
        } else {
            alert(data.message);
        }
    });
};

/* ---------- PASSWORD TOGGLE ---------- */
function togglePassword() {
    passwordInput.type =
        passwordInput.type === "password" ? "text" : "password";
}

/* ---------- VOICE COMMANDS ---------- */
const SpeechRecognition =
    window.SpeechRecognition || window.webkitSpeechRecognition;

if (SpeechRecognition) {
    const recog = new SpeechRecognition();
    recog.lang = "en-US";
    recog.continuous = true;

    recog.onresult = e => {
        const text =
            e.results[e.results.length - 1][0].transcript
                .toLowerCase().trim();

        if (text.startsWith("email"))
            emailInput.value = text.replace("email", "").trim();

        if (text.startsWith("password"))
            passwordInput.value = text.replace("password", "").trim();

        if (text.includes("capture face")) captureFace();

        if (text.includes("register")) registerBtn.click();
    };

    recog.start();
}



function togglePassword() {
    const pwd = document.getElementById("password");
    pwd.type = pwd.type === "password" ? "text" : "password";
}
function togglePassword() {
    const pwd = document.getElementById("password");
    if (!pwd) return;
    pwd.type = pwd.type === "password" ? "text" : "password";
}
