(function () {
  var API_BASE = window.__LNS_API_BASE || (window.location.protocol === "file:" ? "http://127.0.0.1:8080" : "");

  function apiUrl(path) {
    return API_BASE + path;
  }

  function toBackendGender(gender) {
    return gender === "女" ? "female" : "male";
  }

  function toDisplayGender(gender) {
    if (gender === "female") return "女";
    if (gender === "male") return "男";
    return gender || "";
  }

  function toBackendCalendar(calendarType) {
    if (calendarType === "农历") return "lunar";
    return "solar";
  }

  function readJson(key, fallback) {
    var raw = localStorage.getItem(key);
    if (!raw) return fallback;
    try {
      return JSON.parse(raw);
    } catch (error) {
      return fallback;
    }
  }

  function writeJson(key, value) {
    localStorage.setItem(key, JSON.stringify(value));
  }

  function getBirthProfile() {
    return readJson("lns.birthProfile", null);
  }

  function saveBirthProfile(profile) {
    writeJson("lns.birthProfile", profile);
  }

  function calcAge(birthDate) {
    if (!birthDate) return 35;
    var birth = new Date(birthDate + "T00:00:00");
    if (isNaN(birth.getTime())) return 35;
    var now = new Date();
    var age = now.getFullYear() - birth.getFullYear();
    var monthDiff = now.getMonth() - birth.getMonth();
    if (monthDiff < 0 || (monthDiff === 0 && now.getDate() < birth.getDate())) {
      age -= 1;
    }
    return Math.max(age, 0);
  }

  function formatDateYYYYMMDD(date) {
    var year = date.getFullYear();
    var month = String(date.getMonth() + 1).padStart(2, "0");
    var day = String(date.getDate()).padStart(2, "0");
    return year + "-" + month + "-" + day;
  }

  function todayString() {
    return formatDateYYYYMMDD(new Date());
  }

  async function requestJson(path, options) {
    var response = await fetch(apiUrl(path), Object.assign({
      headers: {
        "Content-Type": "application/json",
      },
    }, options || {}));

    var data = {};
    try {
      data = await response.json();
    } catch (error) {
      data = {};
    }

    if (!response.ok || data.success === false) {
      throw new Error(data.error || data.message || ("Request failed: " + response.status));
    }

    return data;
  }

  async function createUser(profile) {
    return requestJson("/api/v1/user", {
      method: "POST",
      body: JSON.stringify({
        birth_date: profile.birthDate || "",
        birth_time: profile.birthTime || "",
        city: profile.city || "",
        district: profile.district || "",
        country: "CN",
        latitude: profile.latitude || null,
        longitude: profile.longitude || null,
        timezone: profile.timezone || "",
        gender: toBackendGender(profile.gender),
      }),
    });
  }

  async function generateReport(profile, userId, reportType) {
    var age = calcAge(profile.birthDate);
    return requestJson("/api/v1/report", {
      method: "POST",
      body: JSON.stringify({
        birth_date: profile.birthDate || "",
        birth_time: profile.birthTime || "",
        city: profile.city || "",
        country: "CN",
        gender: toBackendGender(profile.gender),
        user_id: userId || "",
        report_type: reportType || "decade",
        target_date: todayString(),
        age: age,
      }),
    });
  }

  function normalizeProfileFromForm(formData) {
    return {
      name: formData.get("name") || "",
      gender: formData.get("gender") || "男",
      birthDate: formData.get("birthDate") || "",
      birthTime: formData.get("birthTime") || "",
      calendarType: formData.get("calendarType") || "公历",
      city: formData.get("city") || "",
      timezone: formData.get("timezone") || "",
      useSolarTimeCorrection: !!formData.get("useSolarTimeCorrection"),
    };
  }

  function setNodeText(selector, value) {
    document.querySelectorAll(selector).forEach(function (node) {
      node.textContent = value == null || value === "" ? "未填写" : String(value);
    });
  }

  function mapEnergyScore(energyLevel) {
    if (energyLevel === "high") return 84;
    if (energyLevel === "low") return 46;
    return 66;
  }

  function mapRiskScore(riskLevel) {
    if (riskLevel === "high") return 76;
    if (riskLevel === "elevated") return 54;
    return 30;
  }

  function hashText(text) {
    var h = 0;
    var i;
    for (i = 0; i < text.length; i += 1) {
      h = ((h << 5) - h) + text.charCodeAt(i);
      h |= 0;
    }
    return Math.abs(h);
  }

  function safeArray(value) {
    return Array.isArray(value) ? value : [];
  }

  function toCurrentYear() {
    return new Date().getFullYear();
  }

  function findCurrentCycleIndex(cycles, currentAge) {
    var idx = -1;
    cycles.forEach(function (cycle, index) {
      var range = String(cycle.age_range || "");
      var match = range.match(/(\d+(?:\.\d+)?)\s*[-~]\s*(\d+(?:\.\d+)?)/);
      if (match) {
        var start = parseFloat(match[1]);
        var end = parseFloat(match[2]);
        if (currentAge >= start && currentAge <= end) {
          idx = index;
        }
      }
    });
    if (idx >= 0) return idx;
    if (cycles.length === 0) return -1;
    return Math.min(Math.floor(cycles.length / 2), cycles.length - 1);
  }

  function buildTrendPoints(analysis, report) {
    var state = (analysis && analysis.data && analysis.data.state) || {};
    var bazi = (analysis && analysis.data && analysis.data.bazi_birth) || {};
    var cycles = safeArray(bazi.luck_cycles);
    var currentAge = Number((report && report.overview && report.overview.stage) ? 36 : 36);
    var age = Number(localStorage.getItem("lns.currentAge") || 0) || 0;
    var scoreBase = mapEnergyScore(state.energy_level);
    var riskPenalty = Math.round(mapRiskScore(state.risk_level) * 0.35);
    var base = scoreBase - riskPenalty;
    var currentIndex = findCurrentCycleIndex(cycles, age || currentAge);
    var source = cycles.length ? cycles : [
      { age_range: "0-12" }, { age_range: "13-18" }, { age_range: "19-24" }, { age_range: "25-30" },
      { age_range: "31-36" }, { age_range: "37-45" }, { age_range: "46-55" }, { age_range: "56-65" }
    ];

    return source.map(function (cycle, index) {
      var label = cycle.age_range || cycle.pillar || ("阶段 " + (index + 1));
      var jitter = (hashText(label) % 15) - 7;
      var emphasis = index === currentIndex ? 14 : Math.max(0, 10 - Math.abs(index - currentIndex) * 2);
      var value = Math.max(18, Math.min(96, base + jitter + emphasis));
      return {
        label: label,
        value: value,
        isCurrent: index === currentIndex,
        stage: state.current_stage || "",
        tone: value >= 70 ? "up" : (value >= 52 ? "steady" : "down"),
        note: cycle.pillar || cycle.heavenly_stem || "",
      };
    });
  }

  function renderTrendChart(container, points) {
    if (!container) return;
    container.innerHTML = "";
    if (!points.length) {
      container.innerHTML = '<div class="chart-empty">暂无可用趋势数据</div>';
      return;
    }

    var maxValue = 100;
    var wrapper = document.createElement("div");
    wrapper.className = "trend-chart";

    var grid = document.createElement("div");
    grid.className = "trend-chart__grid";

    [20, 40, 60, 80, 100].forEach(function (line) {
      var row = document.createElement("div");
      row.className = "trend-chart__grid-line";
      row.style.bottom = line + "%";
      row.setAttribute("data-label", line);
      grid.appendChild(row);
    });

    var bars = document.createElement("div");
    bars.className = "trend-chart__bars";
    points.forEach(function (point) {
      var bar = document.createElement("button");
      bar.type = "button";
      bar.className = "trend-chart__bar " + (point.tone ? ("is-" + point.tone) : "");
      if (point.isCurrent) bar.className += " is-current";
      bar.style.height = Math.max(12, (point.value / maxValue) * 100) + "%";
      bar.setAttribute("title", point.label + " · " + point.value + "分" + (point.note ? (" · " + point.note) : ""));
      bar.innerHTML = '<span class="trend-chart__bar-label">' + point.label + '</span>' +
        '<span class="trend-chart__bar-score">' + Math.round(point.value) + '</span>';
      bars.appendChild(bar);
    });

    wrapper.appendChild(grid);
    wrapper.appendChild(bars);
    container.appendChild(wrapper);
  }

  function showActiveNav() {
    var path = window.location.pathname.split("/").pop() || "home.html";
    document.querySelectorAll("[data-nav]").forEach(function (node) {
      if (node.getAttribute("href") === path) {
        node.classList.add("is-active");
      }
    });

    var reportPages = ["kline.html", "analysis.html", "year-detail.html"];
    document.querySelectorAll("[data-report-nav]").forEach(function (node) {
      if (node.getAttribute("href") === path) {
        node.classList.add("is-current");
      }
      if (reportPages.indexOf(path) === -1) {
        node.style.display = "none";
      }
    });
  }

  async function initCreatePage() {
    var createForm = document.getElementById("birthProfileForm");
    if (!createForm) return;

    var statusNode = document.querySelector("[data-create-status]");
    var submitButton = createForm.querySelector('button[type="submit"]');

    function setStatus(message, kind) {
      if (!statusNode) return;
      statusNode.textContent = message;
      statusNode.setAttribute("data-status-kind", kind || "info");
    }

    createForm.addEventListener("submit", async function (event) {
      event.preventDefault();
      var formData = new FormData(createForm);
      var profile = normalizeProfileFromForm(formData);
      var userId = localStorage.getItem("lns.userId") || "";

      saveBirthProfile(profile);
      localStorage.setItem("lns.currentAge", String(calcAge(profile.birthDate)));

      if (submitButton) submitButton.disabled = true;
      setStatus("正在创建用户并生成报告...", "loading");

      try {
        if (!userId) {
          var userResp = await createUser(profile);
          userId = userResp.user_id;
          localStorage.setItem("lns.userId", userId);
        }

        var reportResp = await generateReport(profile, userId, "decade");
        localStorage.setItem("lns.lastReport", JSON.stringify(reportResp.data));
        localStorage.setItem("lns.lastReportType", "decade");
        setStatus("已生成报告，正在进入人生 K 线页。", "success");
        window.location.href = "kline.html";
      } catch (error) {
        if (submitButton) submitButton.disabled = false;
        setStatus("生成失败：" + error.message, "error");
      }
    });
  }

  function reportContentToText(report) {
    if (!report) return "";
    if (report.overview && report.overview.stage) {
      var parts = [];
      parts.push(report.title || "LNS 报告");
      parts.push("阶段：" + report.overview.stage);
      if (report.overview.dominant) parts.push("主导结构：" + report.overview.dominant);
      return parts.join(" · ");
    }
    return report.title || "LNS 报告";
  }

  async function loadLatestReportFromServer(userId) {
    if (!userId) return null;
    var reportListResp = await requestJson("/api/v1/user/" + encodeURIComponent(userId) + "/reports");
    var reports = safeArray(reportListResp.data);
    if (!reports.length) return null;
    var latest = reports[0];
    var reportResp = await requestJson("/api/v1/report/" + encodeURIComponent(latest.id) + "/view");
    return reportResp.data && reportResp.data.content ? reportResp.data.content : reportResp.data;
  }

  async function initKlinePage() {
    var chartNode = document.querySelector("[data-kline-chart]");
    if (!chartNode) return;

    var profile = getBirthProfile();
    var report = readJson("lns.lastReport", null);
    var userId = localStorage.getItem("lns.userId") || "";
    var currentAge = profile ? calcAge(profile.birthDate) : 36;
    localStorage.setItem("lns.currentAge", String(currentAge));

    var titleNode = document.querySelector("[data-report-title]");
    var summaryNode = document.querySelector("[data-report-summary]");
    var sourceNode = document.querySelector("[data-report-source]");
    var stageNode = document.querySelector("[data-current-stage]");
    var stageNoteNode = document.querySelector("[data-current-stage-note]");
    var energyNode = document.querySelector("[data-current-energy]");
    var riskNode = document.querySelector("[data-current-risk]");
    var cycleNode = document.querySelector("[data-current-cycle]");
    var cycleNoteNode = document.querySelector("[data-current-cycle-note]");
    var actionNode = document.querySelector("[data-current-action]");

    var loadingNode = document.querySelector("[data-kline-loading]");
    if (loadingNode) loadingNode.textContent = "正在拉取真实分析数据...";

    var analysis = null;
    try {
      if (profile && profile.birthDate && profile.birthTime && profile.city) {
        analysis = await requestJson("/api/v1/analyze", {
          method: "POST",
          body: JSON.stringify({
            birth_date: profile.birthDate,
            birth_time: profile.birthTime,
            city: profile.city,
            country: "CN",
            gender: toBackendGender(profile.gender),
            age: currentAge,
            user_id: userId,
          }),
        });
      }
    } catch (error) {
      console.warn("analysis request failed", error);
    }

    if (!report && userId) {
      try {
        report = await loadLatestReportFromServer(userId);
        if (report) {
          localStorage.setItem("lns.lastReport", JSON.stringify(report));
        }
      } catch (error) {
        console.warn("report load failed", error);
      }
    }

    if (titleNode) {
      titleNode.textContent = report ? (report.title || "人生导航大运报告") : "人生 K 线总览";
    }

    if (summaryNode) {
      summaryNode.textContent = report ? reportContentToText(report) : "基于真实分析接口生成的趋势总览，当前页面会先展示总体结构，再结合出生信息构建趋势图。";
    }

    if (sourceNode) {
      sourceNode.textContent = profile
        ? [profile.name, profile.gender ? toDisplayGender(toBackendGender(profile.gender)) : "", profile.city, profile.birthDate]
            .filter(Boolean).join(" · ")
        : "未找到出生信息，请先通过生成入口提交";
    }

    if (analysis && analysis.data) {
      var state = analysis.data.state || {};
      var bazi = analysis.data.bazi_birth || {};
      var time = analysis.data.time || {};
      var reportCycles = buildTrendPoints(analysis, report);
      renderTrendChart(chartNode, reportCycles);

      if (stageNode) stageNode.textContent = state.current_stage || "未识别";
      if (stageNoteNode) {
        stageNoteNode.textContent = "当前风险 " + (state.risk_level || "normal") + "，主导结构 " + (state.dominant_structure || "未识别");
      }
      if (energyNode) {
        energyNode.textContent = state.energy_level === "high" ? "84" : (state.energy_level === "low" ? "46" : "66");
      }
      if (riskNode) {
        riskNode.textContent = state.risk_level === "high" ? "76" : (state.risk_level === "elevated" ? "54" : "30");
      }
      if (cycleNode) {
        cycleNode.textContent = (bazi.luck_cycles && bazi.luck_cycles.length && bazi.luck_cycles[0].pillar) ? bazi.luck_cycles[0].pillar : (state.luck_cycle_theme && state.luck_cycle_theme[0]) || "趋势分析";
      }
      if (cycleNoteNode) {
        cycleNoteNode.textContent = "起运年龄 " + (bazi.start_age != null ? bazi.start_age : "未知") + "，当前年龄 " + currentAge + " 岁";
      }
      if (actionNode) {
        var focus = safeArray((time.T0 && time.T0.recommended_focus) || state.capability_profile);
        actionNode.textContent = focus.length ? focus.slice(0, 2).join(" / ") : "先完成基础数据接入";
      }
    } else {
      renderTrendChart(chartNode, buildTrendPoints(null, report));
      if (loadingNode) loadingNode.textContent = "暂未接入后端分析接口，显示本地结构图。";
    }
  }

  function initProfileNodes() {
    var profileNodes = document.querySelectorAll("[data-profile-field]");
    if (profileNodes.length === 0) return;
    var profile = getBirthProfile();
    if (!profile) return;
    profileNodes.forEach(function (node) {
      var key = node.getAttribute("data-profile-field");
      var value = profile[key];
      if (key === "gender") value = toDisplayGender(toBackendGender(value));
      if (value) node.textContent = value;
    });
  }

  showActiveNav();
  initProfileNodes();
  initCreatePage();
  initKlinePage();

  window.LNS_UI = {
    apiUrl: apiUrl,
    requestJson: requestJson,
    getBirthProfile: getBirthProfile,
    saveBirthProfile: saveBirthProfile,
    calcAge: calcAge,
  };
})();
