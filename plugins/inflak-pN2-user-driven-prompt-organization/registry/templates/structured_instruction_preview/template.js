(function () {
  document.getElementById("revise").onclick = () => {
    window.submitWidget({ preview_status: "revise" });
  };
  document.getElementById("confirm").onclick = () => {
    window.submitWidget({ preview_status: "confirmed" });
  };
})();