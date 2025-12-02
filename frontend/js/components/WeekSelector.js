import { createElement, clearElement } from '../utils/dom.js';

export class WeekSelector {
    constructor(container, onChange) {
        this.container = container;
        this.onChange = onChange;
        this.currentWeekIndex = 0;
        this.totalWeeks = 0;
        this.weekLabel = '';
    }

    /**
     * 更新组件状态并重绘
     * @param {number} index 当前周索引
     * @param {number} total 总周数
     * @param {string} label 显示文本 (e.g. "第 3 周")
     */
    update(index, total, label) {
        this.currentWeekIndex = index;
        this.totalWeeks = total;
        this.weekLabel = label;
        this.render();
    }

    render() {
        clearElement(this.container);

        const wrapper = createElement('div', 'week-selector');

        // 上一周按钮
        const prevBtn = createElement('button', 'week-btn', '<');
        prevBtn.disabled = this.currentWeekIndex <= 0;
        prevBtn.onclick = () => this.onChange(this.currentWeekIndex - 1);

        // 显示文本
        const display = createElement('div', 'week-display', this.weekLabel);

        // 下一周按钮
        const nextBtn = createElement('button', 'week-btn', '>');
        nextBtn.disabled = this.currentWeekIndex >= this.totalWeeks - 1;
        nextBtn.onclick = () => this.onChange(this.currentWeekIndex + 1);

        wrapper.appendChild(prevBtn);
        wrapper.appendChild(display);
        wrapper.appendChild(nextBtn);

        this.container.appendChild(wrapper);
    }
}