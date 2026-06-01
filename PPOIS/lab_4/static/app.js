const API_BASE = '/api/v1';

let currentSection = 'students';
let questions = [];

function showSection(section) {
    document.querySelectorAll('.section').forEach(s => s.classList.add('hidden'));
    document.getElementById(section).classList.remove('hidden');
    currentSection = section;

    document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');

    if (section === 'students') loadStudents();
    else if (section === 'teachers') loadTeachers();
    else if (section === 'materials') loadMaterials();
    else if (section === 'assignments') loadAssignments();
    else if (section === 'tests') loadTests();
    else if (section === 'forum') loadThreads();
    else if (section === 'lectures') loadLectures();
}

function showMessage(text, type = 'success') {
    const msg = document.getElementById('message');
    msg.textContent = text;
    msg.className = `message show ${type}`;
    setTimeout(() => msg.classList.remove('show'), 3000);
}

async function apiCall(method, endpoint, body = null) {
    try {
        const options = { method, headers: { 'Content-Type': 'application/json' } };
        if (body) options.body = JSON.stringify(body);

        const res = await fetch(`${API_BASE}${endpoint}`, options);
        const data = await res.json();

        if (!res.ok) throw new Error(data.message || 'API Error');
        return data;
    } catch (err) {
        showMessage(err.message, 'error');
        throw err;
    }
}

async function createStudent() {
    const login = document.getElementById('studentLogin').value.trim();
    const name = document.getElementById('studentName').value.trim();

    if (!login || !name) {
        showMessage('Заполните все поля', 'error');
        return;
    }

    try {
        await apiCall('POST', '/students', { login, name });
        showMessage('Студент создан');
        document.getElementById('studentLogin').value = '';
        document.getElementById('studentName').value = '';
        loadStudents();
    } catch (err) {}
}

async function loadStudents() {
    try {
        const data = await apiCall('GET', '/students');
        const list = document.getElementById('studentsList');
        list.innerHTML = '';

        data.data.students.forEach(student => {
            const item = document.createElement('div');
            item.className = 'list-item';
            item.innerHTML = `
                <div class="list-item-content">
                    <strong>${student.login}</strong> - ${student.name}
                    <br><small>ID: ${student.student_id}</small>
                </div>
            `;
            list.appendChild(item);
        });
    } catch (err) {}
}

async function createTeacher() {
    const login = document.getElementById('teacherLogin').value.trim();
    const name = document.getElementById('teacherName').value.trim();

    if (!login || !name) {
        showMessage('Заполните все поля', 'error');
        return;
    }

    try {
        await apiCall('POST', '/teachers', { login, name });
        showMessage('Преподаватель создан');
        document.getElementById('teacherLogin').value = '';
        document.getElementById('teacherName').value = '';
        loadTeachers();
    } catch (err) {}
}

async function loadTeachers() {
    try {
        const data = await apiCall('GET', '/teachers');
        const list = document.getElementById('teachersList');
        list.innerHTML = '';

        data.data.teachers.forEach(teacher => {
            const item = document.createElement('div');
            item.className = 'list-item';
            item.innerHTML = `
                <div class="list-item-content">
                    <strong>${teacher.login}</strong> - ${teacher.name}
                    <br><small>ID: ${teacher.teacher_id}</small>
                </div>
            `;
            list.appendChild(item);
        });
    } catch (err) {}
}

async function addMaterial() {
    const title = document.getElementById('materialTitle').value.trim();
    const content = document.getElementById('materialContent').value.trim();

    if (!title || !content) {
        showMessage('Заполните все поля', 'error');
        return;
    }

    try {
        await apiCall('POST', '/materials', { title, content });
        showMessage('Материал добавлен');
        document.getElementById('materialTitle').value = '';
        document.getElementById('materialContent').value = '';
        loadMaterials();
    } catch (err) {}
}

async function loadMaterials() {
    try {
        const data = await apiCall('GET', '/materials');
        const list = document.getElementById('materialsList');
        list.innerHTML = '';

        data.data.materials.forEach(material => {
            const item = document.createElement('div');
            item.className = 'list-item';
            item.innerHTML = `
                <div class="list-item-content">
                    <strong>${material.title}</strong>
                    <br><small>ID: ${material.material_id}</small>
                </div>
            `;
            list.appendChild(item);
        });
    } catch (err) {}
}

async function addAssignment() {
    const title = document.getElementById('assignmentTitle').value.trim();
    const description = document.getElementById('assignmentDesc').value.trim();

    if (!title || !description) {
        showMessage('Заполните все поля', 'error');
        return;
    }

    try {
        await apiCall('POST', '/assignments', { title, description });
        showMessage('Задание добавлено');
        document.getElementById('assignmentTitle').value = '';
        document.getElementById('assignmentDesc').value = '';
        loadAssignments();
    } catch (err) {}
}

async function loadAssignments() {
    try {
        const data = await apiCall('GET', '/assignments');
        const list = document.getElementById('assignmentsList');
        list.innerHTML = '<h3>Задания</h3>';

        data.data.assignments.forEach(assignment => {
            const item = document.createElement('div');
            item.className = 'list-item';
            item.innerHTML = `
                <div class="list-item-content">
                    <strong>${assignment.title}</strong>
                    <br><small>ID: ${assignment.assignment_id}</small>
                </div>
            `;
            list.appendChild(item);
        });

        loadSubmissions();
    } catch (err) {}
}

