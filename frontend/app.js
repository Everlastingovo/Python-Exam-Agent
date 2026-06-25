const API_HOST = window.location.hostname || "localhost";
const API_BASE = `http://${API_HOST}:8000`;

const state = {
  username: localStorage.getItem("pea_username") || "",
  topics: [],
  currentExam: null,
  currentQuestionIndex: 0,
  submissions: new Map(),
  drafts: new Map(),
  timerId: null,
  examEndsAt: null,
};

const elements = {
  loginView: document.querySelector("#loginView"),
  appView: document.querySelector("#appView"),
  loginForm: document.querySelector("#loginForm"),
  usernameInput: document.querySelector("#usernameInput"),
  passwordInput: document.querySelector("#passwordInput"),
  userLabel: document.querySelector("#userLabel"),
  logoutButton: document.querySelector("#logoutButton"),
  tabs: document.querySelectorAll(".tab"),
  sections: document.querySelectorAll(".view-section"),
  topicCount: document.querySelector("#topicCount"),
  examForm: document.querySelector("#examForm"),
  aiForm: document.querySelector("#aiForm"),
  apiKeyInput: document.querySelector("#apiKeyInput"),
  modelSelect: document.querySelector("#modelSelect"),
  aiResultList: document.querySelector("#aiResultList"),
  timerDisplay: document.querySelector("#timerDisplay"),
  scoreDisplay: document.querySelector("#scoreDisplay"),
  examWorkspace: document.querySelector("#examWorkspace"),
  examTitle: document.querySelector("#examTitle"),
  questionList: document.querySelector("#questionList"),
  prevQuestionButton: document.querySelector("#prevQuestionButton"),
  nextQuestionButton: document.querySelector("#nextQuestionButton"),
  questionProgress: document.querySelector("#questionProgress"),
  finishExamButton: document.querySelector("#finishExamButton"),
  finalFeedback: document.querySelector("#finalFeedback"),
  wrongList: document.querySelector("#wrongList"),
  historyList: document.querySelector("#historyList"),
  refreshWrongButton: document.querySelector("#refreshWrongButton"),
  refreshHistoryButton: document.querySelector("#refreshHistoryButton"),
  homeStartButton: document.querySelector("#homeStartButton"),
  homeWrongButton: document.querySelector("#homeWrongButton"),
  toast: document.querySelector("#toast"),
};

init();

function init() {
  bindEvents();
  updateAuthView();
  if (state.username) {
    loadTopics();
  }
}

function bindEvents() {
  elements.loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const username = elements.usernameInput.value.trim();
    const password = elements.passwordInput.value;
    if (!username || !password) {
      showToast("Please enter a username and password.");
      return;
    }
    try {
      const result = await apiPost("/login", { username, password });
      state.username = result.username;
      localStorage.setItem("pea_username", result.username);
      elements.passwordInput.value = "";
      updateAuthView();
      loadTopics();
      showToast("Login successful.");
    } catch (error) {
      showToast(error.message);
    }
  });

  elements.logoutButton.addEventListener("click", () => {
    localStorage.removeItem("pea_username");
    state.username = "";
    state.currentExam = null;
    state.submissions.clear();
    stopTimer();
    updateAuthView();
  });

  elements.tabs.forEach((tab) => {
    tab.addEventListener("click", () => showSection(tab.dataset.view));
  });

  elements.homeStartButton.addEventListener("click", () => showSection("examSection"));
  elements.homeWrongButton.addEventListener("click", () => {
    showSection("wrongSection");
    loadWrongQuestions();
  });

  elements.examForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    await generateExam();
  });
  elements.aiForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    await generateAiQuestions();
  });

  elements.finishExamButton.addEventListener("click", finishExam);
  elements.prevQuestionButton.addEventListener("click", () => moveQuestion(-1));
  elements.nextQuestionButton.addEventListener("click", () => moveQuestion(1));
  elements.refreshWrongButton.addEventListener("click", loadWrongQuestions);
  elements.refreshHistoryButton.addEventListener("click", loadHistory);
}

function updateAuthView() {
  const isLoggedIn = Boolean(state.username);
  elements.loginView.classList.toggle("hidden", isLoggedIn);
  elements.appView.classList.toggle("hidden", !isLoggedIn);
  elements.logoutButton.classList.toggle("hidden", !isLoggedIn);
  elements.userLabel.textContent = isLoggedIn ? `Logged in as ${state.username}` : "Not logged in";
  if (isLoggedIn) {
    showSection("homeSection");
  }
}

