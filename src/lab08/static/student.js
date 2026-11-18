class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

const myClassesBody = document.querySelector("#my-classes-body");
const allClassesBody = document.querySelector("#all-classes-body");
const statusMessage = document.querySelector("#status");
const studentNameDisplay = document.querySelector("#student-name-display");
const refreshButton = document.querySelector("#refresh-button");
const logoutForm = document.querySelector("#logout-form");

if (
  !(myClassesBody instanceof HTMLTableSectionElement) ||
  !(allClassesBody instanceof HTMLTableSectionElement) ||
  !(statusMessage instanceof HTMLElement) ||
  !(studentNameDisplay instanceof HTMLElement) ||
  !(refreshButton instanceof HTMLButtonElement) ||
  !(logoutForm instanceof HTMLFormElement)
) {
  throw new Error("The student dashboard is missing required elements.");
}

async function request(path, options = {}) {
  const response = await fetch(path, {
    credentials: "same-origin",
    ...options,
  });
  const data = await response.json().catch(() => null);

  if (!response.ok) {
    const message =
      data && typeof data.error === "string"
        ? data.error
        : `Request failed (${response.status}).`;
    throw new ApiError(message, response.status);
  }

  return data;
}

function setStatus(message, isError = false) {
  statusMessage.textContent = message;
  statusMessage.classList.toggle("error", isError);
}

function showTableMessage(tableBody, message) {
  const row = document.createElement("tr");
  const cell = document.createElement("td");
  cell.colSpan = 5;
  cell.className = "table-placeholder";
  cell.textContent = message;
  row.append(cell);
  tableBody.replaceChildren(row);
}

function validateCourse(course, includeAvailability) {
  if (
    !course ||
    !Number.isInteger(course.id) ||
    typeof course.name !== "string" ||
    typeof course.teacher !== "string" ||
    typeof course.time !== "string" ||
    typeof course.capacity !== "string" ||
    (includeAvailability &&
      (typeof course.is_full !== "boolean" ||
        typeof course.enrolled !== "boolean"))
  ) {
    throw new Error("The server returned an invalid course record.");
  }
}

function makeCourseRow(course, action) {
  const row = document.createElement("tr");
  const nameCell = document.createElement("th");
  const teacherCell = document.createElement("td");
  const timeCell = document.createElement("td");
  const capacityCell = document.createElement("td");
  const actionCell = document.createElement("td");

  nameCell.scope = "row";
  nameCell.textContent = course.name;
  teacherCell.textContent = course.teacher;
  timeCell.textContent = course.time;
  capacityCell.textContent = course.capacity;

  const button = document.createElement("button");
  button.type = "button";
  button.className = `button ${
    action === "drop" ? "button-danger" : "button-primary"
  }`;
  button.dataset.courseId = String(course.id);

  if (action === "full") {
    button.textContent = "Full";
    button.disabled = true;
  } else {
    button.dataset.action = action;
    button.textContent = action === "drop" ? "Drop" : "Sign up";
  }

  actionCell.append(button);
  row.append(nameCell, teacherCell, timeCell, capacityCell, actionCell);
  return row;
}

function renderMyClasses(courses) {
  myClassesBody.replaceChildren();

  if (courses.length === 0) {
    showTableMessage(myClassesBody, "You are not enrolled in any classes.");
    return;
  }

  for (const course of courses) {
    validateCourse(course, false);
    myClassesBody.append(makeCourseRow(course, "drop"));
  }
}

function renderOtherClasses(courses) {
  allClassesBody.replaceChildren();
  for (const course of courses) {
    validateCourse(course, true);
  }
  const otherCourses = courses.filter((course) => !course.enrolled);

  if (otherCourses.length === 0) {
    showTableMessage(allClassesBody, "There are no other classes offered.");
    return;
  }

  for (const course of otherCourses) {
    allClassesBody.append(
      makeCourseRow(course, course.is_full ? "full" : "enroll"),
    );
  }
}

async function loadClasses(showLoading = true) {
  if (showLoading) {
    setStatus("Loading classes…");
    showTableMessage(myClassesBody, "Loading your classes…");
    showTableMessage(allClassesBody, "Loading other classes…");
  }

  try {
    const [myCourses, allCourses] = await Promise.all([
      request("/my-courses"),
      request("/courses"),
    ]);

    if (!Array.isArray(myCourses) || !Array.isArray(allCourses)) {
      throw new Error("The server returned an invalid course list.");
    }

    renderMyClasses(myCourses);
    renderOtherClasses(allCourses);
    if (showLoading) setStatus("");
    return true;
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) {
      window.location.replace("/");
      return false;
    }

    const message =
      error instanceof Error ? error.message : "Could not load classes.";
    showTableMessage(myClassesBody, "Could not load your classes.");
    showTableMessage(allClassesBody, "Could not load other classes.");
    setStatus(message, true);
    return false;
  }
}

async function handleCourseAction(event) {
  if (!(event.target instanceof Element)) return;
  const button = event.target.closest("button[data-action]");
  if (!(button instanceof HTMLButtonElement)) return;

  const courseId = button.dataset.courseId;
  const action = button.dataset.action;
  if (!courseId || (action !== "enroll" && action !== "drop")) {
    setStatus("The class action is invalid.", true);
    return;
  }

  button.disabled = true;

  try {
    const result =
      action === "enroll"
        ? await request(`/courses/${encodeURIComponent(courseId)}/enrollment`, {
            method: "PUT",
          })
        : await request(`/courses/${encodeURIComponent(courseId)}/leaving`, {
            method: "DELETE",
          });

    const refreshed = await loadClasses(false);
    if (refreshed) {
      setStatus(
        result && typeof result.msg === "string"
          ? result.msg
          : action === "enroll"
            ? "You are enrolled in the class."
            : "You dropped the class.",
      );
    }
  } catch (error) {
    setStatus(
      error instanceof Error ? error.message : "The class action failed.",
      true,
    );
    button.disabled = false;
  }
}

async function handleLogout(event) {
  event.preventDefault();
  const button = logoutForm.querySelector('button[type="submit"]');
  if (button instanceof HTMLButtonElement) button.disabled = true;

  try {
    await request("/logout", { method: "POST" });
    window.location.assign("/");
  } catch (error) {
    setStatus(
      error instanceof Error ? error.message : "Could not log out.",
      true,
    );
    if (button instanceof HTMLButtonElement) button.disabled = false;
  }
}

async function initializeDashboard() {
  try {
    const user = await request("/me");
    if (!user || typeof user.name !== "string" || user.role !== "student") {
      window.location.replace("/");
      return;
    }
    studentNameDisplay.textContent = user.name;
    await loadClasses();
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) {
      window.location.replace("/");
      return;
    }
    setStatus(
      error instanceof Error
        ? `Could not verify your session: ${error.message}`
        : "Could not verify your session.",
      true,
    );
  }
}

myClassesBody.addEventListener("click", handleCourseAction);
allClassesBody.addEventListener("click", handleCourseAction);
refreshButton.addEventListener("click", () => loadClasses());
logoutForm.addEventListener("submit", handleLogout);

initializeDashboard();
