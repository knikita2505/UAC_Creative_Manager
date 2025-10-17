import React, { useState, useEffect } from 'react';
import { FileText, ExternalLink, Calendar, Filter, Download } from 'lucide-react';
import axios from 'axios';
import toast from 'react-hot-toast';

const Registry = () => {
  const [uploads, setUploads] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [uploadsResponse, templatesResponse] = await Promise.all([
        axios.get('http://localhost:8000/uploads'),
        axios.get('http://localhost:8000/templates')
      ]);
      
      setUploads(uploadsResponse.data.uploads);
      setTemplates(templatesResponse.data.templates);
    } catch (error) {
      console.error('Ошибка загрузки данных:', error);
      toast.error('Ошибка загрузки реестра');
    } finally {
      setLoading(false);
    }
  };

  const filteredUploads = uploads.filter(upload => {
    const matchesStatus = filterStatus === 'all' || upload.status === filterStatus;
    const matchesSearch = upload.campaign_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         upload.youtube_url.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesStatus && matchesSearch;
  });

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      active: { color: 'bg-green-100 text-green-800', label: 'Активен' },
      banned: { color: 'bg-red-100 text-red-800', label: 'Заблокирован' },
      limited: { color: 'bg-yellow-100 text-yellow-800', label: 'Ограничен' }
    };
    
    const config = statusConfig[status] || { color: 'bg-gray-100 text-gray-800', label: status };
    
    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${config.color}`}>
        {config.label}
      </span>
    );
  };

  const exportData = () => {
    const csvContent = [
      ['ID', 'Название кампании', 'YouTube URL', 'Статус', 'Дата загрузки', 'Ad Group', 'Метрики'],
      ...filteredUploads.map(upload => [
        upload.id,
        upload.campaign_name,
        upload.youtube_url,
        upload.status,
        formatDate(upload.upload_date),
        upload.ad_group || '',
        upload.metrics ? JSON.stringify(upload.metrics) : ''
      ])
    ].map(row => row.join(',')).join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `creative_registry_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    toast.success('Данные экспортированы в CSV');
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto">
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
            <div className="space-y-4">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="h-16 bg-gray-200 rounded"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto">
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-900">
            Реестр креативов
          </h2>
          <button
            onClick={exportData}
            className="flex items-center px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 transition-colors"
          >
            <Download className="w-4 h-4 mr-2" />
            Экспорт CSV
          </button>
        </div>

        {/* Фильтры и поиск */}
        <div className="flex flex-col sm:flex-row gap-4 mb-6">
          <div className="flex-1">
            <input
              type="text"
              placeholder="Поиск по названию кампании или YouTube URL..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
          <div className="flex items-center space-x-2">
            <Filter className="w-4 h-4 text-gray-500" />
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            >
              <option value="all">Все статусы</option>
              <option value="active">Активные</option>
              <option value="banned">Заблокированные</option>
              <option value="limited">Ограниченные</option>
            </select>
          </div>
        </div>

        {/* Статистика */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-blue-50 p-4 rounded-lg">
            <div className="text-2xl font-bold text-blue-600">{uploads.length}</div>
            <div className="text-sm text-blue-800">Всего загрузок</div>
          </div>
          <div className="bg-green-50 p-4 rounded-lg">
            <div className="text-2xl font-bold text-green-600">
              {uploads.filter(u => u.status === 'active').length}
            </div>
            <div className="text-sm text-green-800">Активных</div>
          </div>
          <div className="bg-red-50 p-4 rounded-lg">
            <div className="text-2xl font-bold text-red-600">
              {uploads.filter(u => u.status === 'banned').length}
            </div>
            <div className="text-sm text-red-800">Заблокированных</div>
          </div>
          <div className="bg-yellow-50 p-4 rounded-lg">
            <div className="text-2xl font-bold text-yellow-600">
              {uploads.filter(u => u.status === 'limited').length}
            </div>
            <div className="text-sm text-yellow-800">Ограниченных</div>
          </div>
        </div>

        {/* Таблица загрузок */}
        {filteredUploads.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <FileText className="w-16 h-16 mx-auto mb-4 text-gray-300" />
            <p className="text-lg font-medium">Загрузки не найдены</p>
            <p className="text-sm">
              {searchTerm || filterStatus !== 'all' 
                ? 'Попробуйте изменить фильтры поиска'
                : 'Загрузите первое видео в разделе "Загрузка видео"'
              }
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Кампания
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    YouTube URL
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Статус
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Дата загрузки
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Ad Group
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Действия
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredUploads.map((upload) => (
                  <tr key={upload.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">
                        {upload.campaign_name}
                      </div>
                      <div className="text-sm text-gray-500">
                        ID: {upload.id}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <a
                        href={upload.youtube_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center text-sm text-primary-600 hover:text-primary-800"
                      >
                        <ExternalLink className="w-4 h-4 mr-1" />
                        Открыть на YouTube
                      </a>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {getStatusBadge(upload.status)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <div className="flex items-center">
                        <Calendar className="w-4 h-4 mr-1" />
                        {formatDate(upload.upload_date)}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {upload.ad_group || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <button className="text-primary-600 hover:text-primary-800">
                        Подробнее
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Шаблоны */}
        {templates.length > 0 && (
          <div className="mt-8">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Шаблоны креативов ({templates.length})
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {templates.map((template) => (
                <div key={template.id} className="border border-gray-200 rounded-lg p-4">
                  <h4 className="font-medium text-gray-900 mb-2">
                    {template.style} - {template.language}
                  </h4>
                  <div className="text-sm text-gray-500 space-y-1">
                    <p>Фон: {template.background}</p>
                    <p>Агрессивность: {template.aggressiveness}</p>
                    <p>Категория: {template.category}</p>
                    {template.characteristics.length > 0 && (
                      <p>Характеристики: {template.characteristics.join(', ')}</p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Registry;
