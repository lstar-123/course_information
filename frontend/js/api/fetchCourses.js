/**
 * 从 JSON 文件获取课程数据
 * @returns {Promise<Array>} 课程列表
 */
export async function fetchAllCourses() {
    try {
        const response = await fetch('./dist/all_weeks_courses.json');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        // 返回的是对象: { "01": [], "02": [...] }
        const data = await response.json();
        return data; 
    } catch (error) {
        console.error('Failed to fetch courses:', error);
        return {}; // 失败时返回空对象
    }
}