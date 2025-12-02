import { createElement, clearElement } from '../utils/dom.js';
import { formatFriendlyDate, isSameDate, getSectionStartTime, getTodayInBeijing } from '../utils/date.js';
import { CourseCard } from './CourseCard.js';

export class ScheduleGrid {
    constructor(container) {
        this.container = container;
        this.weekDays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
    }

    /**
     * 渲染某一周的课程
     * @param {Object} weekData 
     */
    render(weekData) {
        clearElement(this.container);
        const grid = createElement('div', 'schedule-grid');
        
        // 1. 提取并排序当前周所有唯一的节次 (Sections)
        // 用于确定 Grid 的行索引
        const allSections = new Set();
        Object.values(weekData.days).forEach(dayCourses => {
            dayCourses.forEach(course => allSections.add(course.section));
        });

        // 排序节次 (早 -> 晚)
        const sortedSections = Array.from(allSections).sort((a, b) => {
            return getSectionStartTime(a) - getSectionStartTime(b);
        });

        // 2. 遍历 7 天生成列
        let currentIterateDate = new Date(weekData.startDate);

        for (let i = 0; i < 7; i++) {
            const dateStr = currentIterateDate.toISOString().split('T')[0];
            const courses = weekData.days[dateStr] || [];
            
            // 创建天容器 (在移动端是卡片容器，在桌面端通过 display: contents 变为虚拟容器)
            const dayColumn = createElement('div', 'day-column');
            
            // 设置 CSS 变量，告诉 CSS 这一列属于 Grid 的第几列 (1-7)
            dayColumn.style.setProperty('--day-col', i + 1);

            // 设置当前时间
            const todayStr = getTodayInBeijing();
            const isToday = isSameDate(dateStr, todayStr);
            if (isToday) dayColumn.classList.add('is-today');

            // --- A. 表头 (Grid Row 1) ---
            const header = createElement('div', 'day-header');
            header.innerHTML = `
                <span class="day-name">${this.weekDays[i]}</span>
                <span class="day-date">${formatFriendlyDate(dateStr)}</span>
            `;
            dayColumn.appendChild(header);

            // --- B. 课程卡片 (Grid Row 2+) ---
            // 我们不需要填充空位，直接渲染存在的课程，通过 CSS 指定它去哪一行
            courses.forEach(course => {
                const card = CourseCard(course);
                
                // 找到该课程属于第几个节次 (Index + 2, 因为 Header 是 Row 1)
                const sectionIndex = sortedSections.indexOf(course.section);
                if (sectionIndex !== -1) {
                    card.style.setProperty('--section-row', sectionIndex + 2);
                }
                
                dayColumn.appendChild(card);
            });

            // (可选) 如果需要填补视觉空白，可以在这里根据 sortedSections 插入占位符
            // 但使用了 Grid Row 定位后，视觉上已经是对齐的了。

            grid.appendChild(dayColumn);
            
            // 日期 + 1
            currentIterateDate.setDate(currentIterateDate.getDate() + 1);
        }

        this.container.appendChild(grid);
    }
}