function showSection(sectionId) {
  elements.sections.forEach((section) => {
    section.classList.toggle("hidden", section.id !== sectionId);
  });
  elements.tabs.forEach((tab) => {
    tab.classList.toggle("active", tab.dataset.view === sectionId);
  });
  if (sectionId === "wrongSection") {
    loadWrongQuestions();
  }
  if (sectionId === "historySection") {
    loadHistory();
  }
}

async function loadTopics() {
  try {
    const data = await apiGet("/topics");
    state.topics = data.topics || [];
    elements.topicCount.textContent = `${state.topics.length} available`;
  } catch (error) {
    showToast(error.message);
  }
}

async function generateExam() {
  try {
    const exam = await apiPost("/generate-exam", {
      topic: "__all__",
      difficulty: "mixed",
      number_of_questions: 8,
      username: state.username,
    });
    state.currentExam = exam;
    state.currentQuestionIndex = 0;
    state.submissions.clear();
    state.drafts.clear();
    elements.finalFeedback.classList.add("hidden");
    elements.examWorkspace.classList.remove("hidden");
    elements.examTitle.textContent = `${exam.topic} exam #${exam.exam_id}`;
    renderQuestions(exam.questions);
    updateScore();
    startTimer(90);
    showToast("Timed exam started. You have 90 minutes.");
  } catch (error) {
    showToast(error.message);
  }
}

function renderQuestions(questions) {
  renderCurrentQuestion();
}

function moveQuestion(direction) {
  if (!state.currentExam) {
    return;
  }
  saveCurrentDraft();
  const nextIndex = state.currentQuestionIndex + direction;
  if (nextIndex < 0 || nextIndex >= state.currentExam.questions.length) {
    return;
  }
  state.currentQuestionIndex = nextIndex;
  renderCurrentQuestion();
}

function renderCurrentQuestion() {
  const questions = state.currentExam?.questions || [];
  if (!questions.length) {
    elements.questionList.innerHTML = "";
    return;
  }

  const question = questions[state.currentQuestionIndex];
  elements.questionProgress.textContent = `Question ${state.currentQuestionIndex + 1} of ${questions.length}`;
  elements.prevQuestionButton.disabled = state.currentQuestionIndex === 0;
  elements.nextQuestionButton.disabled = state.currentQuestionIndex === questions.length - 1;
  elements.questionList.innerHTML = questionTemplate(question, state.currentQuestionIndex);
  const button = document.querySelector(`[data-submit-question="${question.id}"]`);
  button.addEventListener("click", () => submitAnswer(question.id));
}

function saveCurrentDraft() {
  const question = state.currentExam?.questions[state.currentQuestionIndex];
  if (!question) {
    return;
  }
  const textarea = document.querySelector(`#code-${question.id}`);
  if (textarea) {
    state.drafts.set(question.id, textarea.value);
  }
}

function questionTemplate(question, index) {
  return `
    <article class="question-card" id="question-${question.id}">
      <div>
        <div class="question-meta">
          <span>Question ${index + 1}</span>
          <span>${escapeHtml(question.topic)}</span>
          <span class="difficulty-tag ${escapeHtml(question.difficulty)}">${escapeHtml(question.difficulty)}</span>
          <span>${escapeHtml(question.function_signature)}</span>
        </div>
        <h3>${escapeHtml(question.title)}</h3>
        <p>${escapeHtml(question.description)}</p>
      </div>
      <div class="examples-panel">
        <h4>Examples</h4>
        ${renderExamples(question.examples || [])}
      </div>
      <div class="editor-shell">
        <div class="editor-header">
          <span>submission.py</span>
          <span>Python</span>
        </div>
        <textarea id="code-${question.id}" spellcheck="false">${escapeHtml(state.drafts.get(question.id) || question.starter_code)}</textarea>
      </div>
      <div>
        <button type="button" data-submit-question="${question.id}">Compile & Run Tests</button>
      </div>
      <div id="output-${question.id}" class="output-panel hidden"></div>
    </article>
  `;
}

function renderExamples(examples) {
  if (!examples.length) {
    return `<pre>No visible examples.</pre>`;
  }
  return examples
    .map((example, index) => (
      `<pre>Example ${index + 1}\nInput: ${escapeHtml(JSON.stringify(example.input))}\nExpected: ${escapeHtml(JSON.stringify(example.expected))}</pre>`
    ))
    .join("");
}

