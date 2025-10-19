-- Инициализация данных для UAC Creative Manager

-- ==================== РОЛИ ПО УМОЛЧАНИЮ ====================
INSERT INTO roles (id, name, description) VALUES
    ('550e8400-e29b-41d4-a716-446655440001', 'admin', 'Администратор системы'),
    ('550e8400-e29b-41d4-a716-446655440002', 'user', 'Обычный пользователь'),
    ('550e8400-e29b-41d4-a716-446655440003', 'viewer', 'Только просмотр')
ON CONFLICT (name) DO NOTHING;

-- ==================== ТЕСТОВЫЙ ПОЛЬЗОВАТЕЛЬ ====================
INSERT INTO users (id, email, role_id) VALUES
    ('550e8400-e29b-41d4-a716-446655440010', 'admin@example.com', '550e8400-e29b-41d4-a716-446655440001')
ON CONFLICT (email) DO NOTHING;

-- ==================== ТЕСТОВЫЕ ШАБЛОНЫ ====================
INSERT INTO templates (id, language, style, orientation, background, ai_tag, ai_text, ai_hardness, characteristics) VALUES
    ('550e8400-e29b-41d4-a716-446655440020', 'ru', 'modern', 'vertical', 'dark', 'modal', 'Скачай игру прямо сейчас!', 3, '["яркие цвета", "крупный текст", "призыв к действию"]'),
    ('550e8400-e29b-41d4-a716-446655440021', 'en', 'classic', 'horizontal', 'light', 'virus', 'Best mobile game 2024!', 2, '["минимализм", "чистый дизайн", "профессиональный"]'),
    ('550e8400-e29b-41d4-a716-446655440022', 'ru', 'aggressive', 'vertical', 'red', 'subtitles', 'НЕ УПУСТИ ШАНС!', 5, '["агрессивный", "яркие цвета", "много текста"]')
ON CONFLICT (id) DO NOTHING;

-- ==================== ТЕСТОВЫЕ МОДАЛКИ ====================
INSERT INTO modal_images (id, filename, file_path, file_size, is_active) VALUES
    ('550e8400-e29b-41d4-a716-446655440030', 'soft_modal_1.png', 'uploads/modals/soft_modal_1.png', 45678, true),
    ('550e8400-e29b-41d4-a716-446655440031', 'soft_modal_2.png', 'uploads/modals/soft_modal_2.png', 52341, true),
    ('550e8400-e29b-41d4-a716-446655440032', 'soft_modal_3.png', 'uploads/modals/soft_modal_3.png', 38912, false)
ON CONFLICT (id) DO NOTHING;

-- ==================== ТЕСТОВЫЕ ЗАГРУЗКИ ====================
INSERT INTO uploads (id, template_id, youtube_url, video_title, campaign_name, thumbnail_type, thumbnail_image_id, status, performance) VALUES
    ('550e8400-e29b-41d4-a716-446655440040', '550e8400-e29b-41d4-a716-446655440020', 'https://youtube.com/watch?v=test1', 'Мобильная игра 15-12-24', 'Мобильная игра', 'soft_modal', '550e8400-e29b-41d4-a716-446655440030', 'active', '{"views": 1250, "ctr": 0.035, "spend": 45.50}'),
    ('550e8400-e29b-41d4-a716-446655440041', '550e8400-e29b-41d4-a716-446655440021', 'https://youtube.com/watch?v=test2', 'Best Game 15-12-24', 'Best Game', 'first_frame', null, 'active', '{"views": 890, "ctr": 0.028, "spend": 32.75}'),
    ('550e8400-e29b-41d4-a716-446655440042', '550e8400-e29b-41d4-a716-446655440022', 'https://youtube.com/watch?v=test3', 'Агрессивная игра 15-12-24', 'Агрессивная игра', 'none', null, 'banned', '{"views": 2100, "ctr": 0.045, "spend": 67.80}')
ON CONFLICT (id) DO NOTHING;
