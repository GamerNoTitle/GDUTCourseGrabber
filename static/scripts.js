document.addEventListener("DOMContentLoaded", function() {
    document.querySelector(".add-course").addEventListener("click", function() {
        addCourseEntry();
    });
    document.getElementById("fetch-courses-btn").addEventListener("click", fetchCourses);
    document.getElementById("start-qk-btn").addEventListener("click", start);
    document.getElementById("stop-qk-btn").addEventListener("click", stop);
    checkCoursesCount();
});

function addCourseEntry() {
    const courseEntry = document.createElement("div");
    courseEntry.className = "course-entry";
    courseEntry.innerHTML = `
        <input type="text" name="kcrwdm" placeholder="课程ID" required>
        <input type="text" name="kcmc" placeholder="课程名称" required>
        <input type="text" name="teacher" placeholder="老师名字" required>
        <button type="button" class="btn remove-course" onclick="removeCourse(this)">-</button>
    `;
    document.getElementById("courses-container").appendChild(courseEntry);
    checkCoursesCount();
}

function removeCourse(button) {
    const courseEntry = button.parentElement;
    const kcrwdm = courseEntry.querySelector('input[name="kcrwdm"]').value;

    if (!confirm(`确定要删除课程ID为 ${kcrwdm} 的课程吗？`)) {
        return;
    }

    fetch('/delete_course', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: new URLSearchParams({ 'kcrwdm': kcrwdm })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
            } else {
                courseEntry.remove();
                checkCoursesCount();
                alert('课程删除成功');
            }
        })
        .catch(error => {
            console.error('删除课程失败:', error);
            alert('删除课程失败，请查看控制台错误信息。');
        });
}

function checkCoursesCount() {
    const courseEntries = document.querySelectorAll(".course-entry");
    const removeButtons = document.querySelectorAll(".remove-course");

    if (courseEntries.length <= 1) {
        removeButtons.forEach(button => {
            button.disabled = false;
        });
    } else {
        removeButtons.forEach(button => {
            button.disabled = false;
        });
    }
}

function fetchCourses() {
    const cookie = document.getElementById("cookie").value;
    if (!cookie) {
        alert("请先输入 Cookie");
        return;
    }

    fetch('/fetch_courses', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: new URLSearchParams({ 'cookie': cookie })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
            } else {
                updateAvailableCourses(data.available_courses);
            }
        })
        .catch(error => {
            console.error('获取课程列表失败:', error);
            alert('获取课程列表失败，请查看控制台错误信息。');
        });
}

function updateAvailableCourses(courses) {
    const tableBody = document.getElementById("available-courses-list");
    tableBody.innerHTML = ''; // 清空当前列表

    courses.forEach(course => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${course.kcrwdm}</td>
            <td>${course.kcmc}</td>
            <td>${course.teaxm || '未知'}</td>
            <td>
                <form id="add-course-form-${course.kcrwdm}" class="add-course-form">
                    <input type="hidden" name="kcrwdm" value="${course.kcrwdm}">
                    <input type="hidden" name="kcmc" value="${course.kcmc}">
                    <input type="hidden" name="teacher" value="${course.teaxm || '未知'}">
                    <button type="button" class="btn add-course-btn" onclick="addCourse(this)">添加</button>
                </form>
            </td>
        `;
        tableBody.appendChild(row);
    });
}

function addCourse(button) {
    const form = button.closest('form');
    const formData = new FormData(form);

    fetch('/add_course', {
            method: 'POST',
            body: new URLSearchParams(formData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
            } else {
                alert('课程添加成功');
                updateCoursesList(data);
            }
        })
        .catch(error => {
            console.error('添加课程失败:', error);
            alert('添加课程失败，请查看控制台错误信息。');
        });
}

function updateCoursesList(course) {
    const coursesContainer = document.getElementById("courses-container");
    const newCourseEntry = document.createElement("div");
    newCourseEntry.className = "course-entry";
    newCourseEntry.innerHTML = `
        <input type="text" name="kcrwdm" value="${course.kcrwdm}" readonly>
        <input type="text" name="kcmc" value="${course.kcmc}" readonly>
        <input type="text" name="teacher" value="${course.teaxm}" readonly>
        <button type="button" class="btn remove-course" onclick="removeCourse(this)">-</button>
    `;
    coursesContainer.appendChild(newCourseEntry);
    checkCoursesCount();
}

function start() {
    fetch('/start', {
            method: 'POST',
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
        })
        .catch(error => {
            console.error('启动抢课失败:', error);
            alert('启动抢课失败，请查看控制台错误信息。');
        });
}

function stop() {
    fetch('/stop', {
            method: 'POST',
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
        })
        .catch(error => {
            console.error('停止抢课失败:', error);
            alert('停止抢课失败，请查看控制台错误信息。');
        });
}

async function fetchLogs() {
    try {
        let response = await fetch('/latest_log');
        let data = await response.json();
        let logContainer = document.getElementById('log-container');
        logContainer.innerText = data.logs;

        // 自动滚动到底部
        logContainer.scrollTop = logContainer.scrollHeight;
    } catch (error) {
        console.error('获取日志失败:', error);
    }
}

function startPolling() {
    fetchLogs();
    setInterval(fetchLogs, 500); // 每0.5秒刷新一次
}

function startPolling() {
    fetchLogs();
    setInterval(fetchLogs, 500); // 每0.5秒刷新一次
}

window.onload = startPolling;