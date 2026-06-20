const btn = document.getElementById("convertBtn");
const fileInput = document.getElementById("fileInput");
const output = document.getElementById("output");

const progressContainer = document.getElementById("progressContainer");
const progressBar = document.getElementById("progressBar");
const progressText = document.getElementById("progressText");
const statusText = document.getElementById("statusText");

btn.onclick = async () => {
    const file = fileInput.files[0];

    if (!file) {
        alert("Please select a file.");
        return;
    }

    output.value = "";

    progressContainer.style.display = "block";
    progressBar.style.width = "0%";
    progressText.innerText = "0%";
    statusText.innerText = "Preparing upload...";

    const formData = new FormData();
    formData.append("file", file);

    const xhr = new XMLHttpRequest();

    xhr.upload.addEventListener("progress", (event) => {
        if (event.lengthComputable) {
            const percent = Math.round(
                (event.loaded / event.total) * 100
            );

            progressBar.style.width = percent + "%";
            progressText.innerText = percent + "%";

            statusText.innerText =
                `Uploading ${percent}%`;
        }
    });

    xhr.addEventListener("loadstart", () => {
        statusText.innerText = "Starting upload...";
    });

    xhr.onreadystatechange = () => {
        if (xhr.readyState === 2) {
            statusText.innerText =
                "Upload complete. Converting document...";
        }
    };

    xhr.onload = () => {
        if (xhr.status === 200) {
            const data = JSON.parse(xhr.responseText);

            output.value =
                data.markdown ||
                data.result ||
                JSON.stringify(data, null, 2);

            progressBar.style.width = "100%";
            progressText.innerText = "100%";

            statusText.innerText =
                "Conversion completed.";
        } else {
            statusText.innerText =
                "Conversion failed.";

            console.error(xhr.responseText);
        }
    };

    xhr.onerror = () => {
        statusText.innerText =
            "Network error.";

        console.error(xhr.responseText);
    };

    xhr.open("POST", "/convert");
    xhr.send(formData);
};

document.getElementById("copyBtn").onclick = async () => {
    await navigator.clipboard.writeText(output.value);

    const btn = document.getElementById("copyBtn");

    const original = btn.innerText;

    btn.innerText = "Copied";

    setTimeout(() => {
        btn.innerText = original;
    }, 1500);
};