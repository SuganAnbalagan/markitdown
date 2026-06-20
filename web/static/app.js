const fileInput = document.getElementById("fileInput");
const selectedFile = document.getElementById("selectedFile");
const convertBtn = document.getElementById("convertBtn");
const output = document.getElementById("output");

const progressBar = document.getElementById("progressBar");
const progressText = document.getElementById("progressText");
const statusText = document.getElementById("statusText");

fileInput.addEventListener("change", () => {
    if (fileInput.files.length) {
        selectedFile.innerText =
            fileInput.files[0].name;
    }
});

convertBtn.addEventListener("click", () => {

    const file = fileInput.files[0];

    if (!file) {
        alert("Select a file first.");
        return;
    }

    output.value = "";

    const formData = new FormData();
    formData.append("file", file);

    const xhr = new XMLHttpRequest();

    progressBar.style.width = "0%";
    progressText.innerText = "0%";

    xhr.upload.addEventListener("progress", e => {

        if (!e.lengthComputable) return;

        const percent =
            Math.round(
                (e.loaded / e.total) * 100
            );

        progressBar.style.width =
            percent + "%";

        progressText.innerText =
            percent + "%";

        statusText.innerText =
            "Uploading...";
    });

    xhr.onreadystatechange = () => {

        if (xhr.readyState === 2) {

            statusText.innerText =
                "Upload complete. Converting...";

            statusText.classList.add(
                "converting"
            );
        }
    };

    xhr.onload = () => {

        statusText.classList.remove(
            "converting"
        );

        if (xhr.status !== 200) {

            statusText.innerText =
                "Conversion failed";

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
            `Done in ${response.conversion_time}s`;
    };

    xhr.onerror = () => {

        statusText.classList.remove(
            "converting"
        );

        statusText.innerText =
            "Network error";
    };

    xhr.open(
        "POST",
        "/convert"
    );

    xhr.send(formData);
});

document
.getElementById("copyBtn")
.addEventListener("click", async () => {

    await navigator.clipboard.writeText(
        output.value
    );

    const btn =
        document.getElementById(
            "copyBtn"
        );

    btn.innerText = "Copied";

    setTimeout(() => {
        btn.innerText = "Copy";
    }, 1500);
});