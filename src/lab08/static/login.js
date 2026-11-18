class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

const loginForm = document.querySelector("#login-form");
const statusMessage = document.querySelector("#status");

if (
  !(loginForm instanceof HTMLFormElement) ||
  !(statusMessage instanceof HTMLElement)
) {
  throw new Error("The login page is missing required elements.");
}

function setStatus(message, isError = false) {
  statusMessage.textContent = message;
  statusMessage.classList.toggle("error", isError);
}

function dashboardPath(role) {
  if (role === "student") return "/student";
  if (role === "teacher") return "/teacher";
  return null;
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

async function handleLogin(event) {
  event.preventDefault();
  const formData = new FormData(loginForm);
  const name = String(formData.get("name") || "").trim();
  const password = String(formData.get("password") || "");
  const submitButton = loginForm.querySelector('button[type="submit"]');

  if (!name || !password) {
    setStatus("Enter your name and password.", true);
    return;
  }

  if (submitButton instanceof HTMLButtonElement) submitButton.disabled = true;

  try {
    const user = await request("/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, password }),
    });

    if (!user || typeof user.role !== "string") {
      throw new Error("The server returned an invalid login response.");
    }
    const destination = dashboardPath(user.role);
    if (!destination) {
      setStatus("The admin interface is available at /admin.", true);
      return;
    }

    window.location.assign(destination);
  } catch (error) {
    setStatus(
      error instanceof Error ? error.message : "Could not log in.",
      true,
    );
  } finally {
    if (submitButton instanceof HTMLButtonElement) submitButton.disabled = false;
  }
}

async function restoreDashboardSession() {
  try {
    const user = await request("/me");
    const destination = user && dashboardPath(user.role);
    if (destination) {
      window.location.replace(destination);
    }
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) return;
    setStatus(
      error instanceof Error
        ? `Could not check your session: ${error.message}`
        : "Could not check your session.",
      true,
    );
  }
}

loginForm.addEventListener("submit", handleLogin);
restoreDashboardSession();
