-- Создание таблиц для UAC Creative Manager

-- ==================== ROLES ====================
CREATE TABLE IF NOT EXISTS roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ==================== USERS ====================
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT NOT NULL UNIQUE,
    role_id UUID REFERENCES roles(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ==================== OAUTH CREDENTIALS ====================
CREATE TABLE IF NOT EXISTS oauth_credentials (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    service TEXT NOT NULL, -- youtube, google_ads, telegram
    credentials JSONB NOT NULL, -- client_id, client_secret, tokens, etc.
    user_id UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ==================== MODAL IMAGES ====================
CREATE TABLE IF NOT EXISTS modal_images (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_size INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ==================== TEMPLATES ====================
CREATE TABLE IF NOT EXISTS templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    language TEXT, -- en, ru, etc.
    style TEXT, -- classic, modern, etc.
    orientation TEXT, -- vertical, horizontal
    background TEXT, -- цветовая схема
    ai_tag TEXT, -- modal, virus, subtitles
    ai_text TEXT, -- распознанный текст
    ai_hardness INTEGER CHECK (ai_hardness >= 1 AND ai_hardness <= 5), -- агрессивность 1-5
    characteristics JSONB, -- дополнительные характеристики
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ==================== UPLOADS ====================
CREATE TABLE IF NOT EXISTS uploads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_id UUID REFERENCES templates(id),
    youtube_url TEXT NOT NULL,
    video_title TEXT NOT NULL,
    campaign_name TEXT NOT NULL,
    thumbnail_type TEXT NOT NULL CHECK (thumbnail_type IN ('none', 'first_frame', 'soft_modal')),
    thumbnail_image_id UUID REFERENCES modal_images(id),
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'banned', 'pending', 'error', 'limited')),
    performance JSONB, -- метрики GAds: spend, ctr, etc.
    upload_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ==================== LOGS ====================
CREATE TABLE IF NOT EXISTS logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    action TEXT NOT NULL,
    metadata JSONB,
    user_id UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ==================== ИНДЕКСЫ ====================

-- Индексы для быстрого поиска
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_oauth_service ON oauth_credentials(service);
CREATE INDEX IF NOT EXISTS idx_uploads_status ON uploads(status);
CREATE INDEX IF NOT EXISTS idx_uploads_campaign ON uploads(campaign_name);
CREATE INDEX IF NOT EXISTS idx_uploads_date ON uploads(upload_date);
CREATE INDEX IF NOT EXISTS idx_logs_action ON logs(action);
CREATE INDEX IF NOT EXISTS idx_logs_date ON logs(created_at);

-- ==================== RLS (Row Level Security) ====================

-- Включаем RLS для всех таблиц
ALTER TABLE roles ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE oauth_credentials ENABLE ROW LEVEL SECURITY;
ALTER TABLE modal_images ENABLE ROW LEVEL SECURITY;
ALTER TABLE templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE uploads ENABLE ROW LEVEL SECURITY;
ALTER TABLE logs ENABLE ROW LEVEL SECURITY;

-- Политики доступа (пока разрешаем все для сервисного ключа)
CREATE POLICY "Allow all operations for service role" ON roles FOR ALL USING (true);
CREATE POLICY "Allow all operations for service role" ON users FOR ALL USING (true);
CREATE POLICY "Allow all operations for service role" ON oauth_credentials FOR ALL USING (true);
CREATE POLICY "Allow all operations for service role" ON modal_images FOR ALL USING (true);
CREATE POLICY "Allow all operations for service role" ON templates FOR ALL USING (true);
CREATE POLICY "Allow all operations for service role" ON uploads FOR ALL USING (true);
CREATE POLICY "Allow all operations for service role" ON logs FOR ALL USING (true);

-- ==================== ФУНКЦИИ ====================

-- Функция для обновления updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Триггеры для автоматического обновления updated_at
CREATE TRIGGER update_oauth_credentials_updated_at 
    BEFORE UPDATE ON oauth_credentials 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_uploads_updated_at 
    BEFORE UPDATE ON uploads 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