async function submitAnswer(questionId) {
  if (!state.currentExam) {
    showToast("Please generate an exam first.");
    return;
  }

  const textarea = document.querySelector(`#code-${questionId}`);
  const output = document.querySelector(`#output-${questionId}`);
  const code = textarea.value.trim();
  if (!code) {
    showToast("Please enter code before submitting.");
    return;
  }

  try {
    output.classList.remove("hidden");
    output.innerHTML = "<h4>Output</h4><pre>Running tests...</pre>";
    const result = await apiPost("/submit-answer", {
      exam_id: state.currentExam.exam_id,
      question_id: questionId,
      code,
    });
    state.drafts.set(questionId, textarea.value);
    state.submissions.set(questionId, result);
    output.innerHTML = renderSubmissionOutput(result);
    updateScore();
  } catch (error) {
    output.classList.remove("hidden");
    output.innerHTML = `<h4>Output</h4><pre>${escapeHtml(error.message)}</pre>`;
  }
}

function renderSubmissionOutput(result) {
  const statusClass = result.is_correct ? "pass" : "fail";
  const statusText = result.is_correct ? "Correct" : "Incorrect";
  const tests = result.test_results
    .map((test, index) => {
      const fileResults = (test.file_results || [])
        .map((file) => `File ${file.file}: ${file.passed ? "passed" : "failed"}`)
        .join("\n");
      const caseType = test.hidden ? "Backend edge case" : "Visible test";
      return [
        `${caseType} ${index + 1}: ${test.passed ? "passed" : "failed"}`,
        test.hidden ? "" : `Input: ${JSON.stringify(test.input)}`,
        test.hidden ? "" : `Expected: ${JSON.stringify(test.expected)}`,
        test.hidden ? "" : `Actual: ${JSON.stringify(test.actual)}`,
        test.error ? `Error: ${test.error}` : "",
        fileResults,
      ].filter(Boolean).join("\n");
    })
    .join("\n\n");

  return `
    <h4>Output <span class="result-pill ${statusClass}">${statusText}</span></h4>
    <pre>${escapeHtml(result.feedback)}\n\n${escapeHtml(tests)}</pre>
  `;
}

async function finishExam() {
  if (!state.currentExam) {
    showToast("Please generate an exam first.");
    return;
  }

  try {
    const report = await apiPost(`/finish-exam/${state.currentExam.exam_id}`, {});
    stopTimer();
    const passed = report.solved_questions === report.total_questions;
    elements.finalFeedback.classList.remove("hidden");
    elements.finalFeedback.innerHTML = `
      <h3>Final feedback</h3>
      <p><span class="result-pill ${passed ? "pass" : "fail"}">${passed ? "PASS" : "NOT PASS"}</span></p>
      <p><strong>Score:</strong> ${report.solved_questions}/${report.total_questions}</p>
      <p>${escapeHtml(report.summary)}</p>
      <p><strong>Weak topics:</strong> ${escapeHtml(report.weak_topics.join(", ") || "None")}</p>
      <p><strong>Suggestions:</strong></p>
      <ul>${report.suggestions.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>
    `;
    loadHistory();
    updateScore(report.solved_questions, report.total_questions);
    showToast("Exam finished.");
  } catch (error) {
    showToast(error.message);
  }
}

function startTimer(minutes) {
  stopTimer();
  state.examEndsAt = Date.now() + minutes * 60 * 1000;
  renderTimer();
  state.timerId = window.setInterval(() => {
    const remainingMs = state.examEndsAt - Date.now();
    if (remainingMs <= 0) {
      stopTimer();
      elements.timerDisplay.textContent = "00:00";
      elements.timerDisplay.classList.add("warning");
      showToast("Time is up. Finishing exam.");
      finishExam();
      return;
    }
    renderTimer();
  }, 1000);
}

function stopTimer() {
  if (state.timerId) {
    window.clearInterval(state.timerId);
  }
  state.timerId = null;
  state.examEndsAt = null;
}

