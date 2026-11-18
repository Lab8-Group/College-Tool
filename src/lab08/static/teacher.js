// Delegate clicks so newly created Save and Cancel buttons use the same handler.
document.addEventListener("click", (event) => {
  if (!(event.target instanceof Element)) return;

  const button = event.target.closest("button");
  if (!button) return;

  if (button.classList.contains("edit-grade")) {
    startEditing(button);
  } else if (button.classList.contains("save-grade")) {
    saveGrade(button);
  } else if (button.classList.contains("cancel-grade")) {
    cancelEditing(button);
  }
});

function startEditing(button) {
  const row = button.closest("tr");
  if (!row) return;

  const gradeCell = row.querySelector(".grade-value");
  const actionCell = button.closest("td");
  const nameCell = row.querySelector("th");
  if (!gradeCell || !actionCell || !nameCell) return;

  const studentName = nameCell.textContent.trim();
  const input = document.createElement("input");
  input.type = "number";
  input.min = "0";
  input.max = "100";
  input.step = "any";
  input.required = true;
  input.value = gradeCell.textContent.trim();
  input.dataset.originalGrade = input.value;
  input.setAttribute("aria-label", `Grade for ${studentName}`);

  // Swap the displayed grade and Edit button for an input and its controls.
  gradeCell.replaceChildren(input);
  actionCell.replaceChildren(
    makeButton("Save", "button-primary", "save-grade", studentName),
    makeButton("Cancel", "button-secondary", "cancel-grade", studentName),
  );
  input.focus();
}

function saveGrade(button) {
  const row = button.closest("tr");
  const input = row?.querySelector(".grade-value input");
  // Keep the row in edit mode if the grade is blank or outside 0-100.
  if (!row || !input || !input.reportValidity()) return;

  finishEditing(row, input.value);
}

function cancelEditing(button) {
  const row = button.closest("tr");
  const input = row?.querySelector(".grade-value input");
  if (!row || !input) return;

  // Restore the value captured when editing began.
  finishEditing(row, input.dataset.originalGrade);
}

function finishEditing(row, grade) {
  const gradeCell = row.querySelector(".grade-value");
  const actionCell = row.lastElementChild;
  const nameCell = row.querySelector("th");
  if (!gradeCell || !actionCell || !nameCell) return;

  const studentName = nameCell.textContent.trim();
  gradeCell.textContent = grade;
  // Return the row to its read-only state with an Edit button.
  actionCell.replaceChildren(
    makeButton("Edit", "button-secondary", "edit-grade", studentName),
  );
}

function makeButton(label, styleClass, actionClass, studentName) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = `button ${styleClass} ${actionClass}`;
  button.textContent = label;
  button.setAttribute("aria-label", `${label} grade for ${studentName}`);
  return button;
}