async function loadSubmissions() {
    try {
        const data = await apiCall('GET', '/submissions');
        const list = document.getElementById('submissionsList');
        list.innerHTML = '<h3>Сдачи заданий</h3>';

        data.data.submissions.forEach(sub => {
            const item = document.createElement('div');
            item.className = 'list-item';
            item.innerHTML = `
                <div class="list-item-content">
                    Студент ${sub.student_id} → Задание ${sub.assignment_id}
                    <br>Ответ: ${sub.answer}
                    <br>Оценка: ${sub.grade ?? 'не оценено'}
                </div>
            `;
            list.appendChild(item);
        });
    } catch (err) {}
}

function addQuestion() {
    const container = document.getElementById('questionsInput');
    const idx = questions.length;

    const questionDiv = document.createElement('div');
    questionDiv.className = 'question-item';
    questionDiv.id = `question-${idx}`;
    questionDiv.innerHTML = `
        <input type="text" placeholder="Вопрос" class="question-prompt" />
        <div class="options-list">
            <input type="text" placeholder="Опция 1" class="question-option" />
            <input type="text" placeholder="Опция 2" class="question-option" />
        </div>
        <select class="question-correct">
            <option value="0">Правильный ответ: 1</option>
            <option value="1">Правильный ответ: 2</option>
        </select>
        <button class="question-remove" onclick="removeQuestion(${idx})">Удалить вопрос</button>
    `;
    container.appendChild(questionDiv);
    questions.push({});
}

function removeQuestion(idx) {
    const elem = document.getElementById(`question-${idx}`);
    if (elem) elem.remove();
}

async function createTest() {
    const title = document.getElementById('testTitle').value.trim();
    if (!title) {
        showMessage('Введите название теста', 'error');
        return;
    }

    const container = document.getElementById('questionsInput');
    const questionElems = container.querySelectorAll('.question-item');

    if (questionElems.length === 0) {
        showMessage('Добавьте хотя бы один вопрос', 'error');
        return;
    }

    const questionsData = Array.from(questionElems).map(elem => {
        const prompt = elem.querySelector('.question-prompt').value.trim();
        const options = Array.from(elem.querySelectorAll('.question-option')).map(o => o.value.trim());
        const correctIndex = parseInt(elem.querySelector('.question-correct').value);

        return { prompt, options, correct_index: correctIndex };
    });

    try {
        await apiCall('POST', '/tests', { title, questions: questionsData });
        showMessage('Тест создан');
        document.getElementById('testTitle').value = '';
        document.getElementById('questionsInput').innerHTML = '';
        questions = [];
        loadTests();
    } catch (err) {}
}

async function loadTests() {
    try {
        const data = await apiCall('GET', '/tests');
        const list = document.getElementById('testsList');
        list.innerHTML = '<h3>Тесты</h3>';

        data.data.tests.forEach(test => {
            const item = document.createElement('div');
            item.className = 'list-item';
            item.innerHTML = `
                <div class="list-item-content">
                    <strong>${test.title}</strong>
                    <br><small>ID: ${test.test_id}</small>
                </div>
            `;
            list.appendChild(item);
        });

        loadAttempts();
    } catch (err) {}
}

async function loadAttempts() {
    try {
        const data = await apiCall('GET', '/attempts');
        const list = document.getElementById('attemptsList');
        list.innerHTML = '<h3>Попытки прохождения</h3>';

        data.data.attempts.forEach(attempt => {
            const item = document.createElement('div');
            item.className = 'list-item';
            item.innerHTML = `
                <div class="list-item-content">
                    Студент ${attempt.student_id} → Тест ${attempt.test_id}
                    <br>Баллы: ${attempt.score}
                </div>
            `;
            list.appendChild(item);
        });
    } catch (err) {}
}

async function createThread() {
    const title = document.getElementById('threadTitle').value.trim();

    if (!title) {
        showMessage('Введите название темы', 'error');
        return;
    }

    try {
        await apiCall('POST', '/threads', { title });
        showMessage('Тема создана');
        document.getElementById('threadTitle').value = '';
        loadThreads();
    } catch (err) {}
}

async function loadThreads() {
    try {
        const data = await apiCall('GET', '/threads');
        const list = document.getElementById('threadsList');
        list.innerHTML = '';

        data.data.threads.forEach(thread => {
            const item = document.createElement('div');
            item.className = 'list-item';
            item.innerHTML = `
                <div class="list-item-content">
                    <strong>${thread.title}</strong>
                    <br><small>ID: ${thread.thread_id} | Постов: ${thread.posts_count}</small>
                </div>
            `;
            list.appendChild(item);
        });
    } catch (err) {}
}

async function scheduleLecture() {
    const topic = document.getElementById('lectureTopic').value.trim();

    if (!topic) {
        showMessage('Введите тему лекции', 'error');
        return;
    }

    try {
        await apiCall('POST', '/lectures', { topic });
        showMessage('Лекция запланирована');
        document.getElementById('lectureTopic').value = '';
        loadLectures();
    } catch (err) {}
}

async function loadLectures() {
    try {
        const data = await apiCall('GET', '/lectures');
        const list = document.getElementById('lecturesList');
        list.innerHTML = '';

        data.data.lectures.forEach(lecture => {
            const status = lecture.is_live ? '🔴 LIVE' : '⏳ Запланирована';
            const item = document.createElement('div');
            item.className = 'list-item';
            item.innerHTML = `
                <div class="list-item-content">
                    <strong>${lecture.topic}</strong>
                    <br><small>ID: ${lecture.lecture_id} | ${status}</small>
                </div>
            `;
            list.appendChild(item);
        });
    } catch (err) {}
}

window.addEventListener('DOMContentLoaded', () => {
    showSection('students');
});
