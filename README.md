一款专为国内用户设计的报刊内容抓取工具，支持人民日报 / 经济日报 / 纽约时报的 PDF / 图片下载，并通过通义千问免费 AI提取头版精华内容（头条新闻、关键数据、核心主题），全程无需代理，国内网络直接使用。
 核心功能
 
 多报刊支持：人民日报（PDF）、经济日报（PDF）、纽约时报（头版图片）
 
 AI 精华提取：基于通义千问免费多模态模型，智能解析图片 / PDF 内容

 结构化输出：自动提取头条新闻、关键数据、核心主题，格式规整

 本地保存：自动下载报刊文件并保存 AI 解析结果，方便后续使用

 国内适配：无需代理，通义千问 API 国内直连，无访问限制

 完善的错误处理：网络超时、文件缺失、API 调用失败等场景全覆盖

 环境要求

Python 3.7 及以上版本
操作系统：Windows/macOS/Linux（Windows 需额外安装 poppler）

 快速开始
 
1. 克隆仓库
bash
运行
git clone https://github.com/your-username/newspaper-ai-extractor.git
cd newspaper-ai-extractor

2. 安装依赖
bash
运行
# 基础依赖（所有系统）
pip install requests pillow pdf2image

# Windows用户额外安装poppler（PDF转图片依赖）
# 下载地址：https://github.com/oschwartz10612/poppler-windows/releases
# 解压后将bin目录添加到系统环境变量

# macOS用户安装poppler
brew install poppler

# Linux用户安装poppler
sudo apt-get install poppler-utils

3. 获取通义千问 API Key
访问阿里云通义千问控制台
登录后进入「API-KEY 管理」，创建并复制你的 API Key
替换代码中 TONGYI_API_KEY 变量的值：
python
运行
TONGYI_API_KEY = "你的通义千问API Key"

5. 运行程序
bash
运行
python newspaper_ai_extractor.py

7. 操作流程
选择日期（推荐选「昨天」，确保报纸已发布）
选择报纸（输入序号 1/2/3 或报纸名称）
等待报刊文件下载完成
选择是否进行 AI 解析
选择是否保存解析结果（自动保存到newspaper_copies文件夹）
📄 输出示例
plaintext
=== 《人民日报》20260219 精华内容 ===


【头条新闻1】习近平复信美国艾奥瓦州友人
 核心内容：习近平主席复信美国艾奥瓦州友人，回顾中美民间交往30余年历程，强调中美人民友谊是双边关系的重要基础，愿推动两国地方和民间层面交流合作走深走实。


【头条新闻2】“我们一家人在雄安过年”（新春走基层）
 核心内容：新春走基层记者探访雄安新区，记录当地居民在安置区过年的温馨场景，新区配套设施完善，就业、教育、医疗等民生保障到位，居民幸福感显著提升。


【头条新闻3】“电影+”融合发展势头正劲（向新向优的中国产业）
 核心内容：我国“电影+”融合发展模式成效显著，春节档票房同比增长15.6%，电影与文旅、科技、文创等产业深度融合，成为文化产业高质量发展的新引擎。

 关键数据：
• 中国冬奥代表团已获2金3银4铜（截至2026年2月19日）
• 2026春节档电影票房同比增长15.6%，创历史新高

 今日核心主题：
聚焦新春民生与国际交往，展现中国发展成就与开放合作的大国姿态
 目录结构
plaintext
newspaper-ai-extractor/
├── newspaper_images/       # 下载的报刊PDF/图片文件
├── newspaper_copies/       # AI解析后的精华内容文件
├── newspaper_ai_extractor.py  # 主程序文件
└── README.md               # 使用说明
 常见问题解决

问题 1：API 调用失败（401 错误）
检查 API Key 是否正确
确认已激活通义千问服务（控制台可查看）
确认 API Key 未过期或被禁用

问题 2：PDF 转图片失败
Windows 用户：确保 poppler 已安装并添加到环境变量
macOS/Linux 用户：确保已安装 poppler-utils
检查 PDF 文件是否损坏（重新下载后重试）

问题 3：AI 调用超时
检查网络连接是否稳定
延长代码中timeout参数（当前为 60 秒）
避开高峰期（如工作日 9:00-18:00）重试

问题 4：429 错误（调用次数超限）
通义千问免费版有每日调用额度限制
次日自动恢复额度，或升级为付费版

问题 5：报纸文件下载失败（404 错误）
选择的日期可能未发布报纸（如节假日）
优先选择「昨天」的日期重试
确认网络可正常访问人民日报 / 经济日报官网

 自定义扩展
1. 添加新报纸
修改NEWSPAPER_CONFIG字典，新增报纸配置：
python
运行
"新华日报": {
    "type": "pdf_dynamic",
    "layout_url_template": "新华日报版面页URL模板",
    "description": "新华日报",
}

2. 调整 AI 解析规则
修改analyze_with_free_ai函数中的prompt变量，可自定义：
提取的头条数量
摘要长度
输出格式
提取维度（如新增「政策解读」「国际要闻」等）

4. 调整输出格式
修改 AI 提示词中的输出模板，支持 Markdown/JSON/ 纯文本等格式。
 许可证
本项目基于 MIT 许可证开源，详见LICENSE文件。
 反馈与支持
提交 Issue：https://github.com/your-username/newspaper-ai-extractor/issues
邮箱：your-email@example.com
 贡献指南
欢迎提交 PR 改进代码：
Fork 本仓库
创建特性分支（git checkout -b feature/xxx）
提交修改（git commit -am 'Add xxx feature'）
推送到分支（git push origin feature/xxx）
创建 Pull Request
