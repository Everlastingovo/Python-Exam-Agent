const API_HOST = window.location.hostname || "localhost";
const API_BASE = `http://${API_HOST}:8000`;
const MODEL_OPTIONS = [
  { provider: "OpenAI", id: "gpt-5.5" },
  { provider: "OpenAI", id: "gpt-5.4" },
  { provider: "OpenAI", id: "gpt-5.4-mini" },
  { provider: "OpenAI", id: "gpt-5.4-nano" },
  { provider: "OpenAI", id: "gpt-4.1" },
  { provider: "OpenAI", id: "gpt-4.1-mini" },
  { provider: "DeepSeek", id: "deepseek-v4-flash" },
  { provider: "DeepSeek", id: "deepseek-chat" },
  { provider: "DeepSeek", id: "deepseek-reasoner" },
  { provider: "Google Gemini", id: "gemini-3.1-pro" },
  { provider: "Google Gemini", id: "gemini-3.1-flash" },
  { provider: "Google Gemini", id: "gemini-2.5-pro" },
  { provider: "Google Gemini", id: "gemini-2.5-flash" },
  { provider: "Google Gemini", id: "gemini-2.5-flash-lite" },
  { provider: "Z.ai GLM", id: "glm-5.2" },
  { provider: "Z.ai GLM", id: "glm-5.1" },
  { provider: "Z.ai GLM", id: "glm-5" },
  { provider: "Z.ai GLM", id: "glm-4.6" },
  { provider: "Z.ai GLM", id: "glm-4.5" },
  { provider: "Anthropic Claude", id: "claude-opus-4.5" },
  { provider: "Anthropic Claude", id: "claude-sonnet-4.5" },
  { provider: "Qwen", id: "qwen3-max" },
  { provider: "Qwen", id: "qwen3-coder" },
  { provider: "Mistral", id: "mistral-large-latest" },
  { provider: "Mistral", id: "codestral-latest" },
  { provider: "Meta Llama", id: "llama-4" },
  { provider: "Moonshot Kimi", id: "kimi-k2" },
  { provider: "Other", id: "__other__" },
];

