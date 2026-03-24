// js/config/site.js
const year = new Date().getFullYear();

export const siteConfig = {
    copyright: `© ${year} LingxingTech.`,
    icp: {
        text: "豫ICP备2025153149号-1",
        url: "https://beian.miit.gov.cn"
    },
    police: {
        enabled: true,
        text: "豫公网安备41030502001184号",
        url: "http://www.beian.gov.cn/portal/registerSystemInfo?recordcode=41030502001184",
        icon: "assets/icons/police_badge.png" // 警徽图标路径
    }
};