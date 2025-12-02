import { SchedulePage } from './pages/SchedulePage.js';

// 等待 DOM 加载完成
document.addEventListener('DOMContentLoaded', () => {
    const app = new SchedulePage();
    app.init().catch(err => console.error('App init failed:', err));
});