const state = {
  username: localStorage.getItem("pea_username") || "",
  email: localStorage.getItem("pea_email") || "",
  avatarInitial: localStorage.getItem("pea_avatar") || "T",
  isDemo: localStorage.getItem("pea_is_demo") === "true",
  editorTheme: localStorage.getItem("pea_editor_theme") || "dark",
  accentColor: localStorage.getItem("pea_accent_color") || "blue",
  apiKey: localStorage.getItem("pea_api_key") || "",
  apiKeyVerified: localStorage.getItem("pea_api_key_verified") === "true",
  defaultModel: localStorage.getItem("pea_default_model") || "gpt-5.4-mini",
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
  brandHomeButton: document.querySelector("#brandHomeButton"),
  userLabel: document.querySelector("#userLabel"),
  apiWarningButton: document.querySelector("#apiWarningButton"),
  apiWarningPopover: document.querySelector("#apiWarningPopover"),
  accountButton: document.querySelector("#accountButton"),
  accountQuickMenu: document.querySelector("#accountQuickMenu"),
  accountDetailsOption: document.querySelector("#accountDetailsOption"),
  quickSaveAccountOption: document.querySelector("#quickSaveAccountOption"),
  logoutOption: document.querySelector("#logoutOption"),
  accountAvatar: document.querySelector("#accountAvatar"),
  accountName: document.querySelector("#accountName"),
  accountEmail: document.querySelector("#accountEmail"),
  accountAttempts: document.querySelector("#accountAttempts"),
  accountLearningTime: document.querySelector("#accountLearningTime"),
  practiceCalendar: document.querySelector("#practiceCalendar"),
  avatarForm: document.querySelector("#avatarForm"),
  avatarInput: document.querySelector("#avatarInput"),
  saveAccountForm: document.querySelector("#saveAccountForm"),
  saveEmailInput: document.querySelector("#saveEmailInput"),
  savePasswordInput: document.querySelector("#savePasswordInput"),
  logoutButton: document.querySelector("#logoutButton"),
  sidebar: document.querySelector("#sidebar"),
  sidebarToggle: document.querySelector("#sidebarToggle"),
  sidebarToggleText: document.querySelector("#sidebarToggleText"),
  sidebarToggleArrow: document.querySelector("#sidebarToggleArrow"),
  tabs: document.querySelectorAll(".tab"),
  sections: document.querySelectorAll(".view-section"),
  topicCount: document.querySelector("#topicCount"),
  examForm: document.querySelector("#examForm"),
  practiceForm: document.querySelector("#practiceForm"),
  aiForm: document.querySelector("#aiForm"),
  apiKeyInput: document.querySelector("#apiKeyInput"),
  modelFilterInput: document.querySelector("#modelFilterInput"),
  modelSelect: document.querySelector("#modelSelect"),
  customModelInput: document.querySelector("#customModelInput"),
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
  backHomeButtons: document.querySelectorAll(".back-home-button"),
  settingsButton: document.querySelector("#settingsButton"),
  settingsPanel: document.querySelector("#settingsPanel"),
  settingsCloseButton: document.querySelector("#settingsCloseButton"),
  settingsSearchInput: document.querySelector("#settingsSearchInput"),
  settingsNavButtons: document.querySelectorAll(".settings-nav"),
  settingsViews: document.querySelectorAll(".settings-view"),
  settingsEditorLightButton: document.querySelector("#settingsEditorLightButton"),
  settingsEditorDarkButton: document.querySelector("#settingsEditorDarkButton"),
  colorChoiceButtons: document.querySelectorAll(".color-choice"),
  settingsApiKeyInput: document.querySelector("#settingsApiKeyInput"),
  settingsModelInput: document.querySelector("#settingsModelInput"),
  settingsModelList: document.querySelector("#settingsModelList"),
  settingsSaveApiButton: document.querySelector("#settingsSaveApiButton"),
  toast: document.querySelector("#toast"),
};

init();

