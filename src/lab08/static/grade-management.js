const API_URL = "/api/Classes";

// Cache the page controls used for search, roster rendering, and grade editing.
const tableBody = document.querySelector("#grade-table-body");
const studentCount = document.querySelector("#student-count");
const rosterStatus = document.querySelector("#roster-status");
const lookupForm = document.querySelector("#lookup-form");
const lookupName = document.querySelector("#lookup-name");
const lookupResult = document.querySelector("#lookup-result");
const gradeForm = document.querySelector("#grade-form");
const studentName = document.querySelector("#class-name");
const studentGrade = document.querySelector("#student-grade");
const saveButton = document.querySelector("#save-button");
const cancelEditButton = document.querySelector("#cancel-edit-button");
const formHint = document.querySelector("#form-hint");
const formStatus = document.querySelector("#form-status");
const refreshButton = document.querySelector("#refresh-button");

let students = [];
let editingName = null;

// Send API requests, parse JSON responses, and report HTTP/service errors.
async function request(path = "", options = {}) {
  const response = await fetch(`${API_URL}${path}`, options);
  const responseText = await response.text();
  let data = null;

  if (responseText) {
    try {
      data = JSON.parse(responseText);
    } catch {
      if (response.ok) {
        throw new Error("The grade service returned an unexpected response.");
      }
    }
  }

  if (!response.ok) {
    const detail =
      data && typeof data === "object" && typeof data.message === "string"
        ? ` ${data.message}`
        : "";
    throw new Error(`Request failed (${response.status}).${detail}`);
  }

  return data;
}

// Show status messages and build table rows safely using text, not HTML strings.
function setStatus(element, message, isError = false) {
  element.textContent = message;
  element.classList.toggle("error", isError);
}

function showTableMessage(message) {
  tableBody.replaceChildren();
  const row = document.createElement("tr");
  const cell = document.createElement("td");
  cell.colSpan = 3;
  cell.className = "table-placeholder";
  cell.textContent = message;
  row.append(cell);
  tableBody.append(row);
}

function makeActionButton(label, className, onClick, student) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = `button ${className}`;
  button.textContent = label;
  button.addEventListener("click", () => onClick(student));
  return button;
}

function renderStudents() {
  tableBody.replaceChildren();
  studentCount.textContent = `${students.length} ${
    students.length === 1 ? "student" : "students"
  }`;

  if (students.length === 0) {
    showTableMessage("No student records are available.");
    return;
  }

  for (const student of students) {
    const row = document.createElement("tr");
    const nameCell = document.createElement("td");
    const gradeCell = document.createElement("td");
    const actionsCell = document.createElement("td");
    const actions = document.createElement("div");

    nameCell.textContent = student.name;
    gradeCell.className = "grade-cell";
    gradeCell.textContent = String(student.grade);
    actions.className = "row-actions";
    actions.append(
      makeActionButton("Edit", "button-secondary", startEditing, student),
      makeActionButton("Delete", "button-danger", deleteStudent, student),
    );
    actionsCell.append(actions);
    row.append(nameCell, gradeCell, actionsCell);
    tableBody.append(row);
  }
}

// Fetch the full class roster and update the count, table, or error message.
async function loadStudents() {
  refreshButton.disabled = true;
  setStatus(rosterStatus, "Loading class roster…");
  studentCount.textContent = "Loading…";

  try {
    const data = await request();
    if (!data || typeof data !== "object" || Array.isArray(data)) {
      throw new Error("The grade service returned an invalid class roster.");
    }

    students = Object.entries(data)
      .filter(([, grade]) => typeof grade === "number" && Number.isFinite(grade))
      .map(([name, grade]) => ({ name, grade }))
      .sort((first, second) => first.name.localeCompare(second.name));
    renderStudents();
    setStatus(rosterStatus, "");
  } catch (error) {
    students = [];
    studentCount.textContent = "Unavailable";
    showTableMessage("Could not load the class roster.");
    setStatus(rosterStatus, error.message, true);
  } finally {
    refreshButton.disabled = false;
  }
}

