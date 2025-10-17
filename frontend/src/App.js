import React, { useState } from 'react';
import { Upload, FileText, Settings as SettingsIcon, BarChart3 } from 'lucide-react';
import VideoUpload from './components/VideoUpload';
import Registry from './components/Registry';
import ModalManager from './components/ModalManager';
import Settings from './components/Settings';
import './index.css';

function App() {
  const [activeTab, setActiveTab] = useState('upload');

  const tabs = [
    { id: 'upload', label: 'Загрузка видео', icon: Upload },
    { id: 'registry', label: 'Реестр креативов', icon: FileText },
    { id: 'modals', label: 'Модалки', icon: SettingsIcon },
    { id: 'settings', label: 'Настройки', icon: BarChart3 },
  ];

  const renderContent = () => {
    switch (activeTab) {
      case 'upload':
        return <VideoUpload />;
      case 'registry':
        return <Registry />;
      case 'modals':
        return <ModalManager />;
      case 'settings':
        return <Settings />;
      default:
        return <VideoUpload />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">
                🎯 UAC Creative Manager
              </h1>
            </div>
            <div className="flex space-x-1">
              {tabs.map((tab) => {
                const Icon = tab.icon;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`flex items-center px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                      activeTab === tab.id
                        ? 'bg-primary-100 text-primary-700'
                        : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                    }`}
                  >
                    <Icon className="w-4 h-4 mr-2" />
                    {tab.label}
                  </button>
                );
              })}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {renderContent()}
      </main>
    </div>
  );
}

export default App;