function init() {
  bindEvents();
  renderModelOptions();
  renderSettingsModelList();
  applyEditorTheme();
  applyAccentColor();
  syncApiSettingsInputs();
  updateAuthView();
  if (state.username) {
    loadTopics();
    loadAccountDetails();
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
      applyAccount(result);
      elements.passwordInput.value = "";
      updateAuthView(true);
      loadTopics();
      loadAccountDetails();
      showToast("Login successful.");
    } catch (error) {
      showToast(error.message);
    }
  });

  elements.brandHomeButton.addEventListener("click", () => {
    if (state.username) {
      showSection("homeSection");
    }
  });

  elements.logoutButton.addEventListener("click", () => {
    localStorage.removeItem("pea_username");
    localStorage.removeItem("pea_email");
    localStorage.removeItem("pea_avatar");
    localStorage.removeItem("pea_is_demo");
    state.username = "";
    state.email = "";
    state.avatarInitial = "T";
    state.isDemo = false;
    state.currentExam = null;
    state.submissions.clear();
    stopTimer();
    updateAuthView(true);
  });

  elements.accountButton.addEventListener("click", () => {
    elements.accountQuickMenu.classList.toggle("hidden");
  });

  elements.apiWarningButton.addEventListener("click", () => {
    elements.apiWarningPopover.classList.toggle("hidden");
  });

  elements.accountDetailsOption.addEventListener("click", () => {
    showSection("accountSection");
    loadAccountDetails();
  });

  elements.quickSaveAccountOption.addEventListener("click", () => {
    showSection("saveAccountSection");
  });

  elements.logoutOption.addEventListener("click", () => {
    showSection("logoutSection");
  });

  elements.avatarForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    await updateAvatar();
  });

  elements.saveAccountForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    await saveToAccount();
  });

  elements.tabs.forEach((tab) => {
    tab.addEventListener("click", () => showSection(tab.dataset.view));
  });

  elements.sidebarToggle.addEventListener("click", () => {
    elements.sidebar.classList.toggle("open");
    updateSidebarToggle();
  });

  elements.homeStartButton.addEventListener("click", () => showSection("examSection"));
  elements.settingsEditorLightButton.addEventListener("click", () => setEditorTheme("light"));
  elements.settingsEditorDarkButton.addEventListener("click", () => setEditorTheme("dark"));
  elements.backHomeButtons.forEach((button) => {
    button.addEventListener("click", () => showSection("homeSection"));
  });

  elements.settingsButton.addEventListener("click", () => {
    elements.settingsPanel.classList.remove("hidden");
    syncApiSettingsInputs();
  });

  elements.settingsCloseButton.addEventListener("click", () => {
    elements.settingsPanel.classList.add("hidden");
  });

  elements.settingsNavButtons.forEach((button) => {
    button.addEventListener("click", () => showSettingsView(button.dataset.settingsView));
  });

  elements.colorChoiceButtons.forEach((button) => {
    button.addEventListener("click", () => setAccentColor(button.dataset.accent));
  });

  elements.settingsSaveApiButton.addEventListener("click", saveApiSettings);

  elements.settingsSearchInput.addEventListener("input", () => {
    const query = elements.settingsSearchInput.value.trim().toLowerCase();
    const match = [...elements.settingsNavButtons].find((button) => button.textContent.toLowerCase().includes(query));
    if (match) {
      showSettingsView(match.dataset.settingsView);
    }
  });

  elements.examForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    await generateExam();
  });
  elements.practiceForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    await generatePractice();
  });
  elements.aiForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    await generateAiQuestions();
  });

  elements.modelFilterInput.addEventListener("input", () => {
    renderModelOptions(elements.modelFilterInput.value);
  });

  elements.modelSelect.addEventListener("change", () => {
    updateCustomModelVisibility();
  });

  elements.finishExamButton.addEventListener("click", finishExam);
  elements.prevQuestionButton.addEventListener("click", () => moveQuestion(-1));
  elements.nextQuestionButton.addEventListener("click", () => moveQuestion(1));
  elements.refreshWrongButton.addEventListener("click", loadWrongQuestions);
  elements.refreshHistoryButton.addEventListener("click", loadHistory);
}

function setEditorTheme(theme) {
  state.editorTheme = theme;
  localStorage.setItem("pea_editor_theme", theme);
  applyEditorTheme();
}

function applyEditorTheme() {
  const isLight = state.editorTheme === "light";
  elements.examWorkspace.classList.toggle("editor-light", isLight);
  elements.examWorkspace.classList.toggle("editor-dark", !isLight);
  elements.settingsEditorLightButton.classList.toggle("active", isLight);
  elements.settingsEditorDarkButton.classList.toggle("active", !isLight);
  document.querySelectorAll("[data-editor-theme]").forEach((button) => {
    button.classList.toggle("active", button.dataset.editorTheme === state.editorTheme);
  });
}

function setAccentColor(accent) {
  state.accentColor = accent;
  localStorage.setItem("pea_accent_color", accent);
  applyAccentColor();
}

function applyAccentColor() {
  document.body.dataset.accent = state.accentColor;
  elements.colorChoiceButtons.forEach((button) => {
    button.classList.toggle("active", button.dataset.accent === state.accentColor);
  });
}

function showSettingsView(viewId) {
  elements.settingsViews.forEach((view) => {
    view.classList.toggle("hidden", view.id !== viewId);
  });
  elements.settingsNavButtons.forEach((button) => {
    button.classList.toggle("active", button.dataset.settingsView === viewId);
  });
}

function renderSettingsModelList() {
  elements.settingsModelList.innerHTML = MODEL_OPTIONS
    .filter((model) => model.id !== "__other__")
    .map((model) => `<option value="${escapeHtml(model.id)}">${escapeHtml(model.provider)}</option>`)
    .join("");
}

