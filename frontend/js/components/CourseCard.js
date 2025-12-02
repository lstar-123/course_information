import { createElement } from '../utils/dom.js';

/**
 * 渲染单个课程卡片
 * @param {Object} course 课程数据对象
 * @returns {HTMLElement}
 */
export function CourseCard(course) {
    const card = createElement('div', 'course-card');

    // 1. 节次信息 (Section)
    // 截取前面部分使其简洁，或者显示全部。这里显示全部但样式控制
    const sectionBadge = createElement('div', 'course-section', course.section.split(' ')[0]); // "第四大节"
    
    // 2. 课程名称
    const nameEl = createElement('div', 'course-name', course.name);

    // 3. 详细信息容器
    const infoContainer = createElement('div', 'course-info');

    // 教室
    const roomRow = createElement('div', 'info-row');
    roomRow.innerHTML = `<span>📍 ${course.classroom}</span>`;
    
    // 时间 (从 section 字符串中提取时间部分)
    const timeRow = createElement('div', 'info-row');
    const timeMatch = course.section.match(/\d{1,2}:\d{2}-\d{1,2}:\d{2}/);
    const timeStr = timeMatch ? timeMatch[0] : '';
    timeRow.innerHTML = `<span>⏰ ${timeStr}</span>`;

    infoContainer.appendChild(roomRow);
    if(timeStr) infoContainer.appendChild(timeRow);

    card.appendChild(sectionBadge);
    card.appendChild(nameEl);
    card.appendChild(infoContainer);

    return card;
}