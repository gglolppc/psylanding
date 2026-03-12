document.addEventListener("DOMContentLoaded", () => {
  const editor = document.getElementById("editor");
  const contentInput = document.getElementById("contentInput");
  const toolbar = document.querySelector(".editor-toolbar");
  const form = document.querySelector(".post-form");
  const fontSizeSelect = document.getElementById("fontSizeSelect");
  const coverInput = document.getElementById("coverInput");
  const coverPreview = document.getElementById("coverPreview");
  const previewWrap = document.getElementById("previewWrap");

  if (toolbar && editor) {
    toolbar.addEventListener("click", (e) => {
      const btn = e.target.closest("button[data-cmd]");
      if (!btn) return;

      const cmd = btn.dataset.cmd;
      const value = btn.dataset.value || null;
      document.execCommand(cmd, false, value);
      editor.focus();
    });
  }

  if (fontSizeSelect && editor) {
    fontSizeSelect.addEventListener("change", () => {
      document.execCommand("fontSize", false, fontSizeSelect.value);
      editor.focus();
    });
  }

  if (form && editor && contentInput) {
    form.addEventListener("submit", () => {
      contentInput.value = editor.innerHTML.trim();
    });
  }

  if (coverInput && coverPreview) {
    coverInput.addEventListener("change", () => {
      const file = coverInput.files?.[0];
      if (!file) return;

      const url = URL.createObjectURL(file);
      coverPreview.src = url;
      if (previewWrap) {
        previewWrap.classList.remove("hidden");
      }
    });
  }
});