function syncApiSettingsInputs() {
  elements.settingsApiKeyInput.value = state.apiKey;
  elements.settingsModelInput.value = state.defaultModel;
  if (!elements.apiKeyInput.value && state.apiKey) {
    elements.apiKeyInput.value = state.apiKey;
  }
}

function saveApiSettings() {
  const previousKey = state.apiKey;
  state.apiKey = elements.settingsApiKeyInput.value.trim();
  state.defaultModel = elements.settingsModelInput.value.trim() || "gpt-5.4-mini";
  if (previousKey !== state.apiKey) {
    state.apiKeyVerified = false;
    localStorage.setItem("pea_api_key_verified", "false");
  }
  localStorage.setItem("pea_api_key", state.apiKey);
  localStorage.setItem("pea_default_model", state.defaultModel);
  elements.apiKeyInput.value = state.apiKey;
  setModelValue(state.defaultModel);
  updateApiWarning();
  showToast("API settings saved in this browser.");
}

function renderModelOptions(filterText = "") {
  const normalizedFilter = filterText.trim().toLowerCase();
  const filteredModels = MODEL_OPTIONS.filter((model) => (
    model.id.toLowerCase().includes(normalizedFilter)
    || model.provider.toLowerCase().includes(normalizedFilter)
  ));
  const models = filteredModels.some((model) => model.id === "__other__")
    ? filteredModels
    : [...filteredModels, MODEL_OPTIONS[MODEL_OPTIONS.length - 1]];

  elements.modelSelect.innerHTML = models
    .map((model) => (
      `<option value="${escapeHtml(model.id)}">${escapeHtml(model.provider)} - ${escapeHtml(model.id === "__other__" ? "Other / custom model" : model.id)}</option>`
    ))
    .join("");

  if (!elements.modelSelect.value && models.length) {
    elements.modelSelect.value = models[0].id;
  }
  if (!normalizedFilter) {
    setModelValue(state.defaultModel, false);
  }
  updateCustomModelVisibility();
}

function setModelValue(modelId, updateFilter = true) {
  const options = [...elements.modelSelect.options];
  const matchingOption = options.find((option) => option.value === modelId);
  if (matchingOption) {
    elements.modelSelect.value = modelId;
    elements.customModelInput.value = "";
    elements.customModelInput.classList.add("hidden");
    if (updateFilter) {
      elements.modelFilterInput.value = "";
    }
    return;
  }
  elements.modelSelect.value = "__other__";
  elements.customModelInput.classList.remove("hidden");
  elements.customModelInput.value = modelId;
}

function updateCustomModelVisibility() {
  const isOther = elements.modelSelect.value === "__other__";
  elements.customModelInput.classList.toggle("hidden", !isOther);
}

function applyAccount(account) {
  state.username = account.username;
  state.email = account.email || "";
  state.avatarInitial = account.avatar_initial || account.username.slice(0, 1).toUpperCase();
  state.isDemo = Boolean(account.is_demo);
  localStorage.setItem("pea_username", state.username);
  localStorage.setItem("pea_email", state.email);
  localStorage.setItem("pea_avatar", state.avatarInitial);
  localStorage.setItem("pea_is_demo", String(state.isDemo));
}

