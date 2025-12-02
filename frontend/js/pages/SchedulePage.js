import { fetchAllCourses } from '../api/fetchCourses.js';
import { WeekSelector } from '../components/WeekSelector.js';
import { ScheduleGrid } from '../components/ScheduleGrid.js';
import { formatDate } from '../utils/date.js';

export class SchedulePage {
    constructor() {
        this.rawCoursesMap = {}; // 修改：存储原始的 Map 结构
        this.weeksData = [];     // 整理后的数组，供 UI 使用
        this.currentWeekIdx = 0;

        this.weekSelector = null;
        this.scheduleGrid = null;
    }

    async init() {
        this.rawCoursesMap = await fetchAllCourses();
        
        // 校验数据
        if (!this.rawCoursesMap || Object.keys(this.rawCoursesMap).length === 0) {
            alert('未获取到课程数据');
            return;
        }

        // 处理数据（核心逻辑变更）
        this.processDataIntoWeeks();

        // 确定当前周
        this.findCurrentWeek();

        // 初始化 UI
        this.initUI();

        // 渲染
        this.render();
    }

    /**
     * 新的核心逻辑：
     * 1. 遍历 JSON 的 Key ("01", "02"...)
     * 2. 找到第一个包含有效课程的周，提取其日期作为“锚点”
     * 3. 根据锚点推算所有周（包括空周）的起始日期
     */
    processDataIntoWeeks() {
        const weekKeys = Object.keys(this.rawCoursesMap).sort(); // 确保按 "01", "02" 排序
        
        // 1. 寻找锚点日期 (Anchor Date)
        // 我们需要找到任意一节课的日期，算出那周的周一，以此推算整个学期的日历
        let anchorWeekIndex = -1;
        let anchorMonday = null;

        for (let i = 0; i < weekKeys.length; i++) {
            const key = weekKeys[i];
            const courses = this.rawCoursesMap[key];
            if (courses && courses.length > 0) {
                // 找到第一节课
                const firstCourseDate = new Date(courses[0].date);
                // 计算该日期所在周的周一
                const day = firstCourseDate.getDay(); // 0(Sun) - 6(Sat)
                const diff = firstCourseDate.getDate() - day + (day === 0 ? -6 : 1); // 调整到周一
                anchorMonday = new Date(firstCourseDate.setDate(diff));
                anchorWeekIndex = i;
                break;
            }
        }

        // 如果完全没有课程数据，默认第一周从今天开始（容错处理）
        if (!anchorMonday) {
            const today = new Date();
            const day = today.getDay();
            const diff = today.getDate() - day + (day === 0 ? -6 : 1);
            anchorMonday = new Date(today.setDate(diff));
            anchorWeekIndex = 0;
        }

        // 2. 生成所有周的数据结构
        this.weeksData = weekKeys.map((key, index) => {
            // 计算当前周相对于锚点周的偏移量（周数差）
            const weekOffset = index - anchorWeekIndex;
            
            // 计算当前周的 Monday
            const startCpy = new Date(anchorMonday);
            startCpy.setDate(anchorMonday.getDate() + (weekOffset * 7));
            
            // 计算当前周的 Sunday
            const endCpy = new Date(startCpy);
            endCpy.setDate(startCpy.getDate() + 6);

            const startDate = formatDate(startCpy);
            const endDate = formatDate(endCpy);

            // 整理当周课程为 Map 格式: { '2025-09-22': [Course, Course] }
            const daysObj = {};
            const courses = this.rawCoursesMap[key] || [];
            
            courses.forEach(c => {
                if (!daysObj[c.date]) {
                    daysObj[c.date] = [];
                }
                daysObj[c.date].push(c);
            });

            return {
                weekNum: key, // "01", "02"
                startDate: startDate,
                endDate: endDate,
                days: daysObj
            };
        });
    }

    findCurrentWeek() {
        const today = formatDate(new Date());
        // 查找今天是否在某个周的范围内
        const idx = this.weeksData.findIndex(w => today >= w.startDate && today <= w.endDate);
        
        if (idx >= 0) {
            this.currentWeekIdx = idx;
        } else {
            // 如果今天不在学期内：
            // 如果比第一周还早，显示第一周
            // 如果比最后一周还晚，显示最后一周
            if (this.weeksData.length > 0) {
                if (today < this.weeksData[0].startDate) this.currentWeekIdx = 0;
                else this.currentWeekIdx = this.weeksData.length - 1;
            }
        }
        
        document.getElementById('current-date-display').textContent = today;
    }

    initUI() {
        const selectorContainer = document.getElementById('week-selector-container');
        this.weekSelector = new WeekSelector(selectorContainer, (newIndex) => {
            this.currentWeekIdx = newIndex;
            this.render();
        });

        const gridContainer = document.getElementById('schedule-container');
        this.scheduleGrid = new ScheduleGrid(gridContainer);
    }

    render() {
        if (this.weeksData.length === 0) return;

        const currentWeekData = this.weeksData[this.currentWeekIdx];
        
        // 显示逻辑更新：使用 JSON 中的 key (如 "02")
        const label = `第 ${Number(currentWeekData.weekNum)} 周 (${currentWeekData.startDate.slice(5)} 起)`;
        
        this.weekSelector.update(this.currentWeekIdx, this.weeksData.length, label);
        this.scheduleGrid.render(currentWeekData);
    }
}