// Request one student's record and display the grade without exposing JSON.
async function lookUpStudent(event) {
  event.preventDefault();
  const name = lookupName.value;
  lookupResult.replaceChildren();
  lookupResult.classList.remove("lookup-error");

  try {
    const data = await request(`/${encodeURIComponent(name)}`);
    if (!data || typeof data !== "object" || Array.isArray(data)) {
      throw new Error("The grade service returned an invalid student record.");
    }

    const grade = Object.hasOwn(data, name) ? data[name] : data.grade;
    if (typeof grade !== "number" || !Number.isFinite(grade)) {
      throw new Error(`No grade was returned for "${name}". Check the spelling and capitalization.`);
    }

    const card = document.createElement("div");
    const resultText = document.createElement("p");
    const gradeText = document.createElement("p");
    card.className = "lookup-card";
    resultText.textContent = `Grade for ${name}`;
    gradeText.className = "lookup-grade";
    gradeText.textContent = String(grade);
    card.append(resultText, gradeText);
    lookupResult.append(card);
  } catch (error) {
    lookupResult.textContent = error.message;
    lookupResult.classList.add("lookup-error");
  }
}

// Fill the grade form with a roster entry and allow its grade to be changed.
function startEditing(student) {
  editingName = student.name;
  studentName.value = student.name;
  studentName.readOnly = true;
  studentGrade.value = String(student.grade);
  saveButton.textContent = "Save grade";
  cancelEditButton.hidden = false;
  formHint.textContent = `Editing ${student.name}. Student names are case sensitive.`;
  setStatus(formStatus, "");
  studentGrade.focus();
  gradeForm.scrollIntoView({ behavior: "smooth", block: "center" });
}

// Return the grade form to its create-new-student state.
function cancelEditing() {
  editingName = null;
  gradeForm.reset();
  studentName.readOnly = false;
  saveButton.textContent = "Add student";
  cancelEditButton.hidden = true;
  formHint.textContent =
    "To update a grade, choose Edit in the roster. Student names are case sensitive.";
  setStatus(formStatus, "");
}

// Validate the form, then create a student with POST or update one with PUT.
async function saveGrade(event) {
  event.preventDefault();
  const name = studentName.value;
  const grade = Number(studentGrade.value);

  if (!name.trim()) {
    setStatus(formStatus, "Enter a student name.", true);
    studentName.focus();
    return;
  }

  if (studentGrade.value === "" || !Number.isFinite(grade) || grade < 0 || grade > 100) {
    setStatus(formStatus, "Enter a grade from 0 to 100.", true);
    studentGrade.focus();
    return;
  }

  const isEditing = editingName !== null;
  const path = isEditing ? `/${encodeURIComponent(editingName)}` : "";
  const method = isEditing ? "PUT" : "POST";
  const body = isEditing ? { grade } : { name, grade };
  saveButton.disabled = true;
  setStatus(formStatus, isEditing ? "Updating grade…" : "Adding student…");

  try {
    await request(path, {
      method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    cancelEditing();
    setStatus(formStatus, isEditing ? "Grade updated." : "Student added.");
    await loadStudents();
  } catch (error) {
    setStatus(formStatus, error.message, true);
  } finally {
    saveButton.disabled = false;
  }
}

// Confirm deletions and refresh the roster afterward.
async function deleteStudent(student) {
  const confirmed = window.confirm(
    `Delete the grade record for ${student.name}?`,
  );
  if (!confirmed) {
    return;
  }

  setStatus(rosterStatus, `Deleting ${student.name}…`);
  try {
    await request(`/${encodeURIComponent(student.name)}`, { method: "DELETE" });
    if (editingName === student.name) {
      cancelEditing();
    }
    setStatus(rosterStatus, `Deleted the grade record for ${student.name}.`);
    await loadStudents();
  } catch (error) {
    setStatus(rosterStatus, error.message, true);
  }
}

// Connect the interface controls to their handlers and load the initial roster.
lookupForm.addEventListener("submit", lookUpStudent);
gradeForm.addEventListener("submit", saveGrade);
cancelEditButton.addEventListener("click", cancelEditing);
refreshButton.addEventListener("click", loadStudents);

loadStudents();
