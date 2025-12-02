你是一名专业前端工程师，请基于我提供的 JSON 数据结构生成一个完整的前端课程表网页。

【项目背景】
- JSON 文件路径：/dist/all_weeks_courses.json
- 每周包含多个课程；
- 每个课程包含字段：
  - weekday (Monday–Sunday)
  - date (2025-xx-xx)
  - section ("第四大节 (07,08小节) 15:55-17:30" 这种格式)
  - name
  - classroom

【页面需求】

**请你按照以下要求，生成一个完整的前端项目目录（frontend/），用于展示课程表信息：**

------

## 🏗 **项目基础要求**

- 项目名称：**course-schedule-frontend**
- 技术栈：
  - **Vanilla JavaScript（纯 JS，不用 React / Vue）**
  - **HTML + CSS**
  - **模块化 ES Modules**
  - **采用企业级目录结构**
  - **必须适配移动端（响应式）**
  - **从 /dist/all_weeks_courses.json 获取课程信息并渲染**

------

## 📁 **目录结构（必须生成所有文件）**

```
frontend/
│── index.html
│── package.json（可选）
│── README.md
│
├── assets/
│   ├── styles/
│   │   ├── base.css
│   │   ├── layout.css
│   │   └── components.css
│   └── icons/
│       └── calendar.svg（或其他你生成的图标）
│
├── js/
│   ├── main.js
│   ├── api/
│   │   └── fetchCourses.js
│   ├── utils/
│   │   ├── date.js
│   │   └── dom.js
│   ├── components/
│   │   ├── WeekSelector.js
│   │   ├── CourseCard.js
│   │   └── ScheduleGrid.js
│   └── pages/
│       └── SchedulePage.js
└── dist/
    └── all_weeks_courses.json （已存在，不需要生成内容）
```

------

## 🎨 **UI 设计要求**

- 干净、现代、简约风格
- 统一主色：蓝色 (#2979ff)
- 字体：系统字体（San Francisco / Segoe UI / PingFang）
- 手机上可单手操作
- 课程卡片使用卡片式设计、圆角、阴影
- 周份选择器（Week Selector）可左右切换
- 每天显示对应日期（YYYY-MM-DD）
- 网格布局展示 Mon–Sun × Section

------

## 🧩 **功能要求**

### 1. **自动加载 JSON**

```
fetch('/dist/all_weeks_courses.json')
```

### 2. **展示内容**

课程必须显示：

- weekday
- date
- section（例如“第四大节 (07,08小节) 15:55-17:30”）
- name
- classroom

### 3. **Week Selector**

- 默认显示当前周
- 支持左右切换（上一周 / 下一周）
- 自动更新课程表

### 4. **Schedule Grid**

- 星期为列（Mon–Sun）
- 节次为行（从 XLS 中读取）
- 课程用 CourseCard 渲染
- 多课程支持堆叠显示

------

## 📦 **输出要求**

你需要输出完整项目的所有文件内容，每个文件用独立的代码块组织：

例如：

```
📄 index.html
~~~html
...
~~~

📄 js/main.js
~~~javascript
...
~~~
```

所有文件都必须生成，不能省略。

------

## 📝 **代码质量要求**

- 每个 JS 文件必须写明用途
- 所有函数必须有注释
- 严格使用模块化（import / export）
- CSS 必须拆分为 base / layout / components 三个层级
- HTML 语义化（header / main / section）
- 任何硬编码常量必须放入单独的 config 部分

------

## 🔥 **最终输出格式**

> **请按上述规范生成完整的 frontend 目录所有文件。**