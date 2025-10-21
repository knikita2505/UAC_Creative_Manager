import React, { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, Link, Image, CheckCircle, AlertCircle, Copy, HelpCircle } from 'lucide-react';
import axios from 'axios';
import toast from 'react-hot-toast';

const VideoUpload = () => {
  const [formData, setFormData] = useState({
    campaign_name: '',
    video_source: 'local',
    drive_urls: '',
    thumbnail_option: 'none',
    modal_image_id: null,
    create_formats: false
  });
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);
  const [modalImages, setModalImages] = useState([]);
  const [selectedModal, setSelectedModal] = useState(null);

  // Загрузка списка модалок при монтировании компонента
  React.useEffect(() => {
    fetchModalImages();
  }, []);

  const fetchModalImages = async () => {
    try {
      const response = await axios.get('http://localhost:8000/modals');
      setModalImages(response.data.modals);
    } catch (error) {
      console.error('Ошибка загрузки модалок:', error);
    }
  };

  const onDrop = (acceptedFiles) => {
    const videoFiles = acceptedFiles.filter(file => file.type.startsWith('video/'));
    if (videoFiles.length > 0) {
      setUploadedFiles(videoFiles);
      toast.success(`Выбрано ${videoFiles.length} видео файлов`);
    } else {
      toast.error('Пожалуйста, выберите видео файлы');
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'video/*': ['.mp4', '.avi', '.mov', '.mkv', '.webm']
    },
    multiple: true
  });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.campaign_name.trim()) {
      toast.error('Введите название кампании');
      return;
    }

    if (formData.video_source === 'local' && uploadedFiles.length === 0) {
      toast.error('Выберите видео файлы');
      return;
    }

    if (formData.video_source === 'drive' && !formData.drive_urls.trim()) {
      toast.error('Введите ссылки на Google Drive (по одной на строку)');
      return;
    }

    if (formData.thumbnail_option === 'soft_modal' && !formData.modal_image_id) {
      toast.error('Выберите модалку для наложения');
      return;
    }

    setIsUploading(true);
    setUploadResult(null);

    try {
      const submitData = new FormData();
      submitData.append('campaign_name', formData.campaign_name);
      submitData.append('video_source', formData.video_source);
      submitData.append('thumbnail_option', formData.thumbnail_option);
      submitData.append('create_formats', formData.create_formats);
      
      if (formData.video_source === 'drive') {
        // Парсим ссылки и отправляем как JSON
        const urls = formData.drive_urls.split('\n').filter(url => url.trim());
        submitData.append('drive_urls', JSON.stringify(urls));
      }
      
      if (formData.thumbnail_option === 'soft_modal') {
        submitData.append('modal_image_id', formData.modal_image_id);
      }
      
      // Добавляем видео файлы
      if (uploadedFiles.length > 1) {
        // Пакетная загрузка
        uploadedFiles.forEach(file => {
          submitData.append('video_files', file);
        });
      } else if (uploadedFiles.length === 1) {
        // Одиночная загрузка
        submitData.append('video_file', uploadedFiles[0]);
      }

      const endpoint = uploadedFiles.length > 1 ? '/upload/videos/batch' : '/upload/video';
      const response = await axios.post(`http://localhost:8000${endpoint}`, submitData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.data.success) {
        setUploadResult(response.data);
        if (uploadedFiles.length > 1) {
          toast.success(`Успешно загружено ${response.data.successful_uploads} из ${response.data.total_videos} видео!`);
        } else {
          toast.success('Видео успешно загружено на YouTube!');
        }
        // Сброс формы
        setFormData({
          campaign_name: '',
          video_source: 'local',
          drive_urls: '',
          thumbnail_option: 'none',
          modal_image_id: null,
          create_formats: false
        });
        setUploadedFiles([]);
        setSelectedModal(null);
      } else {
        toast.error('Ошибка загрузки: ' + response.data.error);
      }
    } catch (error) {
      console.error('Ошибка загрузки:', error);
      toast.error('Ошибка загрузки видео');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">
          Загрузка видео на YouTube
        </h2>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Прилка */}
          <div>
            <label className="flex items-center text-sm font-medium text-gray-700 mb-2">
              <span>Прилка *</span>
              <div className="relative group ml-1">
                <HelpCircle className="w-4 h-4 text-gray-400 cursor-help" />
                <div className="absolute left-0 bottom-full mb-2 hidden group-hover:block w-64 p-2 bg-gray-900 text-white text-xs rounded shadow-lg z-10">
                  Название приложения, которое будет использоваться в названиях видео
                </div>
              </div>
            </label>
            <input
              type="text"
              name="campaign_name"
              value={formData.campaign_name}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              placeholder="Например: MasterSwiper"
              required
            />
          </div>

          {/* Источник видео */}
          <div>
            <label className="flex items-center text-sm font-medium text-gray-700 mb-3">
              <span>Источник видео *</span>
              <div className="relative group ml-1">
                <HelpCircle className="w-4 h-4 text-gray-400 cursor-help" />
                <div className="absolute left-0 bottom-full mb-2 hidden group-hover:block w-64 p-2 bg-gray-900 text-white text-xs rounded shadow-lg z-10">
                  Выберите откуда загружать видео: с вашего устройства или по ссылке из Google Drive
                </div>
              </div>
            </label>
            <div className="space-y-3">
              <label className="flex items-center">
                <input
                  type="radio"
                  name="video_source"
                  value="local"
                  checked={formData.video_source === 'local'}
                  onChange={handleInputChange}
                  className="mr-3"
                />
                <span>Локальный файл</span>
              </label>
              <label className="flex items-center">
                <input
                  type="radio"
                  name="video_source"
                  value="drive"
                  checked={formData.video_source === 'drive'}
                  onChange={handleInputChange}
                  className="mr-3"
                />
                <span>Ссылка на Google Drive</span>
              </label>
            </div>
          </div>

          {/* Загрузка файлов или ссылки на Drive */}
          {formData.video_source === 'local' ? (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Видео файлы * (можно выбрать несколько)
              </label>
              <div
                {...getRootProps()}
                className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors ${
                  isDragActive
                    ? 'border-primary-400 bg-primary-50'
                    : 'border-gray-300 hover:border-primary-400'
                }`}
              >
                <input {...getInputProps()} />
                <Upload className="w-8 h-8 mx-auto mb-2 text-gray-400" />
                {uploadedFiles.length > 0 ? (
                  <div className="text-green-600">
                    <CheckCircle className="w-6 h-6 mx-auto mb-2" />
                    <p className="font-medium">Выбрано {uploadedFiles.length} файлов</p>
                    <div className="mt-2 space-y-1">
                      {uploadedFiles.map((file, index) => (
                        <div key={index} className="text-sm text-gray-600">
                          {file.name} ({(file.size / (1024 * 1024)).toFixed(2)} MB)
                        </div>
                      ))}
                    </div>
                  </div>
                ) : (
                  <div>
                    <p className="text-gray-600">
                      {isDragActive
                        ? 'Отпустите файлы здесь'
                        : 'Перетащите видео файлы сюда или нажмите для выбора'}
                    </p>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Ссылки на Google Drive * (по одной на строку)
              </label>
              <textarea
                name="drive_urls"
                value={formData.drive_urls}
                onChange={handleInputChange}
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                placeholder="https://drive.google.com/file/d/...&#10;https://drive.google.com/file/d/...&#10;https://drive.google.com/file/d/..."
              />
            </div>
          )}

          {/* Создание других форматов */}
          <div className="border-t pt-4">
            <label className="flex items-start">
              <input
                type="checkbox"
                name="create_formats"
                checked={formData.create_formats}
                onChange={(e) => setFormData(prev => ({
                  ...prev,
                  create_formats: e.target.checked
                }))}
                className="mt-1 mr-3"
              />
              <div className="flex items-center">
                <span className="font-medium text-gray-900">Создать для видео недостающие форматы</span>
                <div className="relative group ml-1">
                  <HelpCircle className="w-4 h-4 text-gray-400 cursor-help" />
                  <div className="absolute left-0 bottom-full mb-2 hidden group-hover:block w-80 p-3 bg-gray-900 text-white text-xs rounded shadow-lg z-10">
                    <p className="mb-2">Система создаст видео в других ориентациях с черными полосами:</p>
                    <ul className="list-disc ml-4 space-y-1">
                      <li>Квадратное (1:1) → Горизонтальное (16:9) + Вертикальное (9:16)</li>
                      <li>Горизонтальное (16:9) → Квадратное (1:1) + Вертикальное (9:16)</li>
                      <li>Вертикальное (9:16) → Квадратное (1:1) + Горизонтальное (16:9)</li>
                    </ul>
                    <p className="mt-2 italic opacity-75">⚠️ Работает корректно только с квадратными видео!</p>
                  </div>
                </div>
              </div>
            </label>
          </div>

          {/* Кнопка загрузки */}
          <div className="flex justify-end">
            <button
              type="submit"
              disabled={isUploading}
              className={`px-6 py-2 rounded-md font-medium transition-colors ${
                isUploading
                  ? 'bg-gray-400 text-white cursor-not-allowed'
                  : 'bg-primary-600 text-white hover:bg-primary-700'
              }`}
            >
              {isUploading ? 'Загрузка...' : 'Загрузить на YouTube'}
            </button>
          </div>
        </form>

        {/* Результат загрузки */}
        {uploadResult && (
          <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg">
            <div className="flex items-center">
              <CheckCircle className="w-5 h-5 text-green-600 mr-2" />
              <h3 className="font-medium text-green-800">
                {uploadResult.total_videos > 1 
                  ? `Загрузка завершена! Успешно: ${uploadResult.successful_uploads} из ${uploadResult.total_videos}`
                  : 'Загрузка завершена успешно!'
                }
              </h3>
            </div>
            <div className="mt-2 text-sm text-green-700">
              {uploadResult.total_videos > 1 || uploadResult.results ? (
                <div>
                  <p><strong>Исходных видео:</strong> {uploadResult.total_videos}</p>
                  <p><strong>Успешно загружено групп:</strong> {uploadResult.successful_uploads}</p>
                  {uploadResult.total_formats && (
                    <p><strong>Всего форматов:</strong> {uploadResult.total_formats}</p>
                  )}
                  {uploadResult.failed_uploads > 0 && (
                    <p><strong>Ошибок:</strong> {uploadResult.failed_uploads}</p>
                  )}
                  
                  {/* Группировка по copy_number */}
                  <div className="mt-3 space-y-3">
                    {Object.entries(
                      uploadResult.results.filter(r => r.success).reduce((groups, result) => {
                        const groupKey = result.group_name || `Видео #${result.copy_number || 'unknown'}`;
                        if (!groups[groupKey]) groups[groupKey] = [];
                        groups[groupKey].push(result);
                        return groups;
                      }, {})
                    ).map(([groupName, videos]) => (
                      <details key={groupName} className="border rounded-lg" open={Object.keys(uploadResult.results.filter(r => r.success).reduce((g, v) => ({...g, [v.group_name || `Видео #${v.copy_number}`]: 1}), {})).length === 1}>
                        <summary className="cursor-pointer p-3 bg-primary-50 hover:bg-primary-100 rounded-t-lg font-medium flex items-center justify-between">
                          <span>{groupName}</span>
                          <span className="text-sm text-gray-600">({videos.length} формат{videos.length > 1 ? (videos.length > 4 ? 'ов' : 'а') : ''})</span>
                        </summary>
                        <div className="p-3 space-y-2">
                          {videos.map((result, index) => (
                            <div key={index} className="p-2 bg-green-50 rounded border border-green-200">
                              <div className="flex items-center justify-between">
                                <span className="font-medium text-sm">{result.video_title}</span>
                                <CheckCircle className="w-4 h-4 text-green-600" />
                              </div>
                              {result.orientation && (
                                <p className="text-xs text-gray-600 mt-1">Ориентация: {result.orientation}</p>
                              )}
                              <button
                                onClick={() => {
                                  navigator.clipboard.writeText(result.youtube_url);
                                  toast.success('Ссылка скопирована в буфер обмена');
                                }}
                                className="flex items-center text-primary-600 hover:text-primary-800 text-xs mt-1"
                              >
                                <Copy className="w-3 h-3 mr-1" />
                                Копировать ссылку
                              </button>
                            </div>
                          ))}
                        </div>
                      </details>
                    ))}
                  </div>
                  
                  {/* Ошибки */}
                  {uploadResult.results.filter(r => !r.success).length > 0 && (
                    <div className="mt-3">
                      <p className="font-medium text-red-600 mb-2">Ошибки:</p>
                      {uploadResult.results.filter(r => !r.success).map((result, index) => (
                        <div key={index} className="p-2 bg-red-100 rounded mb-2">
                          <div className="flex items-center justify-between">
                            <span className="font-medium">{result.video_title}</span>
                            <AlertCircle className="w-4 h-4 text-red-600" />
                          </div>
                          <p className="text-red-600 text-xs mt-1">Ошибка: {result.error}</p>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ) : uploadResult.videos ? (
                <div>
                  <p><strong>Всего загружено форматов:</strong> {uploadResult.total_uploaded}</p>
                  
                  {/* Группировка по copy_number */}
                  <div className="mt-3 space-y-3">
                    {Object.entries(
                      uploadResult.videos.reduce((groups, video) => {
                        const groupKey = video.group_name || `Group ${video.copy_number}`;
                        if (!groups[groupKey]) groups[groupKey] = [];
                        groups[groupKey].push(video);
                        return groups;
                      }, {})
                    ).map(([groupName, videos]) => (
                      <details key={groupName} className="border rounded-lg" open={Object.keys(uploadResult.videos.reduce((g, v) => ({...g, [v.group_name]: 1}), {})).length === 1}>
                        <summary className="cursor-pointer p-3 bg-primary-50 hover:bg-primary-100 rounded-t-lg font-medium flex items-center justify-between">
                          <span>{groupName}</span>
                          <span className="text-sm text-gray-600">({videos.length} формат{videos.length > 1 ? 'а' : ''})</span>
                        </summary>
                        <div className="p-3 space-y-2">
                          {videos.map((video, index) => (
                            <div key={index} className="p-2 bg-green-50 rounded border border-green-200">
                              <div className="flex items-center justify-between">
                                <span className="font-medium text-sm">{video.video_title}</span>
                                <CheckCircle className="w-4 h-4 text-green-600" />
                              </div>
                              <p className="text-xs text-gray-600 mt-1">Ориентация: {video.orientation}</p>
                              <button
                                onClick={() => {
                                  navigator.clipboard.writeText(video.youtube_url);
                                  toast.success('Ссылка скопирована в буфер обмена');
                                }}
                                className="flex items-center text-primary-600 hover:text-primary-800 text-xs mt-1"
                              >
                                <Copy className="w-3 h-3 mr-1" />
                                Копировать ссылку
                              </button>
                            </div>
                          ))}
                        </div>
                      </details>
                    ))}
                  </div>
                </div>
              ) : (
                <div>
                  <p><strong>ID загрузки:</strong> {uploadResult.upload_id}</p>
                  <p><strong>Название видео:</strong> {uploadResult.video_title}</p>
                  <p><strong>Ссылка на YouTube:</strong> 
                    <button
                      onClick={() => {
                        navigator.clipboard.writeText(uploadResult.youtube_url);
                        toast.success('Ссылка скопирована в буфер обмена');
                      }}
                      className="flex items-center text-primary-600 hover:text-primary-800 ml-2"
                    >
                      <Copy className="w-4 h-4 mr-1" />
                      Копировать ссылку
                    </button>
                  </p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default VideoUpload;
