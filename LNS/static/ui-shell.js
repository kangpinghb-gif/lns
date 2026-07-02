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

  function isProfileComplete(profile) {
    return !!(profile && profile.birthDate && profile.birthTime && profile.city);
  }

  function getCurrentPage() {
    return window.location.pathname.split("/").pop() || "home.html";
  }

  function isResultPage(path) {
    return ["kline.html", "analysis.html", "year-detail.html"].indexOf(path) >= 0;
  }

  function redirectToCreate(nextPage) {
    var target = "create.html";
    if (nextPage) {
      target += "?next=" + encodeURIComponent(nextPage);
    }
    window.location.replace(target);
  }

  function saveBirthProfile(profile) {
    writeJson("lns.birthProfile", profile);
  }

  function getEntitlement() {
    return {
      paid: false,
      analysisDeep: true,
      yearlyPro: true,
      klinePro: true,
    };
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

  async function generateReport(profile, userId, reportType, targetDate) {
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
        target_date: targetDate || todayString(),
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

  function setListItems(selector, items, fallback) {
    var node = document.querySelector(selector);
    if (!node) return;
    var list = safeArray(items).filter(Boolean);
    node.innerHTML = "";
    if (!list.length) {
      var empty = document.createElement("li");
      empty.textContent = fallback || "暂无数据";
      node.appendChild(empty);
      return;
    }
    list.forEach(function (item) {
      var li = document.createElement("li");
      li.textContent = item;
      node.appendChild(li);
    });
  }

  function pillarText(label, pillar) {
    if (!pillar) return label + " 待生成";
    return label + " " + (pillar.stem || "") + (pillar.branch || "");
  }

  function renderFourPillars(container, fourPillars) {
    if (!container) return;
    var pillars = fourPillars || {};
    var items = [
      pillarText("年柱", pillars.year),
      pillarText("月柱", pillars.month),
      pillarText("日柱", pillars.day),
      pillarText("时柱", pillars.hour)
    ];
    container.innerHTML = "";
    items.forEach(function (text) {
      var tag = document.createElement("span");
      tag.className = "tag";
      tag.textContent = text;
      container.appendChild(tag);
    });
  }

  function elementScore(value) {
    if (value == null || value === "") return "-";
    var num = Number(value);
    if (Number.isNaN(num)) return String(value);
    return String(Math.round(num * 100));
  }

  function mapLevelLabel(level) {
    if (level === "high") return "高";
    if (level === "low") return "低";
    if (level === "elevated") return "偏高";
    if (level === "normal") return "常规";
    if (level === "medium") return "中";
    return level || "未识别";
  }

  function mapEnergyText(level) {
    if (level === "high") return "高";
    if (level === "low") return "低";
    return "中";
  }

  function getAgeBand(age) {
    if (age <= 12) return "0–12岁";
    if (age <= 18) return "13–18岁";
    if (age <= 25) return "19–25岁";
    if (age <= 35) return "26–35岁";
    if (age <= 50) return "36–50岁";
    return "50岁以上";
  }

  function getPillarText(pillar) {
    if (!pillar) return "";
    return [pillar.stem, pillar.branch].filter(Boolean).join("");
  }

  var STEM_ELEMENT = {
    "甲": "wood", "乙": "wood",
    "丙": "fire", "丁": "fire",
    "戊": "earth", "己": "earth",
    "庚": "metal", "辛": "metal",
    "壬": "water", "癸": "water"
  };

  var BRANCH_ELEMENT = {
    "寅": "wood", "卯": "wood",
    "巳": "fire", "午": "fire",
    "辰": "earth", "戌": "earth", "丑": "earth", "未": "earth",
    "申": "metal", "酉": "metal",
    "亥": "water", "子": "water"
  };

  function parseCycleRange(cycle) {
    if (!cycle) return null;
    var start = Number(cycle.start_age);
    var end = Number(cycle.end_age);
    if (Number.isFinite(start) && Number.isFinite(end)) {
      return { start: start, end: end };
    }

    var range = String(cycle.age_range || "").replace("~", "-");
    var match = range.match(/(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)/);
    if (!match) return null;
    return { start: parseFloat(match[1]), end: parseFloat(match[2]) };
  }

  function formatCycleRange(cycle) {
    var range = parseCycleRange(cycle);
    if (!range) return "";
    return Math.round(range.start) + "-" + Math.round(range.end) + "岁";
  }

  function getCurrentLuckCycle(bazi, currentAge) {
    var cycles = safeArray(bazi && bazi.luck_cycles);
    if (!cycles.length) return null;

    var matched = cycles.find(function (cycle) {
      var range = parseCycleRange(cycle);
      return range && currentAge >= range.start && currentAge <= range.end;
    });
    if (matched) return matched;

    var startAge = Number(bazi && bazi.start_age);
    if (Number.isFinite(startAge)) {
      var index = Math.max(0, Math.floor((currentAge - startAge) / 10));
      if (index < cycles.length) return cycles[index];
    }

    return null;
  }

  function deriveLuckCycleTheme(cycle) {
    if (!cycle) return "";
    var stem = cycle.heavenly_stem || (cycle.pillar || "").slice(0, 1);
    var branch = cycle.earthly_branch || (cycle.pillar || "").slice(1, 2);
    var stemElem = STEM_ELEMENT[stem] || "";
    var branchElem = BRANCH_ELEMENT[branch] || "";

    if (stemElem === "wood" && branchElem === "wood") return "成长扩展期";
    if (stemElem === "fire" && branchElem === "fire") return "表达展现期";
    if (stemElem === "metal" && branchElem === "metal") return "规则整合期";
    if (stemElem === "water" && branchElem === "water") return "流动调整期";
    if (stemElem === "earth" && branchElem === "earth") return "稳定积累期";
    if (["wood", "fire"].indexOf(stemElem) >= 0 && ["wood", "fire"].indexOf(branchElem) >= 0) return "积极发展期";
    if (["metal", "water"].indexOf(stemElem) >= 0 && ["metal", "water"].indexOf(branchElem) >= 0) return "内收调整期";
    if (stemElem === "earth" || branchElem === "earth") return "结构巩固期";
    return "综合发展期";
  }

  function getCurrentCycleTheme(bazi, state, currentAge) {
    var currentCycle = getCurrentLuckCycle(bazi, currentAge);
    return deriveLuckCycleTheme(currentCycle) || safeArray(state && state.luck_cycle_theme)[0] || "";
  }

  function getCurrentYearText() {
    var today = new Date();
    var month = today.getMonth() + 1;
    var day = today.getDate();
    var prefix = month <= 2 ? "今日" : "今天";
    return prefix + "是" + formatDateYYYYMMDD(today).slice(5, 10).replace("-", "月") + "日";
  }

  function getCurrentAnchor(bazi, state, currentAge) {
    var dayMaster = bazi && bazi.day_master ? bazi.day_master + "日主" : "命盘";
    var structure = state && state.dominant_structure ? state.dominant_structure : "未识别";
    var currentCycle = getCurrentLuckCycle(bazi, currentAge || Number(localStorage.getItem("lns.currentAge") || 35));
    var cycle = currentCycle && currentCycle.pillar ? currentCycle.pillar + "大运" : "当前大运";
    return dayMaster + " · " + structure + " · " + cycle;
  }

  function renderTimelineItems(container, items) {
    if (!container) return;
    container.innerHTML = "";
    if (!safeArray(items).length) {
      container.innerHTML = '<div class="timeline-item is-current"><div class="timeline-meta"><strong>当前年份</strong><br>暂无可用的年份切换数据。</div></div>';
      return;
    }

    items.forEach(function (item) {
      var wrap = document.createElement("div");
      wrap.className = "timeline-item" + (item.isCurrent ? " is-current" : "");
      wrap.innerHTML =
        '<div class="timeline-badge">' + item.badge + '</div>' +
        '<div class="timeline-meta"><strong>' + item.title + '</strong><br>' + item.note + '</div>' +
        '<div class="timeline-score"><div class="score-number">' + item.score + '</div><div class="score-caption">' + item.caption + '</div></div>';
      container.appendChild(wrap);
    });
  }

  function getAnalysisCacheKey() {
    return "lns.lastAnalysis";
  }

  function readCachedAnalysis() {
    return readJson(getAnalysisCacheKey(), null);
  }

  function saveCachedAnalysis(data) {
    writeJson(getAnalysisCacheKey(), data);
  }

  function getSelectedYear() {
    return localStorage.getItem("lns.selectedYear") || "";
  }

  function setSelectedYear(year) {
    if (!year) return;
    localStorage.setItem("lns.selectedYear", String(year));
  }

  async function loadAnalysis(profile, userId, currentAge) {
    if (!profile || !profile.birthDate || !profile.birthTime || !profile.city) return null;
    var analysis = await requestJson("/api/v1/analyze", {
      method: "POST",
      body: JSON.stringify({
        birth_date: profile.birthDate,
        birth_time: profile.birthTime,
        city: profile.city,
        country: "CN",
        gender: toBackendGender(profile.gender),
        age: currentAge,
        user_id: userId || "",
      }),
    });
    saveCachedAnalysis(analysis);
    return analysis;
  }

  function mapEnergyScore(energyLevel) {
    if (energyLevel === "high") return 84;
    if (energyLevel === "low") return 46;
    return 66;
  }

  function mapEnergyNote(energyLevel) {
    if (energyLevel === "high") return "当前推进力较强，适合处理核心事项";
    if (energyLevel === "low") return "当前更适合收敛节奏，减少非必要消耗";
    return "当前能量平稳，适合按计划推进";
  }

  function mapRiskScore(riskLevel) {
    if (riskLevel === "high") return 76;
    if (riskLevel === "elevated") return 54;
    return 30;
  }

  function mapRiskNote(riskLevel) {
    if (riskLevel === "high") return "风险偏高，关键决策需要延后或拆小";
    if (riskLevel === "elevated") return "风险偏高，推进时需要预留缓冲";
    return "风险常规，可按当前节奏推进";
  }

  function buildUserSummary(state) {
    var energy = state && state.energy_level ? state.energy_level : "medium";
    var risk = state && state.risk_level ? state.risk_level : "normal";
    if (risk === "high" && energy === "high") {
      return {
        title: "当前推进力较强，但风险需要控制",
        copy: "适合处理核心事项，不适合同时扩大多个投入。先验证关键判断，再决定是否加速。",
        advice: "把目标拆成小步骤，优先做最关键的一件事。"
      };
    }
    if (risk === "high") {
      return {
        title: "当前风险偏高，先收敛节奏",
        copy: "压力和不确定性同步上升，关键决策建议延后或拆小。",
        advice: "减少临时承诺，保留缓冲时间。"
      };
    }
    if (risk === "elevated") {
      return {
        title: "当前可以推进，但需要预留缓冲",
        copy: "整体节奏可控，但执行过程中容易出现额外消耗。",
        advice: "推进前先设定边界，避免把计划做得过满。"
      };
    }
    if (energy === "high") {
      return {
        title: "当前推进窗口打开",
        copy: "行动力和外部响应较强，适合把已有计划往前推一步。",
        advice: "优先推进已经验证过的事项。"
      };
    }
    if (energy === "low") {
      return {
        title: "当前更适合蓄力和整理",
        copy: "不必急着扩大投入，先降低消耗、修正节奏。",
        advice: "先复盘、整理资源，再进入下一轮推进。"
      };
    }
    return {
      title: "当前节奏平稳，适合按计划推进",
      copy: "没有明显的极端信号，重点是保持稳定执行。",
      advice: "按既定计划推进，同时保留必要调整空间。"
    };
  }

  function buildAnalysisInsights(state, time, synth) {
    var summary = buildUserSummary(state);
    var focus = safeArray(time && time.T0 && time.T0.recommended_focus);
    var risks = safeArray(synth && synth.synthesized_risk);
    var capabilities = safeArray(state && state.capability_profile);
    return {
      advantage: capabilities.slice(0, 2).join(" / ") || "行动力和结构感较强，适合推进已有计划。",
      risk: risks.slice(0, 2).join(" / ") || mapRiskNote(state && state.risk_level),
      advice: focus.slice(0, 2).join(" / ") || summary.advice
    };
  }

  function translateTenGodKey(key) {
    var map = {
      year: "年柱",
      month: "月柱",
      day: "日柱",
      hour: "时柱"
    };
    return map[key] || key;
  }

  function buildYearHeadline(year, overview, riskAnalysis) {
    var energyText = mapLevelLabel(overview && overview.energy);
    var riskText = mapLevelLabel((overview && overview.risk) || (riskAnalysis && riskAnalysis.level));
    if (energyText === "高" && riskText === "高") return year + " 年机会高，但风险也高";
    if (riskText === "高" || riskText === "偏高") return year + " 年需要控制节奏";
    if (energyText === "高") return year + " 年适合主动推进";
    return year + " 年以稳步推进为主";
  }

  function buildYearSummary(overview, yearlyDirection, riskAnalysis) {
    var focus = safeArray(yearlyDirection && yearlyDirection.strategic_focus).slice(0, 2).join(" / ");
    var risk = safeArray(riskAnalysis && riskAnalysis.synthesized_risks).slice(0, 1).join(" / ");
    if (focus && risk) return "适合" + focus + "，但要注意" + risk + "。";
    if (focus) return "适合" + focus + "，重点是控制节奏，不要同时开启太多事项。";
    if (risk) return "年度风险集中在" + risk + "，建议先验证再放大。";
    return "适合主动推进，但要控制节奏，避免同时开启太多事项。";
  }

  function buildStageNote(state, time) {
    var parts = [];
    if (state && state.current_stage) parts.push("当前处于" + state.current_stage);
    if (state && state.dominant_structure) parts.push("主导结构为" + state.dominant_structure);
    if (time && time.T2 && time.T2.yearly_direction) parts.push("年度方向：" + time.T2.yearly_direction);
    if (!parts.length) return "当前阶段判断已生成，建议结合命理透视页查看结构来源。";
    return parts.join("，") + "。";
  }

  function buildCycleNote(bazi, state, currentAge) {
    var currentCycle = getCurrentLuckCycle(bazi, currentAge);
    var rangeText = formatCycleRange(currentCycle);
    var theme = getCurrentCycleTheme(bazi, state, currentAge);
    var stage = state && state.current_stage ? state.current_stage : "";
    var parts = [];
    if (rangeText) parts.push(rangeText);
    if (stage) parts.push(stage);
    if (theme && theme !== stage) parts.push(theme);
    return parts.length ? parts.join(" · ") : "当前趋势已基于分析结果更新。";
  }

  function buildActionWindowLabel(decision, time, state) {
    var p0Text = safeArray(decision && decision.P0).join(" / ");
    var focusText = safeArray(time && time.T0 && time.T0.recommended_focus).join(" / ");
    var capabilityText = safeArray(state && state.capability_profile).join(" / ");
    var source = [p0Text, focusText, capabilityText].join(" / ");
    if (/职业|岗位|简历|工作|事业|项目|执行|推进/.test(source)) return "行动窗口开启";
    if (/学习|复盘|思考|整理|规划/.test(source)) return "整理窗口开启";
    if (state && state.risk_level === "high") return "谨慎推进";
    if (state && state.energy_level === "high") return "推进窗口开启";
    return "按计划推进";
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
    var idx = cycles.findIndex(function (cycle) {
      var range = parseCycleRange(cycle);
      return range && currentAge >= range.start && currentAge <= range.end;
    });
    if (idx >= 0) return idx;
    if (cycles.length === 0) return -1;
    return Math.min(Math.floor(cycles.length / 2), cycles.length - 1);
  }

  function buildTrendPoints(analysis, report) {
    var state = (analysis && analysis.data && analysis.data.state) || {};
    var bazi = (analysis && analysis.data && analysis.data.bazi_birth) || {};
    var cycles = safeArray(bazi.luck_cycles);
    var currentAge = Number(localStorage.getItem("lns.currentAge") || 36);
    var age = Number(localStorage.getItem("lns.currentAge") || 0) || 0;
    var scoreBase = mapEnergyScore(state.energy_level);
    var riskPenalty = Math.round(mapRiskScore(state.risk_level) * 0.35);
    var base = scoreBase - riskPenalty;
    var currentIndex = findCurrentCycleIndex(cycles, age || currentAge);
    var currentYear = toCurrentYear();
    var source = cycles.length ? cycles : [
      { age_range: "0-12" }, { age_range: "13-18" }, { age_range: "19-24" }, { age_range: "25-30" },
      { age_range: "31-36" }, { age_range: "37-45" }, { age_range: "46-55" }, { age_range: "56-65" }
    ];

    var previousClose = Math.max(18, Math.min(96, base - 4));
    return source.map(function (cycle, index) {
      var label = cycle.age_range || cycle.pillar || ("阶段 " + (index + 1));
      var match = String(label).match(/(\d+(?:\.\d+)?)\s*[-~]\s*(\d+(?:\.\d+)?)/);
      var startAge = match ? parseFloat(match[1]) : Math.max(0, index * 10);
      var targetYear = currentYear + Math.round(startAge - currentAge);
      var jitter = (hashText(label) % 15) - 7;
      var emphasis = index === currentIndex ? 14 : Math.max(0, 10 - Math.abs(index - currentIndex) * 2);
      var close = Math.max(18, Math.min(96, base + jitter + emphasis));
      var openShift = ((hashText(label + "open") % 13) - 6);
      var open = index === 0 ? Math.max(18, Math.min(96, close - openShift)) : previousClose;
      var upperShadow = 4 + (hashText(label + "high") % 10);
      var lowerShadow = 4 + (hashText(label + "low") % 10);
      var high = Math.min(100, Math.max(open, close) + upperShadow);
      var low = Math.max(0, Math.min(open, close) - lowerShadow);
      previousClose = close;
      return {
        label: label,
        year: targetYear,
        value: close,
        open: open,
        high: high,
        low: low,
        close: close,
        isCurrent: index === currentIndex,
        stage: state.current_stage || "",
        tone: close >= open ? "up" : "down",
        note: cycle.pillar || cycle.heavenly_stem || "",
      };
    });
  }

  function renderTrendChart(container, points, options) {
    if (!container) return;
    var chartOptions = options || {};
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
      var high = Math.max(0, Math.min(maxValue, point.high == null ? point.value : point.high));
      var low = Math.max(0, Math.min(maxValue, point.low == null ? point.value : point.low));
      var open = Math.max(0, Math.min(maxValue, point.open == null ? point.value : point.open));
      var close = Math.max(0, Math.min(maxValue, point.close == null ? point.value : point.close));
      var bodyTop = Math.max(open, close);
      var bodyBottom = Math.min(open, close);
      var wickHeight = Math.max(4, high - low);
      var bodyHeight = Math.max(4, bodyTop - bodyBottom);
      bar.setAttribute("title", point.year + " · " + point.label + " · 开" + Math.round(open) + " 高" + Math.round(high) + " 低" + Math.round(low) + " 收" + Math.round(close) + (point.note ? (" · " + point.note) : ""));
      bar.setAttribute("data-target-year", point.year);
      bar.setAttribute("aria-label", point.year + "年 K线，开" + Math.round(open) + "，高" + Math.round(high) + "，低" + Math.round(low) + "，收" + Math.round(close));
      bar.innerHTML =
        '<span class="trend-chart__wick" style="height:' + wickHeight + '%; bottom:' + low + '%"></span>' +
        '<span class="trend-chart__body" style="height:' + bodyHeight + '%; bottom:' + bodyBottom + '%"></span>' +
        '<span class="trend-chart__bar-label">' + point.label + '</span>' +
        '<span class="trend-chart__bar-score">' + Math.round(close) + '</span>';
      ["mouseenter", "focus"].forEach(function (eventName) {
        bar.addEventListener(eventName, function () {
          if (typeof chartOptions.onInspect === "function") {
            chartOptions.onInspect(point);
          }
        });
      });
      bar.addEventListener("click", function () {
        setSelectedYear(point.year);
        window.location.href = "year-detail.html";
      });
      bars.appendChild(bar);
    });

    wrapper.appendChild(grid);
    wrapper.appendChild(bars);
    container.appendChild(wrapper);
  }

  function filterTrendPoints(points, range) {
    var currentYear = toCurrentYear();
    if (range === "month") {
      return points.filter(function (point) {
        return Math.abs(point.year - currentYear) <= 1 || point.isCurrent;
      });
    }
    if (range === "decade") {
      return points.filter(function (point) {
        return point.year >= currentYear - 5 && point.year <= currentYear + 5;
      });
    }
    if (range !== "recent") return points;
    return points.filter(function (point) {
      return point.year >= currentYear - 5 && point.year <= currentYear + 5;
    });
  }

  function renderKlineAxis(axisNode, points) {
    if (!axisNode) return;
    var years = safeArray(points).map(function (point) {
      return Number(point.year);
    }).filter(function (year) {
      return !Number.isNaN(year);
    }).sort(function (a, b) {
      return a - b;
    });

    var labels = ["--", "--", "--"];
    if (years.length === 1) {
      labels = [String(years[0] - 1), String(years[0]), String(years[0] + 1)];
    } else if (years.length > 1) {
      labels = [
        String(years[0]),
        String(years[Math.floor(years.length / 2)]),
        String(years[years.length - 1])
      ];
    }

    axisNode.innerHTML = "";
    labels.forEach(function (label) {
      var item = document.createElement("span");
      item.textContent = label;
      axisNode.appendChild(item);
    });
  }

  function renderKlineInfo(infoNode, point) {
    if (!infoNode || !point) return;
    var yearNode = infoNode.querySelector("[data-kline-info-year]");
    var ohlcNode = infoNode.querySelector("[data-kline-info-ohlc]");
    var stageNode = infoNode.querySelector("[data-kline-info-stage]");
    if (yearNode) yearNode.textContent = String(point.year);
    if (ohlcNode) {
      ohlcNode.textContent = [
        "开" + Math.round(point.open),
        "高" + Math.round(point.high),
        "低" + Math.round(point.low),
        "收" + Math.round(point.close)
      ].join(" / ");
    }
    if (stageNode) {
      stageNode.textContent = [point.stage, point.note].filter(Boolean).join(" · ") || point.label || "趋势阶段";
    }
  }

  function deriveTrendLabel(state) {
    if (!state) return "趋势待识别";
    var risk = state.risk_level || "normal";
    var energy = state.energy_level || "medium";
    var dominant = state.dominant_structure || "";
    var themes = safeArray(state.luck_cycle_theme);

    if (risk === "high") return "压力调整";
    if (risk === "elevated") return "谨慎推进";
    if (energy === "high" && themes.some(function (item) { return /发展|展现|扩展/.test(item); })) return "稳步上升";
    if (energy === "high") return "主动打开";
    if (energy === "low") return "收敛蓄力";
    if (/稳健|规则|学习|稳定/.test(dominant)) return "平稳推进";
    return "结构调整";
  }

  function deriveTrendNote(state) {
    if (!state) return "当前暂无趋势说明。";
    var themes = safeArray(state.luck_cycle_theme);
    var pieces = [];
    if (state.energy_level) pieces.push("能量处于" + mapLevelLabel(state.energy_level));
    if (state.risk_level) pieces.push("风险为" + mapLevelLabel(state.risk_level));
    if (themes.length) pieces.push("大运主题：" + themes.join(" / "));
    return pieces.join("，") || "当前暂无趋势说明。";
  }

  function showActiveNav() {
    var path = getCurrentPage();
    var hasProfile = isProfileComplete(getBirthProfile());
    document.querySelectorAll("[data-nav]").forEach(function (node) {
      var href = node.getAttribute("href");
      if (href === path) {
        node.classList.add("is-active");
      }
      if (!hasProfile && isResultPage(href)) {
        node.classList.add("is-disabled");
        node.setAttribute("aria-disabled", "true");
        node.addEventListener("click", function (event) {
          event.preventDefault();
          redirectToCreate(href);
        });
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

  function renderUpgradeSlots() {
    var entitlement = getEntitlement();
    document.querySelectorAll("[data-upgrade-slot]").forEach(function (node) {
      var scope = node.getAttribute("data-upgrade-slot");
      var statusNode = node.querySelector("[data-upgrade-status]");
      if (!statusNode) return;
      if (scope === "analysis-deep") {
        statusNode.textContent = entitlement.analysisDeep ? "暂免费开放" : "解锁完整版";
      } else if (scope === "yearly-pro") {
        statusNode.textContent = entitlement.yearlyPro ? "暂免费开放" : "解锁年度增强";
      } else if (scope === "kline-pro") {
        statusNode.textContent = entitlement.klinePro ? "暂免费开放" : "解锁专业版";
      }
    });
  }

  function enforceResultAccess() {
    var path = getCurrentPage();
    if (!isResultPage(path)) return true;
    if (isProfileComplete(getBirthProfile())) return true;
    redirectToCreate(path);
    return false;
  }

  function pad2(value) {
    return String(value).padStart(2, "0");
  }

  function daysInMonth(year, month) {
    return new Date(year, month, 0).getDate();
  }

  function clampNumber(value, min, max) {
    var num = Number(value);
    if (!Number.isFinite(num)) return min;
    return Math.max(min, Math.min(max, num));
  }

  function initBirthWheelPicker(createForm, setStatus) {
    var dateInput = createForm.birthDate;
    var timeInput = createForm.birthTime;
    var dateTrigger = document.querySelector('[data-picker-open="date"]');
    var timeTrigger = document.querySelector('[data-picker-open="time"]');
    var dateLabel = document.querySelector("[data-picker-date-label]");
    var timeLabel = document.querySelector("[data-picker-time-label]");
    if (!dateInput || !timeInput || !dateTrigger || !timeTrigger) return;

    var currentYear = new Date().getFullYear();
    var pickerState = {
      kind: "date",
      year: 1990,
      month: 1,
      day: 1,
      hour: 8,
      minute: 0
    };
    var scrollTimers = {};

    var picker = document.createElement("div");
    picker.className = "wheel-picker";
    picker.hidden = true;
    picker.innerHTML =
      '<div class="wheel-picker__panel" role="dialog" aria-modal="true">' +
        '<div class="wheel-picker__head">' +
          '<button class="wheel-picker__action" type="button" data-picker-cancel>取消</button>' +
          '<div class="wheel-picker__title" data-picker-title>选择出生日期</div>' +
          '<button class="wheel-picker__action" type="button" data-picker-confirm>完成</button>' +
        '</div>' +
        '<div class="wheel-picker__cols" data-picker-cols></div>' +
      '</div>';
    document.body.appendChild(picker);

    var titleNode = picker.querySelector("[data-picker-title]");
    var colsNode = picker.querySelector("[data-picker-cols]");
    var cancelButton = picker.querySelector("[data-picker-cancel]");
    var confirmButton = picker.querySelector("[data-picker-confirm]");

    function parseExistingValues() {
      var dateMatch = String(dateInput.value || "").match(/^(\d{4})-(\d{2})-(\d{2})$/);
      if (dateMatch) {
        pickerState.year = clampNumber(dateMatch[1], 1900, currentYear);
        pickerState.month = clampNumber(dateMatch[2], 1, 12);
        pickerState.day = clampNumber(dateMatch[3], 1, daysInMonth(pickerState.year, pickerState.month));
      }
      var timeMatch = String(timeInput.value || "").match(/^(\d{2}):(\d{2})$/);
      if (timeMatch) {
        pickerState.hour = clampNumber(timeMatch[1], 0, 23);
        pickerState.minute = clampNumber(timeMatch[2], 0, 59);
      }
    }

    function updateTriggerLabels() {
      if (dateInput.value) {
        dateLabel.textContent = dateInput.value.replace(/-/g, " / ");
        dateTrigger.classList.add("has-value");
      } else {
        dateLabel.textContent = "选择出生日期";
        dateTrigger.classList.remove("has-value");
      }
      if (timeInput.value) {
        timeLabel.textContent = timeInput.value;
        timeTrigger.classList.add("has-value");
      } else {
        timeLabel.textContent = "选择出生时间";
        timeTrigger.classList.remove("has-value");
      }
    }

    function makeColumn(key, values, formatter) {
      var col = document.createElement("div");
      var track = document.createElement("div");
      col.className = "wheel-picker__col";
      track.className = "wheel-picker__track";
      col.setAttribute("data-picker-key", key);
      var touchStartY = null;

      function applyIndex(index, shouldRender) {
        var safeIndex = Math.max(0, Math.min(values.length - 1, index));
        pickerState[key] = values[safeIndex];
        track.style.transform = "translateY(" + (66 - safeIndex * 44) + "px)";
        track.querySelectorAll(".wheel-picker__option").forEach(function (node, nodeIndex) {
          node.classList.toggle("is-selected", nodeIndex === safeIndex);
        });
        if (shouldRender && (key === "year" || key === "month")) {
          pickerState.day = Math.min(pickerState.day, daysInMonth(pickerState.year, pickerState.month));
          renderPicker();
        }
      }

      values.forEach(function (value) {
        var item = document.createElement("div");
        item.className = "wheel-picker__option";
        item.setAttribute("data-picker-value", String(value));
        item.textContent = formatter ? formatter(value) : String(value);
        item.addEventListener("click", function () {
          applyIndex(values.indexOf(value), true);
        });
        track.appendChild(item);
      });
      col.appendChild(track);
      col.selectPickerValue = function (value) {
        var index = values.findIndex(function (item) { return String(item) === String(value); });
        applyIndex(index < 0 ? 0 : index, false);
      };
      col.addEventListener("wheel", function (event) {
        event.preventDefault();
        window.clearTimeout(scrollTimers[key]);
        scrollTimers[key] = window.setTimeout(function () {
          var currentIndex = values.findIndex(function (item) { return String(item) === String(pickerState[key]); });
          applyIndex(currentIndex + (event.deltaY > 0 ? 1 : -1), true);
        }, 20);
      }, { passive: false });
      col.addEventListener("touchstart", function (event) {
        touchStartY = event.touches && event.touches[0] ? event.touches[0].clientY : null;
      }, { passive: true });
      col.addEventListener("touchend", function (event) {
        if (touchStartY == null || !event.changedTouches || !event.changedTouches[0]) return;
        var delta = touchStartY - event.changedTouches[0].clientY;
        var steps = Math.round(delta / 36);
        if (steps !== 0) {
          var currentIndex = values.findIndex(function (item) { return String(item) === String(pickerState[key]); });
          applyIndex(currentIndex + steps, true);
        }
        touchStartY = null;
      });
      return col;
    }

    function scrollColumnToValue(col, value) {
      if (typeof col.selectPickerValue === "function") {
        col.selectPickerValue(value);
      }
    }

    function renderPicker() {
      var columns = [];
      colsNode.innerHTML = "";
      if (pickerState.kind === "date") {
        titleNode.textContent = "选择出生日期";
        var years = [];
        for (var year = 1900; year <= currentYear; year += 1) years.push(year);
        var months = [];
        for (var month = 1; month <= 12; month += 1) months.push(month);
        var days = [];
        for (var day = 1; day <= daysInMonth(pickerState.year, pickerState.month); day += 1) days.push(day);
        columns = [
          makeColumn("year", years, function (value) { return value + "年"; }),
          makeColumn("month", months, function (value) { return pad2(value) + "月"; }),
          makeColumn("day", days, function (value) { return pad2(value) + "日"; })
        ];
      } else {
        titleNode.textContent = "选择出生时间";
        var hours = [];
        for (var hour = 0; hour <= 23; hour += 1) hours.push(hour);
        var minutes = [];
        for (var minute = 0; minute <= 59; minute += 1) minutes.push(minute);
        columns = [
          makeColumn("hour", hours, function (value) { return pad2(value) + "时"; }),
          makeColumn("minute", minutes, function (value) { return pad2(value) + "分"; })
        ];
      }
      colsNode.style.setProperty("--picker-cols", String(columns.length));
      columns.forEach(function (col) {
        colsNode.appendChild(col);
        scrollColumnToValue(col, pickerState[col.getAttribute("data-picker-key")]);
      });
    }

    function openPicker(kind) {
      parseExistingValues();
      pickerState.kind = kind;
      picker.hidden = false;
      renderPicker();
    }

    function closePicker() {
      picker.hidden = true;
    }

    function confirmPicker() {
      if (pickerState.kind === "date") {
        dateInput.value = pickerState.year + "-" + pad2(pickerState.month) + "-" + pad2(pickerState.day);
      } else {
        timeInput.value = pad2(pickerState.hour) + ":" + pad2(pickerState.minute);
      }
      updateTriggerLabels();
      if (typeof setStatus === "function") setStatus("", "info");
      closePicker();
    }

    dateTrigger.addEventListener("click", function () { openPicker("date"); });
    timeTrigger.addEventListener("click", function () { openPicker("time"); });
    cancelButton.addEventListener("click", closePicker);
    confirmButton.addEventListener("click", confirmPicker);
    picker.addEventListener("click", function (event) {
      if (event.target === picker) closePicker();
    });

    updateTriggerLabels();
    createForm.updateBirthPickerLabels = updateTriggerLabels;
  }

  async function initCreatePage() {
    var createForm = document.getElementById("birthProfileForm");
    if (!createForm) return;

    var statusNode = document.querySelector("[data-create-status]");
    var submitButton = createForm.querySelector('button[type="submit"]');
    var profile = getBirthProfile();
    var nextPage = new URLSearchParams(window.location.search).get("next") || "kline.html";

    if (submitButton) {
      if (nextPage === "analysis.html") submitButton.textContent = "生成并查看命理透视";
      else if (nextPage === "year-detail.html") submitButton.textContent = "生成并查看流年详情";
      else if (nextPage === "kline.html") submitButton.textContent = "生成并查看趋势";
      else submitButton.textContent = "生成并查看结果";
    }

    if (profile) {
      if (createForm.name) createForm.name.value = profile.name || "";
      if (createForm.gender) createForm.gender.value = profile.gender || "男";
      if (createForm.birthDate) createForm.birthDate.value = profile.birthDate || "";
      if (createForm.birthTime) createForm.birthTime.value = profile.birthTime || "";
      if (createForm.calendarType) createForm.calendarType.value = profile.calendarType || "公历";
      if (createForm.city) createForm.city.value = profile.city || "";
      if (createForm.timezone) createForm.timezone.value = profile.timezone || "";
    }

    function setStatus(message, kind) {
      if (!statusNode) return;
      statusNode.textContent = message;
      statusNode.hidden = !message;
      statusNode.setAttribute("data-status-kind", kind || "info");
    }

    initBirthWheelPicker(createForm, setStatus);
    if (typeof createForm.updateBirthPickerLabels === "function") {
      createForm.updateBirthPickerLabels();
    }

    createForm.addEventListener("submit", async function (event) {
      event.preventDefault();
      var formData = new FormData(createForm);
      var profile = normalizeProfileFromForm(formData);
      var userId = localStorage.getItem("lns.userId") || "";

      if (!profile.birthDate) {
        setStatus("请选择出生日期。", "error");
        return;
      }
      if (!profile.birthTime) {
        setStatus("请选择出生时间。", "error");
        return;
      }

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
        setStatus("已生成报告，正在进入结果页。", "success");
        window.location.href = isResultPage(nextPage) ? nextPage : "kline.html";
      } catch (error) {
        if (submitButton) submitButton.disabled = false;
        setStatus("生成失败：" + error.message, "error");
      }
    });
  }

  async function initHomePage() {
    var nameNode = document.querySelector("[data-home-name]");
    if (!nameNode) return;

    var profile = getBirthProfile();
    var userId = localStorage.getItem("lns.userId") || "";
    var currentAge = profile ? calcAge(profile.birthDate) : 35;
    var analysis = readCachedAnalysis();

    if (!isProfileComplete(profile)) {
      var emptyAnchorNode = document.querySelector("[data-home-anchor]");
      var emptyStageNode = document.querySelector("[data-home-stage]");
      var emptyEnergyNode = document.querySelector("[data-home-energy]");
      var emptyEnergyBarNode = document.querySelector("[data-home-energy-bar]");
      var emptyCurrentStageNode = document.querySelector("[data-home-current-stage]");
      var emptyStageRangeNode = document.querySelector("[data-home-current-stage-range]");
      var emptyWindowNode = document.querySelector("[data-home-window]");
      var emptyActionNode = document.querySelector("[data-home-action]");
      var emptyActionCopyNode = document.querySelector("[data-home-action-copy]");
      var emptyActionTimeNode = document.querySelector("[data-home-action-time]");
      var emptyTrendNode = document.querySelector("[data-home-trend]");
      var emptyTrendNoteNode = document.querySelector("[data-home-trend-note]");
      var emptyRiskNode = document.querySelector("[data-home-risk]");
      var emptyRiskNoteNode = document.querySelector("[data-home-risk-note]");
      var emptyWhyNode = document.querySelector("[data-home-why]");

      if (nameNode) nameNode.textContent = "创建命盘";
      if (emptyAnchorNode) emptyAnchorNode.textContent = "出生信息 · 命盘生成 · 人生导航";
      if (emptyStageNode) emptyStageNode.textContent = "填写出生信息后生成个人状态";
      if (emptyEnergyNode) emptyEnergyNode.textContent = "--";
      if (emptyEnergyBarNode) emptyEnergyBarNode.style.width = "0%";
      if (emptyCurrentStageNode) emptyCurrentStageNode.textContent = "待生成";
      if (emptyStageRangeNode) emptyStageRangeNode.textContent = "";
      if (emptyWindowNode) emptyWindowNode.textContent = "待生成";
      if (emptyActionNode) emptyActionNode.textContent = "先生成你的命盘";
      if (emptyActionCopyNode) emptyActionCopyNode.textContent = "用出生时间建立基础命盘，再查看当前阶段、风险提醒和年度建议。";
      if (emptyActionTimeNode) emptyActionTimeNode.textContent = "填写出生信息";
      if (emptyTrendNode) emptyTrendNode.textContent = "待生成";
      if (emptyTrendNoteNode) emptyTrendNoteNode.textContent = "生成后显示趋势";
      if (emptyRiskNode) emptyRiskNode.textContent = "--";
      if (emptyRiskNoteNode) emptyRiskNoteNode.textContent = "生成后显示风险";
      if (emptyWhyNode) emptyWhyNode.setAttribute("href", "create.html");
      return;
    }

    try {
      var fresh = await loadAnalysis(profile, userId, currentAge);
      if (fresh) analysis = fresh;
    } catch (error) {
      console.warn("home page analysis request failed", error);
    }

    var state = (analysis && analysis.data && analysis.data.state) || {};
    var bazi = (analysis && analysis.data && analysis.data.bazi_birth) || {};
    var time = (analysis && analysis.data && analysis.data.time) || {};
    var decision = (analysis && analysis.data && analysis.data.decision) || {};
    var synth = (analysis && analysis.data && analysis.data.synthesized) || {};

    var dayPillar = getPillarText(bazi.four_pillars && bazi.four_pillars.day);
    var anchorNode = document.querySelector("[data-home-anchor]");
    var stageNode = document.querySelector("[data-home-stage]");
    var energyNode = document.querySelector("[data-home-energy]");
    var energyBarNode = document.querySelector("[data-home-energy-bar]");
    var currentStageNode = document.querySelector("[data-home-current-stage]");
    var stageRangeNode = document.querySelector("[data-home-current-stage-range]");
    var windowNode = document.querySelector("[data-home-window]");
    var actionNode = document.querySelector("[data-home-action]");
    var trendNode = document.querySelector("[data-home-trend]");
    var trendNoteNode = document.querySelector("[data-home-trend-note]");
    var riskNode = document.querySelector("[data-home-risk]");
    var riskNoteNode = document.querySelector("[data-home-risk-note]");
    var actionTimeNode = document.querySelector("[data-home-action-time]");
    var actionCopyNode = document.querySelector("[data-home-action-copy]");

    if (nameNode) {
      nameNode.textContent = profile && profile.name ? profile.name : "李明";
    }
    if (anchorNode && bazi) {
      anchorNode.textContent = getCurrentAnchor(bazi, state, currentAge);
    }
    if (stageNode) {
      stageNode.textContent = getCurrentYearText() + " · 处于" + (state.current_stage || "未识别");
    }
    if (energyNode) {
      energyNode.textContent = mapEnergyScore(state.energy_level);
    }
    if (energyBarNode) {
      energyBarNode.style.width = mapEnergyScore(state.energy_level) + "%";
    }
    if (currentStageNode) {
      currentStageNode.textContent = state.current_stage || "未识别";
    }
    if (stageRangeNode) {
      stageRangeNode.textContent = "（" + getAgeBand(currentAge) + "）";
    }
    if (windowNode) {
      windowNode.textContent = buildActionWindowLabel(decision, time, state);
    }
    if (actionNode) {
      actionNode.textContent = (safeArray(decision.P0).length && decision.P0[0]) ||
        "完善简历，针对创新类岗位定向投递";
    }
    if (actionCopyNode) {
      actionCopyNode.textContent = buildUserSummary(state).advice;
    }
    if (actionTimeNode) {
      actionTimeNode.textContent = "本月内完成";
    }
    if (trendNode) {
      trendNode.textContent = deriveTrendLabel(state) === "稳步上升" ? "上升" : deriveTrendLabel(state);
    }
    if (trendNoteNode) {
      trendNoteNode.textContent = safeArray(state.luck_cycle_theme).join(" / ") || "流月逢合";
    }
    if (riskNode) {
      riskNode.textContent = mapRiskScore(state.risk_level) + "%";
    }
    if (riskNoteNode) {
      riskNoteNode.textContent = safeArray(synth.synthesized_risk).slice(0, 1).join(" / ") || "需关注财务";
    }
  }

  function getKlineRangeText(range) {
    if (range === "decade") return "范围：大运";
    if (range === "month") return "范围：流月";
    return "范围：流年";
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
    var trendNode = document.querySelector("[data-current-trend]");
    var trendNoteNode = document.querySelector("[data-current-trend-note]");
    var energyNode = document.querySelector("[data-current-energy]");
    var energyBarNode = document.querySelector("[data-energy-bar]");
    var energyNoteNode = document.querySelector("[data-energy-note]");
    var riskNode = document.querySelector("[data-current-risk]");
    var riskBarNode = document.querySelector("[data-risk-bar]");
    var riskNoteNode = document.querySelector("[data-risk-note]");
    var cycleNode = document.querySelector("[data-current-cycle]");
    var cycleNoteNode = document.querySelector("[data-current-cycle-note]");
    var actionNode = document.querySelector("[data-current-action]");
    var rangeLabelNode = document.querySelector("[data-kline-range-label]");
    var currentAgeNode = document.querySelector("[data-kline-current-age]");
    var rangeButtons = document.querySelectorAll("[data-kline-range]");
    var anchorNode = document.querySelector("[data-kline-anchor]");
    var axisNode = document.querySelector("[data-kline-axis]");
    var klineInfoNode = document.querySelector("[data-kline-info]");

    var loadingNode = document.querySelector("[data-kline-loading]");
    if (loadingNode) loadingNode.textContent = "正在拉取真实分析数据...";
    if (currentAgeNode) currentAgeNode.textContent = "当前 " + currentAge + " 岁";

    var analysis = readCachedAnalysis();
    try {
      analysis = await loadAnalysis(profile, userId, currentAge);
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
      titleNode.textContent = report ? (report.title || "趋势图已生成，先看当前节奏") : "趋势图已生成，先看当前节奏";
    }

    if (summaryNode) {
      summaryNode.textContent = report ? reportContentToText(report) : "后端分析不可用时，先展示本地趋势骨架；接入分析结果后会自动补全能量、风险和行动建议。";
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
      var currentRange = localStorage.getItem("lns.klineRange") || "all";

      function applyRange(range) {
        localStorage.setItem("lns.klineRange", range);
        var visiblePoints = filterTrendPoints(reportCycles, range);
        if (rangeLabelNode) {
          rangeLabelNode.textContent = getKlineRangeText(range);
        }
        rangeButtons.forEach(function (button) {
          var active = button.getAttribute("data-kline-range") === range;
          button.classList.toggle("is-active", active);
        });
        renderTrendChart(chartNode, visiblePoints, {
          onInspect: function (point) {
            renderKlineInfo(klineInfoNode, point);
          }
        });
        renderKlineAxis(axisNode, visiblePoints);
        var currentPoint = visiblePoints.find(function (point) { return point.isCurrent; }) || visiblePoints[0];
        renderKlineInfo(klineInfoNode, currentPoint);
      }

      rangeButtons.forEach(function (button) {
        button.addEventListener("click", function () {
          applyRange(button.getAttribute("data-kline-range"));
        });
      });

      applyRange(currentRange);

      if (anchorNode) {
        anchorNode.textContent = getCurrentAnchor(bazi, state, currentAge);
      }
      if (stageNode) stageNode.textContent = state.current_stage || "未识别";
      if (stageNoteNode) {
        stageNoteNode.textContent = buildStageNote(state, time);
      }
      if (trendNode) {
        trendNode.textContent = deriveTrendLabel(state);
      }
      if (trendNoteNode) {
        trendNoteNode.textContent = safeArray(state.luck_cycle_theme).join(" / ") || "流月逢合";
      }
      if (energyNode) {
        energyNode.textContent = mapEnergyScore(state.energy_level);
      }
      if (energyBarNode) {
        energyBarNode.style.width = mapEnergyScore(state.energy_level) + "%";
      }
      if (energyNoteNode) {
        energyNoteNode.textContent = mapEnergyNote(state.energy_level);
      }
      if (riskNode) {
        riskNode.textContent = mapRiskScore(state.risk_level);
      }
      if (riskBarNode) {
        riskBarNode.style.width = mapRiskScore(state.risk_level) + "%";
      }
      if (riskNoteNode) {
        riskNoteNode.textContent = mapRiskNote(state.risk_level);
      }
      if (cycleNode) {
        var currentCycle = getCurrentLuckCycle(bazi, currentAge);
        cycleNode.textContent = currentCycle && currentCycle.pillar ? currentCycle.pillar + "大运" : "当前大运";
      }
      if (cycleNoteNode) {
        cycleNoteNode.textContent = buildCycleNote(bazi, state, currentAge);
      }
      if (actionNode) {
        var focus = safeArray((time.T0 && time.T0.recommended_focus) || state.capability_profile);
        actionNode.textContent = focus.length ? "建议：" + focus.slice(0, 2).join(" / ") : buildUserSummary(state).advice;
      }
      if (titleNode) titleNode.textContent = buildUserSummary(state).title;
      if (summaryNode) summaryNode.textContent = buildUserSummary(state).copy;
      if (sourceNode) sourceNode.textContent = getCurrentAnchor(bazi, state, currentAge);
    } else {
      var fallbackPoints = buildTrendPoints(null, report);
      renderTrendChart(chartNode, fallbackPoints);
      renderKlineAxis(axisNode, fallbackPoints);
      renderKlineInfo(klineInfoNode, fallbackPoints[0]);
      if (loadingNode) loadingNode.textContent = "暂未接入后端分析接口，显示本地结构图。";
    }
  }

  async function initAnalysisPage() {
    var structureNode = document.querySelector("[data-structure-points]");
    if (!structureNode) return;

    var profile = getBirthProfile();
    var userId = localStorage.getItem("lns.userId") || "";
    var currentAge = profile ? calcAge(profile.birthDate) : 36;
    var analysis = readCachedAnalysis();

    try {
      var fresh = await loadAnalysis(profile, userId, currentAge);
      if (fresh) analysis = fresh;
    } catch (error) {
      console.warn("analysis page request failed", error);
    }

    if (!analysis || !analysis.data) {
      setListItems("[data-structure-points]", [], "未找到分析数据，请先通过生成入口提交出生信息。");
      setListItems("[data-behavior-points]", [], "未找到分析数据，请先完成命理分析。");
      setListItems("[data-analysis-points]", [], "未找到分析数据，请先完成命理分析。");
      return;
    }

    var bazi = analysis.data.bazi_birth || {};
    var state = analysis.data.state || {};
    var time = analysis.data.time || {};
    var synth = analysis.data.synthesized || {};

    var titleNode = document.querySelector("[data-analysis-title]");
    var summaryNode = document.querySelector("[data-analysis-summary]");
    var structureSummaryNode = document.querySelector("[data-analysis-structure-summary]");
    var elementsSummaryNode = document.querySelector("[data-elements-summary]");
    var fourPillarsNode = document.querySelector("[data-four-pillars]");
    var anchorNode = document.querySelector("[data-analysis-anchor]");
    var advantageNode = document.querySelector("[data-analysis-advantage]");
    var riskNode = document.querySelector("[data-analysis-risk]");
    var adviceNode = document.querySelector("[data-analysis-advice]");
    var userSummary = buildUserSummary(state);
    var insights = buildAnalysisInsights(state, time, synth);

    if (titleNode) {
      titleNode.textContent = userSummary.title;
    }
    if (anchorNode) {
      anchorNode.textContent = getCurrentAnchor(bazi, state, currentAge);
    }
    if (summaryNode) {
      summaryNode.textContent = userSummary.copy;
    }
    if (structureSummaryNode) {
      structureSummaryNode.textContent = "日主 " + (bazi.day_master || "未识别") + "，主导结构 " + (state.dominant_structure || "未识别") + "。";
    }
    if (elementsSummaryNode) {
      elementsSummaryNode.textContent = "五行强弱使用标准化结果渲染，当前阶段重点观察偏旺与偏弱项。";
    }
    if (fourPillarsNode) {
      renderFourPillars(fourPillarsNode, bazi.four_pillars);
    }
    if (advantageNode) advantageNode.textContent = insights.advantage;
    if (riskNode) riskNode.textContent = insights.risk;
    if (adviceNode) adviceNode.textContent = insights.advice;

    var elements = bazi.normalized_elements || {};
    ["wood", "fire", "earth", "metal", "water"].forEach(function (key) {
      var node = document.querySelector('[data-element-score="' + key + '"]');
      if (node) node.textContent = elementScore(elements[key]);
    });

    var tenGods = bazi.ten_gods || {};
    var structurePoints = [];
    if (bazi.day_master) structurePoints.push("日主为" + bazi.day_master + "，是命局判断的核心参照。");
    if (state.dominant_structure) structurePoints.push("当前主导结构为“" + state.dominant_structure + "”，会直接影响行为方式与阶段感受。");
    if (Object.keys(tenGods).length) {
      structurePoints.push("十神落位：" + Object.keys(tenGods).map(function (key) {
        return translateTenGodKey(key) + " " + tenGods[key];
      }).join("，") + "。");
    }
    if (safeArray(bazi.deities).length) {
      structurePoints.push("当前可见神煞：" + safeArray(bazi.deities).slice(0, 4).join("、") + "。");
    }
    setListItems("[data-structure-points]", structurePoints, "暂无命局结构数据。");

    var behaviorPoints = [];
    behaviorPoints = behaviorPoints.concat(safeArray(state.capability_profile).map(function (item) {
      return "能力侧重点：" + item;
    }));
    behaviorPoints = behaviorPoints.concat(safeArray(state.behavior_patterns).map(function (item) {
      return "行为倾向：" + item;
    }));
    behaviorPoints = behaviorPoints.concat(safeArray(synth.synthesized_behavior).slice(0, 2).map(function (item) {
      return "综合判断：" + item;
    }));
    setListItems("[data-behavior-points]", behaviorPoints, "暂无性格与倾向分析。");

    var analysisPoints = [];
    if (state.current_stage) analysisPoints.push("当前阶段为“" + state.current_stage + "”。");
    if (safeArray(state.luck_cycle_theme).length) {
      analysisPoints.push("当前大运主题：" + safeArray(state.luck_cycle_theme).join(" / ") + "。");
    }
    if (time.T2 && time.T2.yearly_direction) {
      analysisPoints.push("年度方向：" + time.T2.yearly_direction + "。");
    }
    if (safeArray(time.T0 && time.T0.recommended_focus).length) {
      analysisPoints.push("当前更适合优先处理：" + safeArray(time.T0.recommended_focus).slice(0, 2).join(" / ") + "。");
    }
    if (safeArray(synth.synthesized_risk).length) {
      analysisPoints.push("需要重点留意：" + safeArray(synth.synthesized_risk).slice(0, 2).join(" / ") + "。");
    }
    setListItems("[data-analysis-points]", analysisPoints, "暂无当前命理解读。");
  }

  async function initYearDetailPage() {
    var titleNode = document.querySelector("[data-year-title]");
    if (!titleNode) return;

    var profile = getBirthProfile();
    var userId = localStorage.getItem("lns.userId") || "";
    var currentAge = profile ? calcAge(profile.birthDate) : 36;
    var selectedYear = Number(getSelectedYear() || toCurrentYear());
    var targetDate = String(selectedYear) + "-06-30";
    var year = targetDate.slice(0, 4);

    var summaryNode = document.querySelector("[data-year-summary]");
    var overviewNode = document.querySelector("[data-year-overview]");
    var overviewNoteNode = document.querySelector("[data-year-overview-note]");
    var careerNode = document.querySelector("[data-year-career]");
    var careerNoteNode = document.querySelector("[data-year-career-note]");
    var wealthNode = document.querySelector("[data-year-wealth]");
    var wealthNoteNode = document.querySelector("[data-year-wealth-note]");
    var healthNode = document.querySelector("[data-year-health]");
    var healthNoteNode = document.querySelector("[data-year-health-note]");
    var timelineNode = document.querySelector("[data-year-timeline]");
    var anchorNode = document.querySelector("[data-year-anchor]");

    if (anchorNode) {
      anchorNode.textContent = year + " 流年 · 年度节奏 · 行动建议";
    }

    if (!profile || !profile.birthDate || !profile.birthTime || !profile.city) {
      if (summaryNode) summaryNode.textContent = "未找到出生信息，请先通过生成入口提交。";
      setListItems("[data-year-guidance]", [], "未找到出生信息，请先生成报告。");
      renderTimelineItems(timelineNode, []);
      return;
    }

    var report = null;
    try {
      report = await generateReport(profile, userId, "yearly", targetDate);
    } catch (error) {
      if (summaryNode) summaryNode.textContent = "年报生成失败：" + error.message;
      setListItems("[data-year-guidance]", [], "当前无法生成年报，请稍后再试。");
      renderTimelineItems(timelineNode, []);
      return;
    }

    var content = report && report.data ? report.data : report;
    var overview = (content && content.overview) || {};
    var yearlyDirection = (content && content.yearly_direction) || {};
    var decadeContext = (content && content.decade_context) || {};
    var keyActions = (content && content.key_actions) || {};
    var capabilityAnalysis = (content && content.capability_analysis) || {};
    var riskAnalysis = (content && content.risk_analysis) || {};

    if (titleNode) titleNode.textContent = buildYearHeadline(year, overview, riskAnalysis);
    if (summaryNode) {
      summaryNode.textContent = buildYearSummary(overview, yearlyDirection, riskAnalysis);
    }

    if (overviewNode) overviewNode.textContent = mapLevelLabel(overview.energy);
    if (overviewNoteNode) {
      overviewNoteNode.textContent = "适合主动推进，先验证再放大。";
    }

    if (careerNode) careerNode.textContent = yearlyDirection.direction || "待观察";
    if (careerNoteNode) {
      careerNoteNode.textContent = yearlyDirection.structural_shift || "当前暂无额外结构切换说明。";
    }

    if (wealthNode) wealthNode.textContent = safeArray(capabilityAnalysis.capabilities).slice(0, 2).join(" / ") || "待识别";
    if (wealthNoteNode) {
      wealthNoteNode.textContent = safeArray(capabilityAnalysis.luck_cycle_theme).length
        ? "当前大运主题：" + safeArray(capabilityAnalysis.luck_cycle_theme).join(" / ") + "。"
        : "当前暂无大运主题说明。";
    }

    if (healthNode) healthNode.textContent = mapLevelLabel(riskAnalysis.level);
    if (healthNoteNode) {
      healthNoteNode.textContent = safeArray(riskAnalysis.synthesized_risks).slice(0, 2).join(" / ") || "控制节奏，避免过度承诺。";
    }

    var guidance = [];
    if (safeArray(yearlyDirection.strategic_focus).length) {
      guidance.push("适合：" + safeArray(yearlyDirection.strategic_focus).join(" / "));
    }
    if (safeArray(yearlyDirection.avoidance).length) {
      guidance.push("避免：" + safeArray(yearlyDirection.avoidance).join(" / "));
    }
    if (safeArray(riskAnalysis.constraints).length) {
      guidance.push("风险提示：" + safeArray(riskAnalysis.constraints).join(" / "));
    }
    if (safeArray(keyActions.P0).length) {
      guidance.push("优先动作：" + safeArray(keyActions.P0).join(" / "));
    }
    if (safeArray(keyActions.P1).length) {
      guidance.push("次级动作：" + safeArray(keyActions.P1).join(" / "));
    }
    setListItems("[data-year-guidance]", guidance, "当前暂无年度宜忌与动作建议。");

    renderTimelineItems(timelineNode, [
      {
        badge: String(Number(year) - 1).slice(-2),
        title: (Number(year) - 1) + " 年",
        note: "上一年，建议作为节奏参照，重点看结构延续与风险余波。",
        score: mapLevelLabel(overview.risk),
        caption: "上一年"
      },
      {
        badge: String(Number(year)).slice(-2),
        title: year + " 年",
        note: yearlyDirection.direction || "当前查看年份，正在生成年度方向说明。",
        score: mapLevelLabel(overview.energy),
        caption: "当前",
        isCurrent: true
      },
      {
        badge: String(Number(year) + 1).slice(-2),
        title: (Number(year) + 1) + " 年",
        note: safeArray(decadeContext.long_term_direction).slice(0, 2).join(" / ") || "下一年建议继续参考长期方向。",
        score: mapLevelLabel(riskAnalysis.level),
        caption: "下一年"
      }
    ]);
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

  if (!enforceResultAccess()) return;

  showActiveNav();
  renderUpgradeSlots();
  initProfileNodes();
  initCreatePage();
  initHomePage();
  initKlinePage();
  initAnalysisPage();
  initYearDetailPage();

  window.LNS_UI = {
    apiUrl: apiUrl,
    requestJson: requestJson,
    getBirthProfile: getBirthProfile,
    saveBirthProfile: saveBirthProfile,
    calcAge: calcAge,
    getEntitlement: getEntitlement,
  };
})();
