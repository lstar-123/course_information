import { SchedulePage } from './pages/SchedulePage.js';
import { siteConfig } from './config/site.js';

document.addEventListener('DOMContentLoaded', () => {
    // 1. 启动课程表逻辑
    const app = new SchedulePage();
    app.init().catch(err => console.error('App init failed:', err));

    // 2. 渲染 Footer 信息 (新增部分)
    document.getElementById('copyright-text').textContent = siteConfig.copyright;
    document.getElementById('icp-text').textContent = siteConfig.icp.text;
    
    // 处理公安备案显隐
    const policeLink = document.getElementById('police-link');
    const divider = document.querySelector('.site-footer .divider');
    if (siteConfig.police.enabled) {
        document.getElementById('police-text').textContent = siteConfig.police.text;
        policeLink.href = siteConfig.police.url;
    } else {
        if(policeLink) policeLink.style.display = 'none';
        if(divider) divider.style.display = 'none';
    }
});