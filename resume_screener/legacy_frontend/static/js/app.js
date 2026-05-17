let selectedFiles = [];

const fileInput = document.getElementById('resumeFiles');
const dropZone = document.getElementById('dropZone');
const browseBtn = document.getElementById('browseBtn');
const screenBtn = document.getElementById('screenBtn');
const resetBtn = document.getElementById('resetBtn');

fileInput.addEventListener('change', function () {
  addFiles(Array.from(this.files));
  this.value = '';
});

browseBtn.addEventListener('click', function (e) {
  e.stopPropagation();
  fileInput.click();
});

dropZone.addEventListener('dragenter', (event) => {
  event.preventDefault();
  dropZone.classList.add('dragover');
});

dropZone.addEventListener('dragover', (event) => {
  event.preventDefault();
  dropZone.classList.add('dragover');
});

dropZone.addEventListener('dragleave', (event) => {
  if (!dropZone.contains(event.relatedTarget)) {
    dropZone.classList.remove('dragover');
  }
});

dropZone.addEventListener('drop', (event) => {
  event.preventDefault();
  dropZone.classList.remove('dragover');
  addFiles(Array.from(event.dataTransfer.files));
});

function addFiles(files) {
  files.forEach((file) => {
    const extension = file.name.split('.').pop().toLowerCase();
    if (!['pdf', 'docx', 'txt'].includes(extension)) {
      return;
    }
    if (!selectedFiles.some((existing) => existing.name === file.name)) {
      selectedFiles.push(file);
    }
  });
  renderFileList();
}

function removeFile(name) {
  selectedFiles = selectedFiles.filter((file) => file.name !== name);
  renderFileList();
}

function renderFileList() {
  const fileList = document.getElementById('fileList');
  if (!fileList) {
    return;
  }
  fileList.innerHTML = selectedFiles
    .map(
      (file) =>
        `<div class="file-chip">📄 ${file.name}<button type="button" onclick="event.stopPropagation();removeFile('${file.name.replace(/'/g, "\\'")}')">✕</button></div>`
    )
    .join('');
}

screenBtn.addEventListener('click', runScreen);
resetBtn.addEventListener('click', resetForm);

async function runScreen() {
  const jobTitle = document.getElementById('job_title').value.trim() || 'Untitled Role';
  const jobDescription = document.getElementById('job_description').value.trim();

  if (!jobDescription) {
    alert('Please enter a job description.');
    return;
  }

  if (!selectedFiles.length) {
    alert('Please upload at least one resume.');
    return;
  }

  document.getElementById('form-area').style.display = 'none';
  document.getElementById('loading').style.display = 'block';

  const formData = new FormData();
  formData.append('job_title', jobTitle);
  formData.append('job_description', jobDescription);
  selectedFiles.forEach((file) => formData.append('resumes', file));

  try {
    const response = await fetch('/screen', { method: 'POST', body: formData });
    const data = await response.json();
    if (data.error) {
      alert(data.error);
      resetForm();
      return;
    }
    showResults(data);
    loadHistory();
  } catch (error) {
    alert('Error: ' + error.message + '\n\nMake sure the backend is running on port 5000.');
    resetForm();
  }
}

function showResults(data) {
  document.getElementById('loading').style.display = 'none';
  const results = document.getElementById('results');
  results.style.display = 'block';
  document.getElementById('resultsTitle').textContent = `Results — ${data.job_title}`;
  document.getElementById('resultsMeta').textContent = `${data.results.length} candidate${data.results.length !== 1 ? 's' : ''} screened${data.screening_id ? ` · Screening #${data.screening_id}` : ''}`;

  const candidateList = document.getElementById('candidateList');
  candidateList.innerHTML = data.results
    .map((candidate, index) => {
      const rankClass = index === 0 ? 'rank-1' : index === 1 ? 'rank-2' : index === 2 ? 'rank-3' : 'rank-other';
      const matchedHTML = candidate.matched_skills
        .slice(0, 8)
        .map((skill) => `<span class="skill-tag skill-match">✓ ${skill}</span>`)
        .join('');
      const missingHTML = candidate.missing_skills
        .slice(0, 5)
        .map((skill) => `<span class="skill-tag skill-miss">✗ ${skill}</span>`)
        .join('');
      const barColor = candidate.score >= 75 ? '#10b981' : candidate.score >= 55 ? '#3b82f6' : candidate.score >= 35 ? '#f59e0b' : '#ef4444';
      const experienceLabel = candidate.experience_years > 0 ? `${candidate.experience_years.toFixed(1)} yrs · ${candidate.experience_level}` : candidate.experience_level;

      return `
        <div class="candidate-card">
          <div class="rank-badge ${rankClass}">#${candidate.rank}</div>
          <div class="candidate-info">
            <h3>${candidate.filename}</h3>
            <div class="candidate-meta">${candidate.word_count} words in resume</div>
            <div class="experience-pill">${experienceLabel}</div>
            ${matchedHTML ? `<div class="skills-label">Matched Skills</div><div class="skills-row">${matchedHTML}</div>` : ''}
            ${missingHTML ? `<div class="skills-label">Skill Gaps</div><div class="skills-row">${missingHTML}</div>` : ''}
          </div>
          <div class="score-block">
            <div class="score-num" style="color:${barColor}">${candidate.score}</div>
            <div class="score-pct">/ 100</div>
            <div class="grade-badge" style="background:${barColor}22;color:${barColor};border:1px solid ${barColor}44">${candidate.grade.label}</div>
            <div class="score-bar-wrap">
              <div class="score-bar" style="width:${candidate.score}%;background:${barColor}"></div>
            </div>
          </div>
        </div>`;
    })
    .join('');
}

function resetForm() {
  selectedFiles = [];
  renderFileList();
  document.getElementById('form-area').style.display = 'block';
  document.getElementById('loading').style.display = 'none';
  document.getElementById('results').style.display = 'none';
  document.getElementById('candidateList').innerHTML = '';
  document.getElementById('job_description').value = '';
  document.getElementById('job_title').value = '';
}

async function loadHistory() {
  try {
    const response = await fetch('/history');
    const rows = await response.json();
    const tbody = document.getElementById('historyBody');
    if (!rows.length) {
      return;
    }
    tbody.innerHTML = rows
      .map(
        (row) =>
          `<tr class="clickable-row" onclick="loadScreening(${row.id})">
            <td style="color:var(--muted)">#${row.id}</td>
            <td><strong>${row.job_title}</strong></td>
            <td style="color:var(--muted)">${row.created_at}</td>
            <td>${row.total}</td>
            <td><strong style="color:var(--accent)">${row.top_score}%</strong></td>
          </tr>`
      )
      .join('');
  } catch (error) {
    console.warn('Unable to load screening history', error);
  }
}

async function loadScreening(screeningId) {
  document.getElementById('form-area').style.display = 'none';
  document.getElementById('loading').style.display = 'block';

  try {
    const response = await fetch(`/screening/${screeningId}`);
    const data = await response.json();
    if (data.error) {
      alert(data.error);
      resetForm();
      return;
    }
    showResults(data);
  } catch (error) {
    alert('Unable to load screening details.');
    resetForm();
  }
}

loadHistory();
