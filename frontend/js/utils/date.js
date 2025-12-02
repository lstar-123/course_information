/**
 * 解析节次字符串获取开始时间，用于排序
 * 格式示例: "第一大节 (01,02小节) 08:20-09:55"
 * @param {string} sectionStr 
 * @returns {number} 用于排序的分钟数
 */
export function getSectionStartTime(sectionStr) {
    // 匹配 "08:20" 这种格式
    const match = sectionStr.match(/(\d{1,2}):(\d{2})/);
    if (match) {
        return parseInt(match[1]) * 60 + parseInt(match[2]);
    }
    // 如果没有时间，尝试匹配 "第一大节"
    if (sectionStr.includes("第一")) return 1;
    if (sectionStr.includes("第二")) return 2;
    if (sectionStr.includes("第三")) return 3;
    if (sectionStr.includes("第四")) return 4;
    if (sectionStr.includes("第五")) return 5;
    
    return 9999;
}

// ... 其他函数保持不变 (formatDate, formatFriendlyDate, isSameDate)
export function formatDate(dateObj) {
    const year = dateObj.getFullYear();
    const month = String(dateObj.getMonth() + 1).padStart(2, '0');
    const day = String(dateObj.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

export function formatFriendlyDate(dateStr) {
    const parts = dateStr.split('-');
    return `${parts[1]}月${parts[2]}日`;
}

export function isSameDate(date1, date2) {
    return date1 === date2;
}