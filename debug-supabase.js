// 在浏览器控制台运行这个脚本来检查环境变量配置

console.log('==== Supabase 配置检查 ====')

// 检查环境变量
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseKey = import.meta.env.VITE_SUPABASE_ANON_KEY
const deepseekKey = import.meta.env.VITE_DEEPSEEK_API_KEY

console.log('1. 环境变量检查：')
console.log('   VITE_SUPABASE_URL:', supabaseUrl ? '✅ 已设置' : '❌ 未设置')
console.log('   VITE_SUPABASE_ANON_KEY:', supabaseKey ? '✅ 已设置' : '❌ 未设置')
console.log('   VITE_DEEPSEEK_API_KEY:', deepseekKey ? '✅ 已设置' : '❌ 未设置')

if (!supabaseUrl || !supabaseKey) {
  console.error('❌ Supabase 环境变量未正确设置！')
  console.log('请检查 .env 文件是否包含正确的值，并重启开发服务器。')
} else {
  console.log('✅ 环境变量看起来正常')
  console.log('   Supabase URL:', supabaseUrl)
  console.log('   Anon Key 前10个字符:', supabaseKey.substring(0, 10) + '...')
}

// 测试 Supabase 连接
import { supabase } from './src/services/supabase'

console.log('\n2. 测试 Supabase 连接：')
supabase.auth.getSession().then(({ data, error }) => {
  if (error) {
    console.error('❌ Supabase 连接失败:', error.message)
  } else {
    console.log('✅ Supabase 连接成功')
    if (data.session) {
      console.log('   当前已登录用户:', data.session.user.email)
    } else {
      console.log('   当前未登录')
    }
  }
})

// 测试数据库表
console.log('\n3. 测试数据库表（需要登录）：')
supabase
  .from('user_profiles')
  .select('count')
  .then(({ data, error }) => {
    if (error) {
      console.error('❌ 数据库表不存在或无权限:', error.message)
      console.log('   请在 Supabase 仪表板运行 DATABASE_SCHEMA.md 中的 SQL')
    } else {
      console.log('✅ 数据库表存在且可访问')
    }
  })

console.log('\n==== 检查完成 ====')
console.log('如果看到错误，请按照提示修复。')