function updateAuthView(resetSection = false) {
  const isLoggedIn = Boolean(state.username);
  document.body.classList.toggle("logged-out", !isLoggedIn);
  document.body.classList.toggle("logged-in", isLoggedIn);
  elements.loginView.classList.toggle("hidden", isLoggedIn);
  elements.appView.classList.toggle("hidden", !isLoggedIn);
  elements.accountButton.classList.toggle("hidden", !isLoggedIn);
  elements.logoutButton.classList.toggle("hidden", !isLoggedIn);
  elements.userLabel.textContent = isLoggedIn ? `Logged in as ${state.username}` : "Not logged in";
  elements.accountButton.textContent = state.avatarInitial || "T";
  elements.accountAvatar.textContent = state.avatarInitial || "T";
  elements.accountName.textContent = state.username || "test";
  elements.accountEmail.textContent = state.email ? `Email: ${state.email}` : "Email: unbound";
  elements.saveAccountForm.classList.toggle("hidden", !state.isDemo);
  elements.quickSaveAccountOption.classList.toggle("hidden", !state.isDemo);
  elements.avatarInput.value = state.avatarInitial || "";
  elements.sidebarToggle.classList.toggle("hidden", !isLoggedIn);
  elements.sidebar.classList.toggle("hidden", !isLoggedIn);
  elements.settingsButton.classList.toggle("hidden", !isLoggedIn);
  updateApiWarning();
  updateSidebarToggle();
  if (!isLoggedIn) {
    elements.accountQuickMenu.classList.add("hidden");
    elements.settingsPanel.classList.add("hidden");
    elements.apiWarningPopover.classList.add("hidden");
  }
  if (isLoggedIn && resetSection) {
    showSection("homeSection");
  }
}

async function loadAccountDetails() {
  if (!state.username) {
    return;
  }
  try {
    const details = await apiGet(`/account/${encodeURIComponent(state.username)}`);
    applyAccount(details);
    updateAuthView();
    elements.accountAttempts.textContent = details.attempt_count;
    elements.accountLearningTime.textContent = `${details.learning_time_minutes} min`;
    renderPracticeCalendar(details.activity_days || []);
  } catch (error) {
    showToast(error.message);
  }
}

function renderPracticeCalendar(activityDays) {
  if (!activityDays.length) {
    elements.practiceCalendar.innerHTML = `<div class="empty-state">No practice records yet.</div>`;
    return;
  }

  const activityMap = new Map(activityDays.map((day) => [day.date, day]));
  const endDate = new Date();
  const startDate = new Date(endDate);
  startDate.setDate(endDate.getDate() - 34);
  const cells = [];

  for (let day = new Date(startDate); day <= endDate; day.setDate(day.getDate() + 1)) {
    const dateKey = formatDateKey(day);
    const activity = activityMap.get(dateKey);
    const percent = activity ? Math.min(100, Math.max(0, activity.best_percent)) : 0;
    const attempts = activity
      ? activity.attempts.map((attempt) => attempt.score).join(", ")
      : "No attempts";
    const title = activity
      ? `${dateKey}: best ${activity.best_score}; attempts: ${attempts}`
      : `${dateKey}: no attempts`;
    cells.push(`
      <div class="calendar-day" title="${escapeHtml(title)}">
        <span>${day.getDate()}</span>
        <i style="--fill: ${percent}%">${activity ? escapeHtml(activity.best_score) : ""}</i>
      </div>
    `);
  }

  elements.practiceCalendar.innerHTML = cells.join("");
}

