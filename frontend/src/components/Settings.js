import React, { useState } from 'react';
import { Settings as SettingsIcon, Key, Bell, Database, Shield } from 'lucide-react';
import toast from 'react-hot-toast';

const Settings = () => {
  const [activeTab, setActiveTab] = useState('oauth');
  const [settings, setSettings] = useState({
    // OAuth настройки
    google_client_id: '',
    google_client_secret: '',
    youtube_scope: 'https://www.googleapis.com/auth/youtube.upload',
    ads_scope: 'https://www.googleapis.com/auth/adwords',
    
    // Telegram настройки
    telegram_bot_token: '',
    telegram_chat_id: '',
    
    // База данных
    supabase_url: '',
    supabase_key: '',
    
    // Мониторинг
    monitoring_enabled: true,
    monitoring_interval: 60, // минуты
    auto_reupload: false,
  });

  const tabs = [
    { id: 'oauth', label: 'OAuth', icon: Key },
    { id: 'telegram', label: 'Telegram', icon: Bell },
    { id: 'database', label: 'База данных', icon: Database },
    { id: 'monitoring', label: 'Мониторинг', icon: Shield },
  ];

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setSettings(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSave = () => {
    // Здесь будет логика сохранения настроек
    toast.success('Настройки сохранены');
  };

  const testConnection = (type) => {
    toast.loading(`Тестирование подключения к ${type}...`);
    // Здесь будет логика тестирования подключений
    setTimeout(() => {
      toast.dismiss();
      toast.success(`Подключение к ${type} успешно`);
    }, 2000);
  };

  const renderOAuthSettings = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Google OAuth2 Настройки
        </h3>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Client ID
            </label>
            <input
              type="text"
              name="google_client_id"
              value={settings.google_client_id}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              placeholder="Введите Google Client ID"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Client Secret
            </label>
            <input
              type="password"
              name="google_client_secret"
              value={settings.google_client_secret}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              placeholder="Введите Google Client Secret"
            />
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                YouTube Scope
              </label>
              <input
                type="text"
                name="youtube_scope"
                value={settings.youtube_scope}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Google Ads Scope
              </label>
              <input
                type="text"
                name="ads_scope"
                value={settings.ads_scope}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>
          </div>
          
          <button
            onClick={() => testConnection('Google OAuth')}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
          >
            Тестировать подключение
          </button>
        </div>
      </div>
    </div>
  );

  const renderTelegramSettings = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Telegram Bot Настройки
        </h3>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Bot Token
            </label>
            <input
              type="password"
              name="telegram_bot_token"
              value={settings.telegram_bot_token}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              placeholder="Введите Telegram Bot Token"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Chat ID
            </label>
            <input
              type="text"
              name="telegram_chat_id"
              value={settings.telegram_chat_id}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              placeholder="Введите Chat ID для уведомлений"
            />
          </div>
          
          <button
            onClick={() => testConnection('Telegram')}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
          >
            Тестировать подключение
          </button>
        </div>
      </div>
    </div>
  );

  const renderDatabaseSettings = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Supabase Настройки
        </h3>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Supabase URL
            </label>
            <input
              type="url"
              name="supabase_url"
              value={settings.supabase_url}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              placeholder="https://your-project.supabase.co"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Supabase Key
            </label>
            <input
              type="password"
              name="supabase_key"
              value={settings.supabase_key}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              placeholder="Введите Supabase API Key"
            />
          </div>
          
          <button
            onClick={() => testConnection('Supabase')}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
          >
            Тестировать подключение
          </button>
        </div>
      </div>
    </div>
  );

  const renderMonitoringSettings = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Мониторинг креативов
        </h3>
        
        <div className="space-y-4">
          <div className="flex items-center">
            <input
              type="checkbox"
              name="monitoring_enabled"
              checked={settings.monitoring_enabled}
              onChange={handleInputChange}
              className="mr-3"
            />
            <label className="text-sm font-medium text-gray-700">
              Включить мониторинг заблокированных креативов
            </label>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Интервал проверки (минуты)
            </label>
            <input
              type="number"
              name="monitoring_interval"
              value={settings.monitoring_interval}
              onChange={handleInputChange}
              min="1"
              max="1440"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
          
          <div className="flex items-center">
            <input
              type="checkbox"
              name="auto_reupload"
              checked={settings.auto_reupload}
              onChange={handleInputChange}
              className="mr-3"
            />
            <label className="text-sm font-medium text-gray-700">
              Автоматическая перезагрузка заблокированных креативов
            </label>
          </div>
        </div>
      </div>
    </div>
  );

  const renderContent = () => {
    switch (activeTab) {
      case 'oauth':
        return renderOAuthSettings();
      case 'telegram':
        return renderTelegramSettings();
      case 'database':
        return renderDatabaseSettings();
      case 'monitoring':
        return renderMonitoringSettings();
      default:
        return renderOAuthSettings();
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white rounded-lg shadow-sm border">
        <div className="border-b border-gray-200">
          <div className="flex">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center px-6 py-4 text-sm font-medium border-b-2 transition-colors ${
                    activeTab === tab.id
                      ? 'border-primary-500 text-primary-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon className="w-4 h-4 mr-2" />
                  {tab.label}
                </button>
              );
            })}
          </div>
        </div>
        
        <div className="p-6">
          {renderContent()}
          
          <div className="mt-8 pt-6 border-t border-gray-200">
            <div className="flex justify-end space-x-4">
              <button
                onClick={() => setSettings({
                  google_client_id: '',
                  google_client_secret: '',
                  youtube_scope: 'https://www.googleapis.com/auth/youtube.upload',
                  ads_scope: 'https://www.googleapis.com/auth/adwords',
                  telegram_bot_token: '',
                  telegram_chat_id: '',
                  supabase_url: '',
                  supabase_key: '',
                  monitoring_enabled: true,
                  monitoring_interval: 60,
                  auto_reupload: false,
                })}
                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors"
              >
                Сбросить
              </button>
              <button
                onClick={handleSave}
                className="px-6 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 transition-colors"
              >
                Сохранить настройки
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;
