const fileInput = document.getElementById("fileInput");
const selectedFile = document.getElementById("selectedFile");
const fileMeta = document.getElementById("fileMeta");

const convertBtn = document.getElementById("convertBtn");
const output = document.getElementById("output");

const progressBar = document.getElementById("progressBar");
const progressText = document.getElementById("progressText");
const statusText = document.getElementById("statusText");
const speedText = document.getElementById("speedText");
const timerText = document.getElementById("timerText");

const historyDiv = document.getElementById("history");

let currentFilename = "output";

function formatSize(bytes) {

    const units = ["B", "KB", "MB", "GB"];

    let i = 0;

    while (bytes >= 1024 && i < units.length - 1) {
        bytes /= 1024;
        i++;
    }

    return bytes.toFixed(1) + " " + units[i];
}

function renderHistory() {

    const items =
        JSON.parse(
            localStorage.getItem("history") || "[]"
        );

    historyDiv.innerHTML = "";

    items.slice(0, 10).forEach(item => {

        const div =
            document.createElement("div");

        div.className = "history-item";

        div.innerHTML =
            `<strong>${item.name}</strong><br>
             ${item.time}`;

        historyDiv.appendChild(div);
    });
}

renderHistory();

fileInput.addEventListener("change", () => {

    const file = fileInput.files[0];

    if (!file) return;

    currentFilename = file.name;

    selectedFile.innerText = file.name;

    fileMeta.innerText =
        formatSize(file.size);
});

const dropzone =
    document.getElementById("dropzone");

dropzone.addEventListener("dragover", e => {

    e.preventDefault();

    dropzone.classList.add("dragging");
});

dropzone.addEventListener("dragleave", () => {

    dropzone.classList.remove("dragging");
});

dropzone.addEventListener("drop", e => {

    e.preventDefault();

    dropzone.classList.remove("dragging");

    fileInput.files = e.dataTransfer.files;

    fileInput.dispatchEvent(
        new Event("change")
    );
});

convertBtn.addEventListener("click", () => {

    const file = fileInput.files[0];

    if (!file) return;

    const formData =
        new FormData();

    formData.append(
        "file",
        file
    );

    output.value = "";

    let startTime =
        Date.now();

    let timer =
        setInterval(() => {

            timerText.innerText =
                Math.floor(
                    (Date.now() - startTime)
                    / 1000
                ) + "s";

        }, 1000);

    const xhr =
        new XMLHttpRequest();

    xhr.upload.onprogress = e => {

        if (!e.lengthComputable)
            return;

        const percent =
            Math.round(
                (e.loaded / e.total) * 100
            );

        progressBar.style.width =
            percent + "%";

        progressText.innerText =
            percent + "%";

        const elapsed =
            (Date.now() - startTime) / 1000;

        const speed =
            e.loaded / elapsed;

        speedText.innerText =
            formatSize(speed) + "/s";

        statusText.innerText =
            "Uploading";
    };

    xhr.onreadystatechange = () => {

        if (xhr.readyState === 2) {

            statusText.innerText =
                "Converting";

            progressBar.classList.add(
                "converting"
            );
        }
    };

    xhr.onload = () => {

        clearInterval(timer);

        progressBar.classList.remove(
            "converting"
        );

        if (xhr.status !== 200) {

            statusText.innerText =
                "Failed";

            return;
        }

        const response =
            JSON.parse(xhr.responseText);

        output.value =
            response.markdown || "";

        progressBar.style.width =
            "100%";

        progressText.innerText =
            "100%";

        statusText.innerText =
            "Complete";

        const history =
            JSON.parse(
                localStorage.getItem("history")
                || "[]"
            );

        history.unshift({
            name: file.name,
            time: new Date()
                .toLocaleString()
        });

        localStorage.setItem(
            "history",
            JSON.stringify(history)
        );

        renderHistory();
    };

    xhr.open(
        "POST",
        "/convert"
    );

    xhr.send(formData);
});

document
.getElementById("copyBtn")
.onclick = async () => {

    await navigator.clipboard.writeText(
        output.value
    );
};

document
.getElementById("downloadBtn")
.onclick = () => {

    const blob =
        new Blob(
            [output.value],
            {type:"text/markdown"}
        );

    const a =
        document.createElement("a");

    a.href =
        URL.createObjectURL(blob);

    a.download =
        currentFilename + ".md";

    a.click();
};