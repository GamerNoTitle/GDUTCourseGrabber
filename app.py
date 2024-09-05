from flask import Flask, render_template, request, redirect, url_for, jsonify
import httpx
import asyncio
import threading
import json
import os
import time
from datetime import datetime
import random
import string

app = Flask(__name__)
app.secret_key = ''.join(random.choices(string.ascii_letters + string.digits, k=16))  # 随机生成 secret_key
config_path = 'config.json'
logs_dir = 'logs'
log_file_path = os.path.join(logs_dir, 'latest.log')

# 初始化日志目录
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

# 全局变量用于抢课控制
stop_flag = threading.Event()

# 读取配置
def load_config():
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return {"account": {"cookie": ""}, "delay": 0.5, "courses": []}

# 保存配置
def save_config(config):
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

config = load_config()

# 写入日志
def log_message(message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] {message}"
    with open(log_file_path, 'a', encoding='utf-8') as log_file:
        log_file.write(log_entry + '\n')
    with open(os.path.join(logs_dir, f"{timestamp.replace(':', '-')}.log"), 'w', encoding='utf-8') as new_log_file:
        new_log_file.write(log_entry + '\n')

# 异步获取课程列表
async def fetch_courses(cookie):
    url = 'https://jxfw.gdut.edu.cn/xsxklist!getDataList.action'
    headers = {
        "x-requested-with": "XMLHttpRequest",
        "Cookie": cookie,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "https://jxfw.gdut.edu.cn",
        "DNT": "1",
        "Connection": "keep-alive",
        "Referer": "https://jxfw.gdut.edu.cn/xsxklist!xsmhxsxk.action",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }
    body = {
        "sort": "kcrwdm",
        "order": "asc"
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, params=body)
        response.raise_for_status()
        return response.json()

# 添加课程
@app.route('/add_course', methods=['POST'])
def add_course():
    kcrwdm = request.form.get('kcrwdm')
    kcmc = request.form.get('kcmc')
    teacher = request.form.get('teacher', '未知')  # 默认值为'未知'

    # 校验数据
    if not kcrwdm or not kcmc:
        return jsonify({"error": "课程ID和课程名称不能为空"}), 400

    # 更新配置
    course_exists = any(course['kcrwdm'] == kcrwdm for course in config['courses'])
    if course_exists:
        return jsonify({"error": "课程已经存在"}), 400

    # 添加课程到配置
    config['courses'].append({
        'kcrwdm': kcrwdm,
        'kcmc': kcmc,
        'teacher': teacher
    })
    save_config(config)
    log_message(f"添加课程成功，课程ID: {kcrwdm}, 名称: {kcmc}, 老师: {teacher}")
    return jsonify({"success": True, "kcrwdm": kcrwdm, "kcmc": kcmc, "teacher": teacher})

# 抢课功能
def grabCourse(kcrwdm, kcmc, teacher, cookie):
    url = 'https://jxfw.gdut.edu.cn/xsxklist!getAdd.action'
    headers = {
        "Host": "jxfw.gdut.edu.cn",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://jxfw.gdut.edu.cn",
        "DNT": "1",
        "Connection": "keep-alive",
        "Referer": "https://jxfw.gdut.edu.cn/xskjcjxx!kjcjList.action",
        "Cookie": cookie,
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }
    data = f'kcrwdm={kcrwdm}&kcmc={kcmc}'
    try:
        response = httpx.post(url, headers=headers, data=data.encode('utf-8'))
        log_message(f"抢课请求发送，课程ID: {kcrwdm}, 名称: {kcmc}, 老师: {teacher}, 响应: {response.text}")
    except Exception as e:
        log_message(f"抢课失败: {str(e)}")

# 运行抢课任务
def startGrabCourseTask(config):
    while not stop_flag.is_set():
        for course in config['courses']:
            grabCourse(course['kcrwdm'], course['kcmc'], course['teacher'], config['account']['cookie'])
            time.sleep(config['delay'])

# 启动抢课线程
def startGrabCourseThread():
    global stop_flag
    stop_flag.clear()
    threading.Thread(target=startGrabCourseTask, args=(config,), daemon=True).start()
    log_message("抢课已开始")

# 停止抢课
def stopGrabCouse():
    stop_flag.set()
    log_message("抢课已停止")

# 首页
@app.route('/')
def index():
    logs = ""
    if os.path.exists(log_file_path):
        with open(log_file_path, 'r', encoding='utf-8') as log_file:
            logs = log_file.read()
    return render_template('index.html', config=config, logs=logs)

# 更新配置
@app.route('/update_config', methods=['POST'])
def update_config():
    cookie = request.form.get('cookie')
    delay = float(request.form.get('delay', 0.5))
    courses = [{'kcrwdm': request.form.getlist('kcrwdm')[i], 'kcmc': request.form.getlist('kcmc')[i], 'teacher': request.form.getlist('teacher')[i]} for i in range(len(request.form.getlist('kcrwdm')))]
    config['account']['cookie'] = cookie
    config['delay'] = delay
    config['courses'] = courses
    save_config(config)
    log_message("配置已更新")
    return redirect(url_for('index'))

# 获取课程列表
@app.route('/fetch_courses', methods=['POST'])
async def fetch_courses_endpoint():
    cookie = request.form.get('cookie').replace("b'", "").replace("'", "")
    
    if not cookie:
        return jsonify({"error": "Cookie 不能为空"}), 400

    # 保存 cookie 到配置文件
    config['account']['cookie'] = cookie
    save_config(config)
    log_message(f"Cookie 已保存: {cookie}")

    try:
        courses_data = await fetch_courses(cookie)
        available_courses = courses_data.get('rows', [])
        return jsonify({"available_courses": available_courses}), 200
    except Exception as e:
        log_message(f"获取课程列表失败: {str(e)}")
        return jsonify({"error": f"获取课程列表失败: {str(e)}"}), 500
    
# 删除课程
@app.route('/delete_course', methods=['POST'])
def delete_course():
    kcrwdm = request.form.get('kcrwdm')

    if not kcrwdm:
        return jsonify({"error": "课程ID不能为空"}), 400

    # 查找并删除课程
    courses = [course for course in config['courses'] if course['kcrwdm'] != kcrwdm]
    
    if len(courses) == len(config['courses']):
        return jsonify({"error": "课程未找到"}), 404

    config['courses'] = courses
    save_config(config)
    log_message(f"课程已删除，课程ID: {kcrwdm}")
    return jsonify({"success": True}), 200

# 启动抢课
@app.route('/start', methods=['POST'])
def startGrabCourseRoute():
    startGrabCourseThread()
    return jsonify({"message": "抢课已开始"}), 200

# 停止抢课
@app.route('/stop', methods=['POST'])
def stopGrabCourseRoute():
    stopGrabCouse()
    return jsonify({"message": "抢课已停止"}), 200

# 获取最新日志
@app.route('/latest_log', methods=['GET'])
def latest_log():
    if os.path.exists(log_file_path):
        with open(log_file_path, 'r', encoding='utf-8') as log_file:
            logs = log_file.read()
        return jsonify({"logs": logs})
    return jsonify({"logs": ""})

if __name__ == "__main__":
    app.run(debug=True)
