function showClassMessage(classList, message) {
  const row = document.createElement("tr");
  const cell = document.createElement("td");
  cell.colSpan = 4;
  cell.className = "table-placeholder";
  cell.textContent = message;
  row.append(cell);
  classList.replaceChildren(row);
}

function showRosterMessage(rosterList, message) {
  const row = document.createElement("tr");
  const cell = document.createElement("td");
  cell.colSpan = 3;
  cell.className = "table-placeholder";
  cell.textContent = message;
  row.append(cell);
  rosterList.replaceChildren(row);
}

async function loadRoster(courseId) {
  const rosterList = document.querySelector("#roster-list");
  const selectedCourse = document.querySelector("#selected-course");
  const rosterStatus = document.querySelector("#roster-status");

  if (!rosterList || !selectedCourse || !rosterStatus) {
    throw new Error("The roster section is missing.");
  }

  selectedCourse.textContent = "Loading roster…";
  rosterStatus.textContent = "";
  showRosterMessage(rosterList, "Loading students…");

  try {
    const response = await fetch(
      `/grades/${encodeURIComponent(courseId)}/students`,
    );

    if (response.status === 401) {
      throw new Error("Please sign in as a teacher.");
    }
    if (response.status === 403) {
      throw new Error("You are not authorized to view this roster.");
    }
    if (!response.ok) {
      throw new Error(`Request failed (${response.status}).`);
    }

    const data = await response.json();
    if (
      !data ||
      typeof data.course_name !== "string" ||
      !Array.isArray(data.students)
    ) {
      throw new Error("The server returned an invalid roster.");
    }

    selectedCourse.textContent = `${data.course_name} roster`;

    if (data.students.length === 0) {
      rosterStatus.textContent = "No students are enrolled in this class.";
      showRosterMessage(rosterList, "No students enrolled.");
      return;
    }

    rosterStatus.textContent = `${data.students.length} students loaded.`;
    rosterList.replaceChildren();

    for (const student of data.students) {
      if (
        !student ||
        !Number.isInteger(student.id) ||
        typeof student.name !== "string" ||
        typeof student.grade !== "number"
      ) {
        throw new Error("The server returned an invalid student record.");
      }

      const row = document.createElement("tr");
      const nameCell = document.createElement("th");
      const gradeCell = document.createElement("td");
      const actionCell = document.createElement("td");

      row.dataset.courseId = String(courseId);
      row.dataset.studentId = String(student.id);
      nameCell.scope = "row";
      nameCell.textContent = student.name;
      gradeCell.className = "grade-value";
      gradeCell.textContent = String(student.grade);
      actionCell.append(
        makeButton(
          "Edit",
          "button-secondary",
          "edit-grade",
          student.name,
        ),
      );

      row.append(nameCell, gradeCell, actionCell);
      rosterList.append(row);
    }
  } catch (error) {
    const message =
      error instanceof Error ? error.message : "Unknown error.";
    selectedCourse.textContent = "Roster unavailable";
    rosterStatus.textContent = message;
    showRosterMessage(rosterList, message);
  }
}

async function loadCourses() {
  const classList = document.querySelector("#class-list");
  if (!classList) {
    throw new Error("The class list table is missing.");
  }

  try {
    const response = await fetch("/my-courses");
    if (!response.ok) {
      throw new Error(`Request failed (${response.status}).`);
    }

    const courses = await response.json();
    if (!Array.isArray(courses)) {
      throw new Error("The server returned an invalid course list.");
    }

    if (courses.length === 0) {
      showClassMessage(classList, "No classes found for this teacher.");
      return;
    }

    classList.replaceChildren();

    for (const course of courses) {
      const row = document.createElement("tr");
      const nameCell = document.createElement("th");
      const timeCell = document.createElement("td");
      const capacityCell = document.createElement("td");
      const actionCell = document.createElement("td");
      const viewLink = document.createElement("a");

      nameCell.scope = "row";
      nameCell.textContent = course.name;
      timeCell.textContent = course.time;
      capacityCell.textContent = String(course.capacity);

      viewLink.className = "button button-secondary view-roster";
      viewLink.href = "#roster-heading";
      viewLink.dataset.courseId = String(course.id);
      viewLink.textContent = "View roster";

      actionCell.append(viewLink);
      row.append(nameCell, timeCell, capacityCell, actionCell);
      classList.append(row);
    }
  } catch (error) {
    const message =
      error instanceof Error ? error.message : "Unknown error.";
    showClassMessage(classList, `Could not load classes: ${message}`);
  }
}

