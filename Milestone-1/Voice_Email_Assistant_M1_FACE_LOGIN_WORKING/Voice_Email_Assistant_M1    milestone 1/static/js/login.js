document.getElementById("loginBtn").onclick = async () => {
    const email = email.value;
    const password = password.value;

    const res = await fetch("/api/login",{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({email,password})
    });

    const data = await res.json();
    if(data.success) alert("Now login with face");
};

document.getElementById("faceLoginBtn").onclick = async () => {
    const res = await fetch("/api/face-login",{method:"POST"});
    const data = await res.json();
    if(data.success) location.href="/dashboard";
    else alert("Face not matched");
};
