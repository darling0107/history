# Supabase 设置指南

本指南将帮助您设置 Supabase 数据库以存储用户数据。

## 步骤 1: 创建 Supabase 项目

1. 访问 [Supabase](https://supabase.com) 并注册账户
2. 点击 "New Project" 创建新项目
3. 填写项目信息：
   - 项目名称：`historiaquest` (或您喜欢的名称)
   - 数据库密码：设置一个强密码并保存
   - 区域：选择离您最近的区域
4. 等待项目创建完成（约 2 分钟）

## 步骤 2: 获取 API 密钥

1. 在项目仪表板中，点击左侧菜单的 "Settings" (设置)
2. 选择 "API"
3. 复制以下信息：
   - **Project URL**: `https://xxxxx.supabase.co`
   - **anon public key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

## 步骤 3: 配置环境变量

1. 在项目根目录创建 `.env` 文件（如果不存在）
2. 添加以下内容：

```env
VITE_SUPABASE_URL=your_project_url_here
VITE_SUPABASE_ANON_KEY=your_anon_key_here
VITE_DEEPSEEK_API_KEY=your_deepseek_api_key
```

3. 将 `your_project_url_here` 和 `your_anon_key_here` 替换为您在步骤 2 中复制的值

## 步骤 4: 创建数据库表

1. 在 Supabase 仪表板中，点击左侧菜单的 "SQL Editor"
2. 点击 "New query"
3. 复制 `DATABASE_SCHEMA.md` 文件中的 SQL 代码
4. 粘贴到 SQL 编辑器中
5. 点击 "Run" 执行 SQL

这将创建以下表：

- `user_profiles` - 用户资料
- `lesson_progress` - 学习进度
- `chat_history` - 聊天历史
- `user_preferences` - 用户偏好

## 步骤 5: 启用邮箱认证

1. 在 Supabase 仪表板中，点击 "Authentication" → "Providers"
2. 确保 "Email" 提供商已启用
3. （可选）配置邮件模板：
   - 点击 "Email Templates"
   - 自定义确认邮件、密码重置邮件等

## 步骤 6: 测试集成

1. 启动开发服务器：

   ```bash
   npm run dev
   ```

2. 访问登录页面并尝试注册新账户

3. 检查 Supabase 仪表板：
   - "Authentication" → "Users" 应该显示新用户
   - "Table Editor" → "user_profiles" 应该有新记录

## 常见问题

### Q: 注册后没有收到确认邮件？

A: 在开发环境中，Supabase 会自动确认用户。在生产环境中，您需要配置 SMTP 设置。

### Q: 数据没有保存到数据库？

A: 检查浏览器控制台是否有错误。确保：

- 环境变量正确设置
- 数据库表已创建
- Row Level Security (RLS) 策略已正确配置

### Q: 如何查看数据库中的数据？

A: 在 Supabase 仪表板中：

1. 点击 "Table Editor"
2. 选择要查看的表
3. 查看数据行

## 下一步

- 配置社交登录（Google, GitHub 等）
- 自定义邮件模板
- 设置生产环境的环境变量
- 配置数据库备份

## 需要帮助？

- [Supabase 文档](https://supabase.com/docs)
- [Supabase Discord](https://discord.supabase.com)