loadCourses();// Delegate clicks so newly created Save and Cancel buttons use the same handler.
document.addEventListener("click", (event) => {
  if (!(event.target instanceof Element)) return;
  const viewLink = event.target.closest("a.view-roster");
    if (viewLink) {
        loadRoster(viewLink.dataset.courseId);
        return;
    }

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

function makeButton(label, buttonClass, action, studentName) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = `button ${buttonClass} ${action}`;
  button.textContent = label;
  button.dataset.studentName = studentName;
  return button;
}

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

function finishEditing(row, grade) {
  const gradeCell = row.querySelector(".grade-value");
  const actionCell = row.querySelector("td:last-child");
  const nameCell = row.querySelector("th");
  if (!gradeCell || !actionCell || !nameCell) return;

  gradeCell.textContent = grade;
  actionCell.replaceChildren(
    makeButton(
      "Edit",
      "button-secondary",
      "edit-grade",
      nameCell.textContent.trim(),
    ),
  );
}

function cancelEditing(button) {
  const row = button.closest("tr");
  const input = row?.querySelector(".grade-value input");
  const actionCell = button.closest("td");
  const nameCell = row?.querySelector("th");
  if (!row || !input || !actionCell || !nameCell) return;

  const originalGrade = input.dataset.originalGrade;
  if (originalGrade === undefined) return;

  row.querySelector(".grade-value").textContent = originalGrade;
  actionCell.replaceChildren(
    makeButton(
      "Edit",
      "button-secondary",
      "edit-grade",
      nameCell.textContent.trim(),
    ),
  );
}

function readCookie(name) {
  const prefix = `${name}=`;
  const cookie = document.cookie
    .split("; ")
    .find((item) => item.startsWith(prefix));

  return cookie ? decodeURIComponent(cookie.slice(prefix.length)) : null;
}

async function saveGrade(button) {
  const row = button.closest("tr");
  const input = row?.querySelector(".grade-value input");
  const status = document.querySelector("#roster-status");

  if (!row || !input || !input.reportValidity()) return;

  const { courseId, studentId } = row.dataset;
  if (!courseId || !studentId) {
    status.textContent = "The course or student ID is missing.";
    return;
  }

  const headers = { "Content-Type": "application/json" };
  const csrfToken = readCookie("csrf_access_token");
  if (csrfToken) {
    headers["X-CSRF-TOKEN"] = csrfToken;
  }

  button.disabled = true;

  try {
    const response = await fetch(
      `/grades/${encodeURIComponent(courseId)}/students/${encodeURIComponent(studentId)}/grade`,
      {
        method: "PUT",
        credentials: "same-origin",
        headers,
        body: JSON.stringify({ grade: Number(input.value) }),
      },
    );

    const data = await response.json().catch(() => null);
    if (!response.ok) {
      const detail = data && (data.error || data.msg);
      throw new Error(detail || `Request failed (${response.status}).`);
    }
    if (!data || typeof data.grade !== "number") {
      throw new Error("The server returned an invalid grade.");
    }

    finishEditing(row, String(data.grade));
    status.textContent = `Grade saved for ${data.name}.`;
  } catch (error) {
    status.textContent =
      error instanceof Error ? error.message : "Could not save the grade.";
  } finally {
    button.disabled = false;
  }
}

const logoutForm = document.querySelector("#logout-form");
if (logoutForm instanceof HTMLFormElement) {
  logoutForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const status = document.querySelector("#roster-status");
    const button = logoutForm.querySelector('button[type="submit"]');
    if (button instanceof HTMLButtonElement) button.disabled = true;

    try {
      const response = await fetch("/logout", {
        method: "POST",
        credentials: "same-origin",
      });
      if (!response.ok) {
        throw new Error(`Logout failed (${response.status}).`);
      }
      window.location.assign("/");
    } catch (error) {
      if (status) {
        status.textContent =
          error instanceof Error ? error.message : "Could not log out.";
      }
      if (button instanceof HTMLButtonElement) button.disabled = false;
    }
  });
}
