/**
 * 创建 HTML 元素并添加类名和内容
 * @param {string} tag 标签名
 * @param {string|string[]} classNames 类名
 * @param {string} textContent 文本内容
 * @returns {HTMLElement}
 */
export function createElement(tag, classNames = [], textContent = '') {
    const el = document.createElement(tag);
    if (Array.isArray(classNames)) {
        if (classNames.length) el.classList.add(...classNames);
    } else if (classNames) {
        el.classList.add(classNames);
    }
    if (textContent) el.textContent = textContent;
    return el;
}

/**
 * 清空容器内容
 * @param {HTMLElement} container 
 */
export function clearElement(container) {
    while (container.firstChild) {
        container.removeChild(container.firstChild);
    }
}