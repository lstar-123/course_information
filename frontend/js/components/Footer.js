// js/components/Footer.js
import { siteConfig } from '../config/site.js';

export function renderFooter() {
    // 1. 设置版权
    const copyrightEl = document.getElementById('copyright-text');
    if (copyrightEl) copyrightEl.textContent = siteConfig.copyright;

    // 2. 设置 ICP
    const icpTextEl = document.getElementById('icp-text');
    if (icpTextEl) icpTextEl.textContent = siteConfig.icp.text;

    // 3. 设置公安备案
    const policeLinkEl = document.getElementById('police-link');
    const policeTextEl = document.getElementById('police-text');
    
    if (siteConfig.police.enabled) {
        policeLinkEl.href = siteConfig.police.url;
        policeTextEl.textContent = siteConfig.police.text;
    } else {
        // 如果未开启公安备案，移除该元素和分隔符
        policeLinkEl.style.display = 'none';
        document.querySelector('.divider').style.display = 'none';
    }
}