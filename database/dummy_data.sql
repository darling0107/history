-- HistoriaQuest Dummy Data for Demo
-- Note: These INSERT statements require valid user IDs from auth.users

-- Example: Insert dummy lesson progress (replace 'your-user-uuid' with actual user ID)
-- INSERT INTO public.lesson_progress (user_id, lesson_id, completed, score, completed_at)
-- VALUES
--     ('your-user-uuid', 'lesson-1', true, 85, NOW()),
--     ('your-user-uuid', 'lesson-2', true, 92, NOW()),
--     ('your-user-uuid', 'lesson-3', false, NULL, NULL);

-- Example: Insert dummy chat history
-- INSERT INTO public.chat_history (user_id, figure_id, messages)
-- VALUES
--     ('your-user-uuid', 'confucius', '[{"role": "user", "content": "你好，孔子先生"}, {"role": "assistant", "content": "学而时习之，不亦说乎？"}]'),
--     ('your-user-uuid', 'laozi', '[{"role": "user", "content": "请问道是什么？"}, {"role": "assistant", "content": "道可道，非常道。"}]');

-- Example: Insert dummy user preferences
-- INSERT INTO public.user_preferences (user_id, preferences)
-- VALUES
--     ('your-user-uuid', '{"theme": "dark", "language": "zh-CN", "notifications": true}');