function formatDateKey(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

async function updateAvatar() {
  const avatarInitial = elements.avatarInput.value.trim();
  if (!avatarInitial) {
    showToast("Please enter an avatar letter.");
    return;
  }
  try {
    const details = await apiPost("/account/avatar", {
      username: state.username,
      avatar_initial: avatarInitial,
    });
    applyAccount(details);
    updateAuthView();
    showToast("Avatar updated.");
  } catch (error) {
    showToast(error.message);
  }
}

async function saveToAccount() {
  const email = elements.saveEmailInput.value.trim();
  const password = elements.savePasswordInput.value;
  if (!email || !password) {
    showToast("Please enter email and password.");
    return;
  }
  if (password.length < 8) {
    showToast("Password must be at least 8 characters.");
    return;
  }
  try {
    const account = await apiPost("/account/save-to-account", {
      source_username: state.username,
      email,
      password,
    });
    applyAccount(account);
    updateAuthView();
    loadAccountDetails();
    elements.savePasswordInput.value = "";
    showToast(account.message);
  } catch (error) {
    showToast(error.message);
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
  if (sectionId === "accountSection") {
    loadAccountDetails();
  }
  elements.sidebar.classList.remove("open");
  elements.accountQuickMenu.classList.add("hidden");
  elements.apiWarningPopover.classList.add("hidden");
  updateSidebarToggle();
}

function updateApiWarning() {
  const shouldShow = Boolean(state.username) && !state.apiKeyVerified;
  elements.apiWarningButton.classList.toggle("hidden", !shouldShow);
  if (!shouldShow) {
    elements.apiWarningPopover.classList.add("hidden");
  }
}

function updateSidebarToggle() {
  const isOpen = elements.sidebar.classList.contains("open");
  elements.sidebarToggle.classList.toggle("open", isOpen);
  elements.sidebarToggleText.textContent = isOpen ? "Hidden" : "Menu";
  elements.sidebarToggleArrow.textContent = isOpen ? "←" : "→";
  elements.sidebarToggle.setAttribute("aria-label", isOpen ? "Hide menu" : "Open menu");
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
    state.currentExam.mode = "exam";
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

async function generatePractice() {
  try {
    const exam = await apiPost("/generate-practice", {
      topic: "__all__",
      difficulty: "mixed",
      number_of_questions: 8,
      username: state.username,
    });
    state.currentExam = exam;
    state.currentExam.mode = "practice";
    state.currentQuestionIndex = 0;
    state.submissions.clear();
    state.drafts.clear();
    stopTimer();
    elements.finalFeedback.classList.add("hidden");
    elements.examWorkspace.classList.remove("hidden");
    elements.examTitle.textContent = `Practice bank #${exam.exam_id}`;
    renderQuestions(exam.questions);
    updateScore();
    renderTimer();
    showToast(`Single-question practice started with ${exam.questions.length} questions.`);
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
  const label = state.currentExam?.mode === "practice" ? "Practice question" : "Question";
  elements.questionProgress.textContent = `${label} ${state.currentQuestionIndex + 1} of ${questions.length}`;
  elements.prevQuestionButton.disabled = state.currentQuestionIndex === 0;
  elements.nextQuestionButton.disabled = state.currentQuestionIndex === questions.length - 1;
  elements.questionList.innerHTML = questionTemplate(question, state.currentQuestionIndex);
  const button = document.querySelector(`[data-submit-question="${question.id}"]`);
  button.addEventListener("click", () => submitAnswer(question.id));
  document.querySelectorAll("[data-editor-theme]").forEach((themeButton) => {
    themeButton.addEventListener("click", () => setEditorTheme(themeButton.dataset.editorTheme));
  });
  applyEditorTheme();
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
          <span class="editor-header-actions">
            <span>Python</span>
            <span class="editor-theme-toggle compact" aria-label="Editor appearance">
              <button class="secondary" type="button" data-editor-theme="light">Light</button>
              <button class="secondary" type="button" data-editor-theme="dark">Dark</button>
            </span>
          </span>
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
  if (state.currentExam?.mode === "practice") {
    elements.timerDisplay.textContent = "Practice";
    elements.timerDisplay.classList.remove("warning");
    return;
  }
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
  elements.scoreDisplay.textContent = state.currentExam?.mode === "practice"
    ? `${solved}/${total} solved`
    : (solved === total ? "PASS" : `${solved}/${total}`);
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
  const apiKey = elements.apiKeyInput.value.trim() || state.apiKey;
  const model = elements.modelSelect.value === "__other__"
    ? elements.customModelInput.value.trim()
    : elements.modelSelect.value;
  if (!apiKey) {
    showToast("Please enter an API key.");
    return;
  }
  if (!model) {
    showToast("Please choose a model or enter a custom model name.");
    return;
  }

  elements.aiResultList.innerHTML = `<div class="empty-state">Generating questions...</div>`;
  try {
    const result = await apiPost("/ai/generate-questions", {
      api_key: apiKey,
      model,
    });
    state.apiKeyVerified = true;
    localStorage.setItem("pea_api_key_verified", "true");
    updateApiWarning();
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
