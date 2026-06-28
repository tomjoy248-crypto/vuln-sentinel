# screenshots/

This directory holds product screenshots referenced by the top-level `README.md`.

| File | Content |
|---|---|
| `home.png` | 首页主界面：产品定位 + 登录 + 快速扫描入口 |
| `report.png` | 扫描报告页：三区分层 + 评分仪表盘 + 证据列 |
| `fix.png` | 修复包下载页：多平台（Nginx/Apache/Express/Flask/Spring Boot/Cloudflare）配置生成 |
| `v11.4-example-scan.png` | V12 真实扫描 example.com 完整报告（评分 66，7 个发现） |
| `v11.4-home.png` | V12 首页：趋势图（7 个真实站点分数）|

## 占位说明

在真实截图补齐前，README 顶部的图片链接会显示为不可加载的占位。

如需添加截图：

1. 启动服务 `python3 main.py` 后访问 `http://localhost:8000`。
2. 截取首页 / 报告页 / 修复包下载页。
3. 把图片按上面的命名保存到本目录。
4. README 顶部的表格会自动渲染新截图。

**当前为占位目录，请勿删除本说明文件。**
