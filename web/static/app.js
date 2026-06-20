const btn = document.getElementById("convertBtn");
const fileInput = document.getElementById("fileInput");
const output = document.getElementById("output");

btn.onclick = async () => {
  const file = fileInput.files[0];

  if (!file) return;

  const form = new FormData();
  form.append("file", file);

  const response = await fetch("/convert", {
    method: "POST",
    body: form
  });

  const data = await response.json();

  output.value = data.markdown;
};

document.getElementById("copyBtn").onclick = () => {
  navigator.clipboard.writeText(output.value);
};