function renderTimer() {
  if (!state.examEndsAt) {
    elements.timerDisplay.textContent = "90:00";
    elements.timerDisplay.classList.remove("warning");
    return;
  }
  const remainingSeconds = Math.max(0, Math.ceil((state.examEndsAt - Date.now()) / 1000));
  const minutes = Math.floor(remainingSeconds / 60);
  const seconds = remainingSeconds % 60;
  elements.timerDisplay.textContent = `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
  elements.timerDisplay.classList.toggle("warning", remainingSeconds <= 10 * 60);
}

function updateScore(forcedSolved, forcedTotal) {
  const total = forcedTotal || state.currentExam?.questions.length || 8;
  const solved = forcedSolved ?? [...state.submissions.values()].filter((submission) => submission.is_correct).length;
  elements.scoreDisplay.textContent = solved === total ? "PASS" : `${solved}/${total}`;
}

async function loadWrongQuestions() {
  if (!state.username) {
    return;
  }

  try {
    const items = await apiGet(`/wrong-questions?username=${encodeURIComponent(state.username)}`);
    if (!items.length) {
      elements.wrongList.innerHTML = `<div class="empty-state">No wrong questions yet. Start an exam and submit answers to build this collection.</div>`;
      return;
    }
    elements.wrongList.innerHTML = items.map(wrongQuestionTemplate).join("");
  } catch (error) {
    elements.wrongList.innerHTML = `<div class="empty-state">${escapeHtml(error.message)}</div>`;
  }
}

function wrongQuestionTemplate(item) {
  return `
    <article class="stack-item">
      <div class="question-meta">
        <span>${escapeHtml(item.topic)}</span>
        <span>${escapeHtml(item.function_signature)}</span>
        <span>${formatDate(item.created_at)}</span>
      </div>
      <h3>${escapeHtml(item.title)}</h3>
      <p>${escapeHtml(item.description)}</p>
      <p><strong>Feedback:</strong> ${escapeHtml(item.feedback)}</p>
      ${item.error_message ? `<pre>${escapeHtml(item.error_message)}</pre>` : ""}
      <details>
        <summary>Your submitted code</summary>
        <pre>${escapeHtml(item.user_code)}</pre>
      </details>
    </article>
  `;
}

async function loadHistory() {
  try {
    const items = await apiGet("/history");
    if (!items.length) {
      elements.historyList.innerHTML = `<div class="empty-state">No exam history yet.</div>`;
      return;
    }
    elements.historyList.innerHTML = items.map(historyTemplate).join("");
  } catch (error) {
    elements.historyList.innerHTML = `<div class="empty-state">${escapeHtml(error.message)}</div>`;
  }
}

function historyTemplate(item) {
  return `
    <article class="stack-item">
      <div class="question-meta">
        <span>Exam #${item.exam_id}</span>
        <span>${escapeHtml(item.topic)}</span>
        <span>${escapeHtml(item.status)}</span>
      </div>
      <h3>Score: ${item.solved_questions}/${item.total_questions || 8}</h3>
      <p>Total submissions: ${item.total_submissions}</p>
      <p>${formatDate(item.created_at)}</p>
    </article>
  `;
}

async function generateAiQuestions() {
  const apiKey = elements.apiKeyInput.value.trim();
  const model = elements.modelSelect.value;
  if (!apiKey) {
    showToast("Please enter an API key.");
    return;
  }

  elements.aiResultList.innerHTML = `<div class="empty-state">Generating questions...</div>`;
  try {
    const result = await apiPost("/ai/generate-questions", {
      api_key: apiKey,
      model,
    });
    elements.aiResultList.innerHTML = result.questions.map(aiQuestionTemplate).join("");
    elements.apiKeyInput.value = "";
    showToast("AI questions generated.");
  } catch (error) {
    elements.aiResultList.innerHTML = `<div class="empty-state">${escapeHtml(error.message)}</div>`;
  }
}

function aiQuestionTemplate(question) {
  const examples = (question.examples || [])
    .map((example, index) => `Example ${index + 1}: ${JSON.stringify(example)}`)
    .join("\n");
  return `
    <article class="stack-item">
      <div class="question-meta">
        <span>${escapeHtml(question.topic)}</span>
        <span class="difficulty-tag ${escapeHtml(question.difficulty)}">${escapeHtml(question.difficulty)}</span>
        <span>${escapeHtml(question.function_signature)}</span>
      </div>
      <h3>${escapeHtml(question.title)}</h3>
      <p>${escapeHtml(question.description)}</p>
      <pre>${escapeHtml(examples || "No examples returned.")}</pre>
    </article>
  `;
}

async function apiGet(path) {
  const response = await fetch(`${API_BASE}${path}`);
  return parseResponse(response);
}

async function apiPost(path, body) {
  const response = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return parseResponse(response);
}

async function parseResponse(response) {
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.detail || "Request failed. Is the backend server running?");
  }
  return data;
}

function showToast(message) {
  elements.toast.textContent = message;
  elements.toast.classList.remove("hidden");
  window.clearTimeout(showToast.timer);
  showToast.timer = window.setTimeout(() => {
    elements.toast.classList.add("hidden");
  }, 2600);
}

function formatDate(value) {
  return new Date(value).toLocaleString();
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}
