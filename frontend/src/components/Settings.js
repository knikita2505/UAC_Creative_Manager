import React, { useState, useEffect } from 'react';
import { Settings as SettingsIcon, Key, Bell, Database, Shield, CheckCircle } from 'lucide-react';
import axios from 'axios';
import toast from 'react-hot-toast';

const Settings = () => {
  const [activeTab, setActiveTab] = useState('oauth');
  const [settings, setSettings] = useState({
    // YouTube настройки
    youtube_client_id: '',
    youtube_client_secret: '',
    youtube_redirect_uri: 'http://localhost:8000/auth/youtube/callback',
    
    // Google Drive настройки
    drive_client_id: '',
    drive_client_secret: '',
    drive_redirect_uri: 'http://localhost:8000/auth/drive/callback',
    
    // Google Ads настройки
    ads_client_id: '',
    ads_client_secret: '',
    ads_refresh_token: '',
    ads_developer_token: '',
    ads_customer_id: '',
    
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
  
  const [integrationsStatus, setIntegrationsStatus] = useState({});
  const [loading, setLoading] = useState({});

  const tabs = [
    { id: 'oauth', label: 'OAuth', icon: Key },
    { id: 'telegram', label: 'Telegram', icon: Bell },
    { id: 'database', label: 'База данных', icon: Database },
    { id: 'monitoring', label: 'Мониторинг', icon: Shield },
  ];

  // Загрузка статуса интеграций при монтировании
  useEffect(() => {
    fetchIntegrationsStatus();
    fetchIntegrationsSettings();
  }, []);

  const fetchIntegrationsSettings = async () => {
    try {
      const response = await axios.get('http://localhost:8000/integrations/settings');
      if (response.data.success) {
        const settingsData = response.data.settings;
        setSettings(prev => ({
          ...prev,
          // YouTube
          youtube_client_id: settingsData.youtube?.client_id || '',
          youtube_client_secret: settingsData.youtube?.client_secret || '',
          youtube_redirect_uri: settingsData.youtube?.redirect_uri || '',
          // Telegram
          telegram_bot_token: settingsData.telegram?.bot_token || '',
          telegram_chat_id: settingsData.telegram?.chat_id || '',
          // Google Drive
          drive_client_id: settingsData.google_drive?.client_id || '',
          drive_client_secret: settingsData.google_drive?.client_secret || '',
          drive_redirect_uri: settingsData.google_drive?.redirect_uri || '',
          // Google Ads
          ads_client_id: settingsData.google_ads?.client_id || '',
          ads_client_secret: settingsData.google_ads?.client_secret || '',
          ads_refresh_token: settingsData.google_ads?.refresh_token || '',
          ads_developer_token: settingsData.google_ads?.developer_token || '',
          ads_customer_id: settingsData.google_ads?.customer_id || ''
        }));
      }
    } catch (error) {
      console.error('Ошибка загрузки настроек:', error);
    }
  };

  const fetchIntegrationsStatus = async () => {
    try {
      const response = await axios.get('http://localhost:8000/integrations/status');
      setIntegrationsStatus(response.data.integrations);
    } catch (error) {
      console.error('Ошибка загрузки статуса интеграций:', error);
    }
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setSettings(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const setupYouTube = async () => {
    if (!settings.youtube_client_id || !settings.youtube_client_secret) {
      toast.error('Заполните все поля для YouTube');
      return;
    }

    setLoading(prev => ({ ...prev, youtube: true }));
    try {
      const response = await axios.post('http://localhost:8000/integrations/youtube/setup', {
        client_id: settings.youtube_client_id,
        client_secret: settings.youtube_client_secret,
        redirect_uri: settings.youtube_redirect_uri
      });

      if (response.data.success) {
        toast.success('YouTube настройки сохранены!');
        if (response.data.auth_url) {
          // Автоматически открываем ссылку авторизации в новом окне
          window.open(response.data.auth_url, 'youtube_auth', 'width=600,height=700,scrollbars=yes,resizable=yes');
          toast.success('Открыто окно авторизации YouTube');
        }
        fetchIntegrationsStatus();
      } else {
        toast.error('Ошибка настройки YouTube: ' + response.data.error);
      }
    } catch (error) {
      toast.error('Ошибка настройки YouTube: ' + error.message);
    } finally {
      setLoading(prev => ({ ...prev, youtube: false }));
    }
  };

  const testYouTube = async () => {
    setLoading(prev => ({ ...prev, youtube_test: true }));
    try {
      const response = await axios.post('http://localhost:8000/integrations/youtube/test');
      if (response.data.success) {
        toast.success('YouTube подключение успешно!');
      } else {
        toast.error('Ошибка YouTube: ' + response.data.error);
      }
    } catch (error) {
      toast.error('Ошибка тестирования YouTube: ' + error.message);
    } finally {
      setLoading(prev => ({ ...prev, youtube_test: false }));
    }
  };

  const setupTelegram = async () => {
    if (!settings.telegram_bot_token) {
      toast.error('Введите токен Telegram бота');
      return;
    }

    setLoading(prev => ({ ...prev, telegram: true }));
    try {
      const response = await axios.post('http://localhost:8000/integrations/telegram/setup', {
        bot_token: settings.telegram_bot_token,
        chat_id: settings.telegram_chat_id
      });

      if (response.data.success) {
        toast.success('Telegram Bot настроен успешно!');
        fetchIntegrationsStatus();
      } else {
        toast.error('Ошибка настройки Telegram: ' + response.data.error);
      }
    } catch (error) {
      toast.error('Ошибка настройки Telegram: ' + error.message);
    } finally {
      setLoading(prev => ({ ...prev, telegram: false }));
    }
  };

  const testTelegram = async () => {
    setLoading(prev => ({ ...prev, telegram_test: true }));
    try {
      const response = await axios.post('http://localhost:8000/integrations/telegram/test');
      if (response.data.success) {
        toast.success('Telegram подключение успешно!');
      } else {
        toast.error('Ошибка Telegram: ' + response.data.error);
      }
    } catch (error) {
      toast.error('Ошибка тестирования Telegram: ' + error.message);
    } finally {
      setLoading(prev => ({ ...prev, telegram_test: false }));
    }
  };

  const setupGoogleDrive = async () => {
    if (!settings.drive_client_id || !settings.drive_client_secret) {
      toast.error('Заполните все поля для Google Drive');
      return;
    }

    setLoading(prev => ({ ...prev, drive: true }));
    try {
      const response = await axios.post('http://localhost:8000/integrations/google-drive/setup', {
        client_id: settings.drive_client_id,
        client_secret: settings.drive_client_secret,
        redirect_uri: settings.drive_redirect_uri
      });

      if (response.data.success) {
        toast.success('Google Drive настройки сохранены!');
        if (response.data.auth_url) {
          toast('Перейдите по ссылке для авторизации: ' + response.data.auth_url);
        }
        fetchIntegrationsStatus();
      } else {
        toast.error('Ошибка настройки Google Drive: ' + response.data.error);
      }
    } catch (error) {
      toast.error('Ошибка настройки Google Drive: ' + error.message);
    } finally {
      setLoading(prev => ({ ...prev, drive: false }));
    }
  };

  const testGoogleDrive = async () => {
    setLoading(prev => ({ ...prev, drive_test: true }));
    try {
      const response = await axios.post('http://localhost:8000/integrations/google-drive/test');
      if (response.data.success) {
        toast.success('Google Drive подключение успешно!');
      } else {
        toast.error('Ошибка Google Drive: ' + response.data.error);
      }
    } catch (error) {
      toast.error('Ошибка тестирования Google Drive: ' + error.message);
    } finally {
      setLoading(prev => ({ ...prev, drive_test: false }));
    }
  };

  const setupGoogleAds = async () => {
    if (!settings.ads_client_id || !settings.ads_client_secret || !settings.ads_refresh_token || !settings.ads_developer_token || !settings.ads_customer_id) {
      toast.error('Заполните все поля для Google Ads');
      return;
    }

    setLoading(prev => ({ ...prev, ads: true }));
    try {
      const response = await axios.post('http://localhost:8000/integrations/google-ads/setup', {
        client_id: settings.ads_client_id,
        client_secret: settings.ads_client_secret,
        refresh_token: settings.ads_refresh_token,
        developer_token: settings.ads_developer_token,
        customer_id: settings.ads_customer_id
      });

      if (response.data.success) {
        toast.success('Google Ads настройки сохранены!');
        fetchIntegrationsStatus();
      } else {
        toast.error('Ошибка настройки Google Ads: ' + response.data.error);
      }
    } catch (error) {
      toast.error('Ошибка настройки Google Ads: ' + error.message);
    } finally {
      setLoading(prev => ({ ...prev, ads: false }));
    }
  };

  const testGoogleAds = async () => {
    setLoading(prev => ({ ...prev, ads_test: true }));
    try {
      const response = await axios.post('http://localhost:8000/integrations/google-ads/test');
      if (response.data.success) {
        toast.success('Google Ads подключение успешно!');
      } else {
        toast.error('Ошибка Google Ads: ' + response.data.error);
      }
    } catch (error) {
      toast.error('Ошибка тестирования Google Ads: ' + error.message);
    } finally {
      setLoading(prev => ({ ...prev, ads_test: false }));
    }
  };

  const testSupabase = async () => {
    try {
      const response = await axios.get('http://localhost:8000/');
      if (response.status === 200) {
        toast.success('Supabase подключение успешно!');
      }
    } catch (error) {
      toast.error('Ошибка тестирования Supabase: ' + error.message);
    }
  };

  const renderOAuthSettings = () => (
    <div className="space-y-8">
      {/* YouTube */}
      <div className="border border-gray-200 rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">YouTube API</h3>
          <div className="flex items-center space-x-2">
            {integrationsStatus.youtube?.configured && (
              <CheckCircle className="w-5 h-5 text-green-500" />
            )}
            {integrationsStatus.youtube?.authorized && (
              <CheckCircle className="w-5 h-5 text-blue-500" />
            )}
          </div>
        </div>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Client ID
            </label>
            <input
              type="text"
              name="youtube_client_id"
              value={settings.youtube_client_id}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              placeholder="Введите YouTube Client ID"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Client Secret
            </label>
            <input
              type="password"
              name="youtube_client_secret"
              value={settings.youtube_client_secret}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              placeholder="Введите YouTube Client Secret"
            />
          </div>
          
          <div className="flex space-x-3">
            <button
              onClick={setupYouTube}
              disabled={loading.youtube}
              className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors disabled:opacity-50"
            >
              {loading.youtube ? 'Сохранение...' : 'Сохранить'}
            </button>
            <button
              onClick={testYouTube}
              disabled={loading.youtube_test}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50"
            >
              {loading.youtube_test ? 'Тестирование...' : 'Тестировать'}
            </button>
          </div>
        </div>
      </div>

      {/* Google Drive */}
      <div className="border border-gray-200 rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Google Drive API</h3>
          <div className="flex items-center space-x-2">
            {integrationsStatus.google_drive?.configured && (
              <CheckCircle className="w-5 h-5 text-green-500" />
            )}
            {integrationsStatus.google_drive?.authorized && (
              <CheckCircle className="w-5 h-5 text-blue-500" />
            )}
          </div>
        </div>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Client ID
            </label>
            <input
              type="text"
              name="drive_client_id"
              value={settings.drive_client_id}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              placeholder="Введите Google Drive Client ID"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Client Secret
            </label>
            <input
              type="password"
              name="drive_client_secret"
              value={settings.drive_client_secret}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              placeholder="Введите Google Drive Client Secret"
            />
          </div>
          
          <div className="flex space-x-3">
            <button
              onClick={setupGoogleDrive}
              disabled={loading.drive}
              className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors disabled:opacity-50"
            >
              {loading.drive ? 'Сохранение...' : 'Сохранить'}
            </button>
            <button
              onClick={testGoogleDrive}
              disabled={loading.drive_test}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50"
            >
              {loading.drive_test ? 'Тестирование...' : 'Тестировать'}
            </button>
          </div>
        </div>
      </div>

      {/* Google Ads */}
      <div className="border border-gray-200 rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Google Ads API</h3>
          <div className="flex items-center space-x-2">
            {integrationsStatus.google_ads?.configured && (
              <CheckCircle className="w-5 h-5 text-green-500" />
            )}
            {integrationsStatus.google_ads?.authorized && (
              <CheckCircle className="w-5 h-5 text-blue-500" />
            )}
          </div>
        </div>
        
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Client ID
              </label>
              <input
                type="text"
                name="ads_client_id"
                value={settings.ads_client_id}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                placeholder="Google Ads Client ID"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Client Secret
              </label>
              <input
                type="password"
                name="ads_client_secret"
                value={settings.ads_client_secret}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                placeholder="Google Ads Client Secret"
              />
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Refresh Token
            </label>
            <input
              type="text"
              name="ads_refresh_token"
              value={settings.ads_refresh_token}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              placeholder="Refresh Token"
            />
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Developer Token
              </label>
              <input
                type="text"
                name="ads_developer_token"
                value={settings.ads_developer_token}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                placeholder="Developer Token"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Customer ID
              </label>
              <input
                type="text"
                name="ads_customer_id"
                value={settings.ads_customer_id}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                placeholder="Customer ID"
              />
            </div>
          </div>
          
          <div className="flex space-x-3">
            <button
              onClick={setupGoogleAds}
              disabled={loading.ads}
              className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors disabled:opacity-50"
            >
              {loading.ads ? 'Сохранение...' : 'Сохранить'}
            </button>
            <button
              onClick={testGoogleAds}
              disabled={loading.ads_test}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50"
            >
              {loading.ads_test ? 'Тестирование...' : 'Тестировать'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  const renderTelegramSettings = () => (
    <div className="space-y-6">
      <div className="border border-gray-200 rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Telegram Bot</h3>
          <div className="flex items-center space-x-2">
            {integrationsStatus.telegram?.configured && (
              <CheckCircle className="w-5 h-5 text-green-500" />
            )}
          </div>
        </div>
        
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
            <p className="text-sm text-gray-500 mt-1">
              Получите токен у <a href="https://t.me/BotFather" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">@BotFather</a>
            </p>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Chat ID (опционально)
            </label>
            <input
              type="text"
              name="telegram_chat_id"
              value={settings.telegram_chat_id}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              placeholder="Введите Chat ID для уведомлений"
            />
            <p className="text-sm text-gray-500 mt-1">
              Chat ID для отправки уведомлений (можно оставить пустым)
            </p>
          </div>
          
          <div className="flex space-x-3">
            <button
              onClick={setupTelegram}
              disabled={loading.telegram}
              className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors disabled:opacity-50"
            >
              {loading.telegram ? 'Сохранение...' : 'Сохранить'}
            </button>
            <button
              onClick={testTelegram}
              disabled={loading.telegram_test}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50"
            >
              {loading.telegram_test ? 'Тестирование...' : 'Тестировать'}
            </button>
          </div>
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
            onClick={testSupabase}
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
                onClick={() => toast.success('Настройки сохранены!')}
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
