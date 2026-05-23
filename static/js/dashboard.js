"use strict";

if (!window.__TASKFLOW_DASHBOARD_INITIALIZED__) {
  window.__TASKFLOW_DASHBOARD_INITIALIZED__ = true;

  let tasks = [];
  let currentFilter = "all";
  let activePill = "all";
  let activePriority = "";
  let editingTaskId = null;
  let isSavingTask = false;
  const recentMutations = new Set();

  const taskListEl = document.getElementById("taskList");
  const emptyStateEl = document.getElementById("emptyState");
  const modalOverlay = document.getElementById("modalOverlay");
  const modalTitle = document.getElementById("modalTitle");
  const modalAlert = document.getElementById("modalAlert");
  const modalSaveBtn = document.getElementById("modalSaveBtn");
  const statusField = document.getElementById("statusFieldWrap");
  const toastEl = document.getElementById("toast");
  const pageTitle = document.getElementById("pageTitle");
  const searchInput = document.getElementById("searchInput");
  const searchClear = document.getElementById("searchClear");
  const filterPills = document.getElementById("filterPills");
  const priorityFilter = document.getElementById("priorityFilter");
  const statElements = {
    total: document.getElementById("statTotal"),
    completed: document.getElementById("statCompleted"),
    pending: document.getElementById("statPending"),
    completion: document.getElementById("statPct"),
    low: document.getElementById("statLow"),
    medium: document.getElementById("statMed"),
    high: document.getElementById("statHigh"),
  };

  function createMutationId() {
    return `tf_${Date.now()}_${Math.random().toString(36).slice(2, 10)}`;
  }

  function rememberMutation(id) {
    if (!id) return;
    recentMutations.add(id);
    window.setTimeout(() => recentMutations.delete(id), 8000);
  }

  function isOwnMutation(meta) {
    return Boolean(meta?.mutation_id && recentMutations.has(meta.mutation_id));
  }

  function showToast(msg, type = "success", ms = 3000) {
    toastEl.textContent = msg;
    toastEl.className = `toast ${type}`;
    clearTimeout(showToast._timer);
    showToast._timer = setTimeout(() => {
      toastEl.className = "toast hidden";
    }, ms);
  }

  function showModalAlert(msg, type = "error") {
    modalAlert.textContent = msg;
    modalAlert.className = `alert ${type}`;
  }

  function clearModalAlert() {
    modalAlert.className = "alert hidden";
  }

  function fmtDate(iso) {
    try {
      return new Date(iso).toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
        year: "numeric",
      });
    } catch (error) {
      return iso;
    }
  }

  function escapeHtml(str) {
    if (!str) return "";
    const element = document.createElement("div");
    element.appendChild(document.createTextNode(str));
    return element.innerHTML;
  }

  function normalizeId(id) {
    return typeof id === "number" ? id : Number(id);
  }

  function normalizeTask(task) {
    return {
      ...task,
      id: normalizeId(task.id),
      title: task.title || "",
      description: task.description || "",
      priority: task.priority || "Medium",
      status: task.status || "Pending",
      completed: task.status === "Completed",
    };
  }

  async function api(path, method = "GET", body = null) {
    const options = {
      method,
      headers: { "Content-Type": "application/json" },
    };

    if (body) {
      options.body = JSON.stringify(body);
    }

    const response = await fetch(path, options);
    const data = await response.json();
    return { ok: response.ok, status: response.status, data };
  }

  function dedupeTasks(taskList) {
    const uniqueTasks = new Map();
    (taskList || []).forEach((task) => {
      const normalized = normalizeTask(task);
      uniqueTasks.set(normalized.id, normalized);
    });

    const priorityRank = {
      High: 0,
      Medium: 1,
      Low: 2,
    };

    return Array.from(uniqueTasks.values()).sort(
      (left, right) => {
        const priorityDiff = (priorityRank[left.priority] ?? 99) - (priorityRank[right.priority] ?? 99);
        if (priorityDiff !== 0) {
          return priorityDiff;
        }

        return new Date(right.created_at) - new Date(left.created_at);
      },
    );
  }

  function setTasks(nextTasks) {
    tasks = dedupeTasks(nextTasks);
    renderDashboard();
  }

  function upsertTask(taskObj, { prepend = false } = {}) {
    const normalizedTask = normalizeTask(taskObj);
    const existingIndex = tasks.findIndex((task) => task.id === normalizedTask.id);

    if (existingIndex >= 0) {
      tasks[existingIndex] = { ...tasks[existingIndex], ...normalizedTask };
    } else if (prepend) {
      tasks.unshift(normalizedTask);
    } else {
      tasks.push(normalizedTask);
    }

    tasks = dedupeTasks(tasks);
    renderDashboard();
  }

  function removeTaskById(id) {
    const normalizedId = normalizeId(id);
    const existingIndex = tasks.findIndex((task) => task.id === normalizedId);
    if (existingIndex === -1) {
      return false;
    }

    tasks.splice(existingIndex, 1);
    renderDashboard();
    return true;
  }

  function getDerivedStats(taskList) {
    const safeTasks = Array.isArray(taskList) ? taskList : [];
    const totalTasks = safeTasks.length;
    const completedTasks = safeTasks.filter((task) => task.completed).length;
    const pendingTasks = safeTasks.filter((task) => !task.completed).length;
    const lowPriority = safeTasks.filter((task) => task.priority === "Low").length;
    const mediumPriority = safeTasks.filter((task) => task.priority === "Medium").length;
    const highPriority = safeTasks.filter((task) => task.priority === "High").length;
    const completionRate = totalTasks > 0
      ? Math.round((completedTasks / totalTasks) * 100)
      : 0;

    return {
      totalTasks,
      completedTasks,
      pendingTasks,
      lowPriority,
      mediumPriority,
      highPriority,
      completionRate,
    };
  }

  function animateNumber(element, targetValue, suffix = "") {
    if (!element) return;

    const safeTarget = Math.max(0, Number(targetValue) || 0);
    const currentValue = Number(element.dataset.value || 0);

    if (currentValue === safeTarget) {
      element.textContent = `${safeTarget}${suffix}`;
      return;
    }

    if (element._animationFrame) {
      cancelAnimationFrame(element._animationFrame);
    }

    const startValue = currentValue;
    const startTime = performance.now();
    const duration = 320;

    const step = (timestamp) => {
      const progress = Math.min((timestamp - startTime) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      const nextValue = Math.round(startValue + ((safeTarget - startValue) * eased));

      element.dataset.value = String(nextValue);
      element.textContent = `${nextValue}${suffix}`;

      if (progress < 1) {
        element._animationFrame = requestAnimationFrame(step);
      } else {
        element.dataset.value = String(safeTarget);
        element.textContent = `${safeTarget}${suffix}`;
        element._animationFrame = null;
      }
    };

    element._animationFrame = requestAnimationFrame(step);
  }

  function renderStats() {
    const stats = getDerivedStats(tasks);
    animateNumber(statElements.total, stats.totalTasks);
    animateNumber(statElements.completed, stats.completedTasks);
    animateNumber(statElements.pending, stats.pendingTasks);
    animateNumber(statElements.low, stats.lowPriority);
    animateNumber(statElements.medium, stats.mediumPriority);
    animateNumber(statElements.high, stats.highPriority);
    animateNumber(statElements.completion, stats.completionRate, "%");
  }

  function getVisibleTasks() {
    const query = (searchInput?.value || "").trim().toLowerCase();

    return tasks.filter((task) => {
      const matchesSidebar = currentFilter === "all" || task.status === currentFilter;
      const matchesPill = activePill === "all" || task.priority === activePill || task.status === activePill;
      const matchesPriority = !activePriority || task.priority === activePriority;
      const matchesSearch = !query || `${task.title} ${task.description}`.toLowerCase().includes(query);

      return matchesSidebar && matchesPill && matchesPriority && matchesSearch;
    });
  }

  function getIconForTask(title = "") {
    const normalizedTitle = title.toLowerCase();
    const iconMap = [
      { keys: ["auth", "login", "sign in", "signup", "password", "security"], icon: "shield" },
      { keys: ["deploy", "server", "hosting", "host"], icon: "rocket" },
      { keys: ["analytics", "report", "data", "chart", "metric"], icon: "bar-chart-2" },
      { keys: ["socket", "websocket", "realtime", "notification"], icon: "wifi" },
      { keys: ["ui", "ux", "design", "frontend", "layout"], icon: "monitor" },
      { keys: ["doc", "readme", "documentation", "guide"], icon: "file-text" },
      { keys: ["bug", "fix", "error", "crash"], icon: "bug" },
      { keys: ["db", "database", "postgres", "postgresql"], icon: "database" },
      { keys: ["api", "endpoint", "backend", "server"], icon: "code" },
      { keys: ["email", "message", "mail"], icon: "mail" },
      { keys: ["meeting", "call", "calendar"], icon: "phone" },
      { keys: ["ai", "ml", "model"], icon: "cpu" },
    ];

    for (const item of iconMap) {
      if (item.keys.some((keyword) => normalizedTitle.includes(keyword))) {
        return item.icon;
      }
    }

    return "file-text";
  }

  function renderTasks() {
    const visibleTasks = getVisibleTasks();
    taskListEl.innerHTML = "";
    emptyStateEl.style.display = visibleTasks.length === 0 ? "flex" : "none";

    visibleTasks.forEach((task) => {
      const card = document.createElement("article");
      card.className = `task-card ${task.status === "Completed" ? "completed" : ""}`;
      card.dataset.id = String(task.id);

      const iconName = getIconForTask(task.title);
      card.innerHTML = `
        <div class="task-left">
          <button class="task-check ${task.completed ? "checked" : ""}" aria-label="Toggle complete">
            ${task.completed
              ? '<span class="check-icon check-icon-tick" aria-hidden="true">✓</span>'
              : '<span class="check-icon check-icon-empty" aria-hidden="true"></span>'}
          </button>
          <div class="task-icon" data-icon="${iconName}">
            <i data-lucide="${iconName}"></i>
          </div>
          <div class="task-info">
            <div class="task-title ${task.completed ? "is-complete" : ""}">${escapeHtml(task.title)}</div>
            <div class="task-desc">${escapeHtml(task.description || "")}</div>
            <div class="task-date">${fmtDate(task.created_at)}</div>
          </div>
        </div>
        <div class="task-right">
          <div class="priority-badge priority-${task.priority.toLowerCase()}">${task.priority}</div>
          <div class="status-badge ${task.completed ? "status-completed" : "status-pending"}">${task.status}</div>
          <div class="task-actions">
            <button class="btn-icon edit" title="Edit">✎</button>
            <button class="btn-icon del" title="Delete">✕</button>
          </div>
        </div>
      `;

      card.querySelector(".task-check").addEventListener("click", () => {
        const nextStatus = task.completed ? "Pending" : "Completed";
        toggleStatus(task.id, nextStatus);
      });
      card.querySelector(".btn-icon.edit").addEventListener("click", () => openEditModal(task));
      card.querySelector(".btn-icon.del").addEventListener("click", () => deleteTask(task.id));

      taskListEl.appendChild(card);
      requestAnimationFrame(() => card.classList.add("visible"));
    });

    if (window.lucide && typeof window.lucide.createIcons === "function") {
      window.lucide.createIcons();
    }
  }

  function renderDashboard() {
    renderStats();
    renderTasks();
  }

  async function loadTasks() {
    const { ok, data } = await api("/api/tasks");
    if (!ok) {
      showToast(data.error || "Failed to load tasks.", "error");
      return;
    }

    setTasks(data.tasks || []);
  }

  async function createTask(payload) {
    if (isSavingTask) return;

    isSavingTask = true;
    modalSaveBtn.disabled = true;

    try {
      const mutationId = createMutationId();
      rememberMutation(mutationId);
      const { ok, data } = await api("/api/tasks", "POST", { ...payload, mutation_id: mutationId });
      if (!ok) {
        showModalAlert(data.error || "Failed to create task.");
        return;
      }

      upsertTask(data.task, { prepend: true });
      closeModal();
      showToast("Task created");
    } finally {
      isSavingTask = false;
      modalSaveBtn.disabled = false;
    }
  }

  async function updateTask(id, payload) {
    if (isSavingTask) return;

    isSavingTask = true;
    modalSaveBtn.disabled = true;

    try {
      const mutationId = createMutationId();
      rememberMutation(mutationId);
      const { ok, data } = await api(`/api/tasks/${id}`, "PUT", { ...payload, mutation_id: mutationId });
      if (!ok) {
        showModalAlert(data.error || "Failed to update task.");
        return;
      }

      upsertTask(data.task);
      closeModal();
      showToast("Task updated");
    } finally {
      isSavingTask = false;
      modalSaveBtn.disabled = false;
    }
  }

  async function toggleStatus(id, status) {
    const mutationId = createMutationId();
    rememberMutation(mutationId);
    const { ok, data } = await api(`/api/tasks/${id}`, "PUT", { status, mutation_id: mutationId });
    if (!ok) {
      showToast(data.error || "Failed to update status.", "error");
      return;
    }

    upsertTask(data.task);
  }

  async function deleteTask(id) {
    if (!confirm("Delete this task?")) return;

    const mutationId = createMutationId();
    rememberMutation(mutationId);
    const { ok, data } = await api(`/api/tasks/${id}`, "DELETE", { mutation_id: mutationId });
    if (!ok) {
      showToast(data.error || "Failed to delete task.", "error");
      return;
    }

    removeTaskById(id);
    showToast("Task deleted");
  }

  function openCreateModal() {
    editingTaskId = null;
    modalTitle.textContent = "New Task";
    modalSaveBtn.textContent = "Create Task";
    document.getElementById("taskTitle").value = "";
    document.getElementById("taskDesc").value = "";
    document.getElementById("taskPriority").value = "Medium";
    document.getElementById("taskStatus").value = "Pending";
    statusField.style.display = "none";
    clearModalAlert();
    modalSaveBtn.disabled = false;
    modalOverlay.classList.remove("hidden");
    document.getElementById("taskTitle").focus();
  }

  function openEditModal(task) {
    editingTaskId = task.id;
    modalTitle.textContent = "Edit Task";
    modalSaveBtn.textContent = "Save Changes";
    document.getElementById("taskTitle").value = task.title;
    document.getElementById("taskDesc").value = task.description || "";
    document.getElementById("taskPriority").value = task.priority;
    document.getElementById("taskStatus").value = task.status;
    statusField.style.display = "block";
    clearModalAlert();
    modalSaveBtn.disabled = false;
    modalOverlay.classList.remove("hidden");
    document.getElementById("taskTitle").focus();
  }

  function closeModal() {
    modalOverlay.classList.add("hidden");
    clearModalAlert();
    editingTaskId = null;
    isSavingTask = false;
    modalSaveBtn.disabled = false;
  }

  document.getElementById("openModalBtn").addEventListener("click", openCreateModal);
  document.getElementById("modalClose").addEventListener("click", closeModal);
  document.getElementById("modalCancelBtn").addEventListener("click", closeModal);
  modalOverlay.addEventListener("click", (event) => {
    if (event.target === modalOverlay) closeModal();
  });

  document.getElementById("modalSaveBtn").addEventListener("click", async () => {
    const title = document.getElementById("taskTitle").value.trim();
    const description = document.getElementById("taskDesc").value.trim();
    const priority = document.getElementById("taskPriority").value;
    const status = document.getElementById("taskStatus").value;

    if (!title) {
      showModalAlert("Title is required.");
      return;
    }

    if (editingTaskId) {
      await updateTask(editingTaskId, { title, description, priority, status });
    } else {
      await createTask({ title, description, priority });
    }
  });

  document.querySelectorAll(".nav-item").forEach((item) => {
    item.addEventListener("click", (event) => {
      event.preventDefault();
      document.querySelectorAll(".nav-item").forEach((navItem) => navItem.classList.remove("active"));
      item.classList.add("active");
      currentFilter = item.dataset.filter;
      pageTitle.textContent = item.textContent.trim();
      renderTasks();
    });
  });

  if (searchInput) {
    searchInput.addEventListener("input", () => {
      if (searchClear) {
        searchClear.classList.toggle("hidden", !searchInput.value);
      }
      renderTasks();
    });
  }

  if (searchClear) {
    searchClear.addEventListener("click", () => {
      searchInput.value = "";
      searchClear.classList.add("hidden");
      renderTasks();
    });
  }

  if (filterPills) {
    filterPills.addEventListener("click", (event) => {
      const button = event.target.closest(".pill");
      if (!button) return;

      filterPills.querySelectorAll(".pill").forEach((pill) => pill.classList.remove("active"));
      button.classList.add("active");
      activePill = button.dataset.filter;
      renderTasks();
    });
  }

  if (priorityFilter) {
    priorityFilter.addEventListener("change", (event) => {
      activePriority = event.target.value;
      renderTasks();
    });
  }

  const openModalBtnEmpty = document.getElementById("openModalBtnEmpty");
  if (openModalBtnEmpty) {
    openModalBtnEmpty.addEventListener("click", openCreateModal);
  }

  document.getElementById("logoutBtn").addEventListener("click", async () => {
    await api("/api/auth/logout", "POST");
    window.location.href = "/login";
  });

  const socket = io({ transports: ["websocket", "polling"] });

  socket.on("task_created", (payload) => {
    if (isOwnMutation(payload?.meta)) return;
    upsertTask(payload.task, { prepend: true });
  });

  socket.on("task_updated", (payload) => {
    if (isOwnMutation(payload?.meta)) return;
    upsertTask(payload.task);
  });

  socket.on("task_deleted", (payload) => {
    if (isOwnMutation(payload?.meta)) return;
    removeTaskById(payload.id);
  });

  loadTasks();
}
