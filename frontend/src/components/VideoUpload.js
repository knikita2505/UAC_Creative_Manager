import React, { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, Link, Image, CheckCircle, AlertCircle, Copy } from 'lucide-react';
import axios from 'axios';
import toast from 'react-hot-toast';

const VideoUpload = () => {
  const [formData, setFormData] = useState({
    campaign_name: '',
    video_source: 'local',
    drive_urls: '',
    thumbnail_option: 'none',
    modal_image_id: null
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
          modal_image_id: null
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
          {/* Название кампании */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Название кампании *
            </label>
            <input
              type="text"
              name="campaign_name"
              value={formData.campaign_name}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              placeholder="Введите название кампании"
              required
            />
            <p className="text-sm text-gray-500 mt-1">
              Название видео будет: "{formData.campaign_name || 'Название кампании'} {new Date().toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit', year: '2-digit' })}"
            </p>
          </div>

          {/* Источник видео */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Источник видео *
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
                    <p className="text-sm text-gray-500 mt-1">
                      Поддерживаемые форматы: MP4, AVI, MOV, MKV, WebM
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
              <p className="text-sm text-gray-500 mt-1">
                Введите ссылки на видео в Google Drive, по одной на строку
              </p>
            </div>
          )}

          {/* Настройки миниатюры */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Настройки миниатюры
            </label>
            <div className="space-y-3">
              <label className="flex items-center">
                <input
                  type="radio"
                  name="thumbnail_option"
                  value="none"
                  checked={formData.thumbnail_option === 'none'}
                  onChange={handleInputChange}
                  className="mr-3"
                />
                <span>Не изменять миниатюру</span>
              </label>
              <label className="flex items-center">
                <input
                  type="radio"
                  name="thumbnail_option"
                  value="first_frame"
                  checked={formData.thumbnail_option === 'first_frame'}
                  onChange={handleInputChange}
                  className="mr-3"
                />
                <span>Поставить первый кадр видео</span>
              </label>
              <label className="flex items-center">
                <input
                  type="radio"
                  name="thumbnail_option"
                  value="soft_modal"
                  checked={formData.thumbnail_option === 'soft_modal'}
                  onChange={handleInputChange}
                  className="mr-3"
                />
                <span>Создать кастомную миниатюру с модалкой</span>
              </label>
            </div>

            {/* Выбор модалки */}
            {formData.thumbnail_option === 'soft_modal' && (
              <div className="mt-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Выберите модалку
                </label>
                {modalImages.length > 0 ? (
                  <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                    {modalImages.map((modal) => (
                      <div
                        key={modal.id}
                        className={`border-2 rounded-lg p-3 cursor-pointer transition-all ${
                          formData.modal_image_id === modal.id
                            ? 'border-primary-500 bg-primary-50'
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                        onClick={() => {
                          setFormData(prev => ({
                            ...prev,
                            modal_image_id: modal.id
                          }));
                          setSelectedModal(modal);
                        }}
                      >
                        <div className="aspect-square bg-gray-100 rounded-md mb-2 overflow-hidden">
                          <img
                            src={`http://localhost:8000/modals/${modal.id}/preview`}
                            alt={modal.filename}
                            className="w-full h-full object-cover"
                            onError={(e) => {
                              e.target.style.display = 'none';
                              e.target.nextSibling.style.display = 'flex';
                            }}
                          />
                          <div className="hidden w-full h-full items-center justify-center">
                            <Image className="w-8 h-8 text-gray-400" />
                          </div>
                        </div>
                        <div className="text-sm font-medium text-gray-900 truncate">
                          {modal.filename}
                        </div>
                        <div className="text-xs text-gray-500">
                          {modal.file_size ? `${(modal.file_size / 1024).toFixed(1)} KB` : 'Размер неизвестен'}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8 text-gray-500 border-2 border-dashed border-gray-300 rounded-lg">
                    <Image className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                    <p className="font-medium">Модалки не загружены</p>
                    <p className="text-sm">Перейдите в раздел "Модалки" для загрузки изображений</p>
                  </div>
                )}
                
                {/* Показываем выбранную модалку */}
                {selectedModal && (
                  <div className="mt-4 p-3 bg-primary-50 border border-primary-200 rounded-lg">
                    <div className="flex items-center">
                      <CheckCircle className="w-5 h-5 text-primary-600 mr-2" />
                      <span className="text-sm font-medium text-primary-800">
                        Выбрана модалка: {selectedModal.filename}
                      </span>
                    </div>
                  </div>
                )}
              </div>
            )}
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
              {uploadResult.total_videos > 1 ? (
                <div>
                  <p><strong>Всего видео:</strong> {uploadResult.total_videos}</p>
                  <p><strong>Успешно загружено:</strong> {uploadResult.successful_uploads}</p>
                  <p><strong>Ошибок:</strong> {uploadResult.failed_uploads}</p>
                  
                  {/* Детали по каждому видео */}
                  <div className="mt-3 space-y-2">
                    {uploadResult.results.map((result, index) => (
                      <div key={index} className={`p-2 rounded ${
                        result.success ? 'bg-green-100' : 'bg-red-100'
                      }`}>
                        <div className="flex items-center justify-between">
                          <span className="font-medium">{result.video_title}</span>
                          {result.success ? (
                            <CheckCircle className="w-4 h-4 text-green-600" />
                          ) : (
                            <AlertCircle className="w-4 h-4 text-red-600" />
                          )}
                        </div>
                        {result.success && result.youtube_url && (
                          <button
                            onClick={() => {
                              navigator.clipboard.writeText(result.youtube_url);
                              toast.success('Ссылка скопирована в буфер обмена');
                            }}
                            className="flex items-center text-primary-600 hover:text-primary-800 text-xs"
                          >
                            <Copy className="w-3 h-3 mr-1" />
                            Копировать ссылку
                          </button>
                        )}
                        {!result.success && result.error && (
                          <p className="text-red-600 text-xs mt-1">Ошибка: {result.error}</p>
                        )}
                      </div>
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
