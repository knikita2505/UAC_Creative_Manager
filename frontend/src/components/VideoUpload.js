import React, { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, Link, Image, CheckCircle, AlertCircle } from 'lucide-react';
import axios from 'axios';
import toast from 'react-hot-toast';

const VideoUpload = () => {
  const [formData, setFormData] = useState({
    campaign_name: '',
    video_source: 'local',
    drive_url: '',
    thumbnail_option: 'none',
    modal_image_id: null
  });
  const [uploadedFile, setUploadedFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);
  const [modalImages, setModalImages] = useState([]);

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
    const file = acceptedFiles[0];
    if (file && file.type.startsWith('video/')) {
      setUploadedFile(file);
      toast.success('Видео файл выбран');
    } else {
      toast.error('Пожалуйста, выберите видео файл');
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'video/*': ['.mp4', '.avi', '.mov', '.mkv', '.webm']
    },
    multiple: false
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

    if (formData.video_source === 'local' && !uploadedFile) {
      toast.error('Выберите видео файл');
      return;
    }

    if (formData.video_source === 'drive' && !formData.drive_url.trim()) {
      toast.error('Введите ссылку на Google Drive');
      return;
    }

    if (formData.thumbnail_option === 'custom_modal' && !formData.modal_image_id) {
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
        submitData.append('drive_url', formData.drive_url);
      }
      
      if (formData.thumbnail_option === 'custom_modal') {
        submitData.append('modal_image_id', formData.modal_image_id);
      }
      
      if (uploadedFile) {
        submitData.append('video_file', uploadedFile);
      }

      const response = await axios.post('http://localhost:8000/upload/video', submitData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.data.success) {
        setUploadResult(response.data);
        toast.success('Видео успешно загружено на YouTube!');
        // Сброс формы
        setFormData({
          campaign_name: '',
          video_source: 'local',
          drive_url: '',
          thumbnail_option: 'none',
          modal_image_id: null
        });
        setUploadedFile(null);
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

          {/* Загрузка файла или ссылка на Drive */}
          {formData.video_source === 'local' ? (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Видео файл *
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
                {uploadedFile ? (
                  <div className="text-green-600">
                    <CheckCircle className="w-6 h-6 mx-auto mb-2" />
                    <p className="font-medium">{uploadedFile.name}</p>
                    <p className="text-sm text-gray-500">
                      {(uploadedFile.size / (1024 * 1024)).toFixed(2)} MB
                    </p>
                  </div>
                ) : (
                  <div>
                    <p className="text-gray-600">
                      {isDragActive
                        ? 'Отпустите файл здесь'
                        : 'Перетащите видео файл сюда или нажмите для выбора'}
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
                Ссылка на Google Drive *
              </label>
              <div className="flex">
                <input
                  type="url"
                  name="drive_url"
                  value={formData.drive_url}
                  onChange={handleInputChange}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-l-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="https://drive.google.com/file/d/..."
                />
                <div className="px-3 py-2 bg-gray-100 border border-l-0 border-gray-300 rounded-r-md flex items-center">
                  <Link className="w-4 h-4 text-gray-500" />
                </div>
              </div>
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
                  value="custom_modal"
                  checked={formData.thumbnail_option === 'custom_modal'}
                  onChange={handleInputChange}
                  className="mr-3"
                />
                <span>Создать кастомную миниатюру с модалкой</span>
              </label>
            </div>

            {/* Выбор модалки */}
            {formData.thumbnail_option === 'custom_modal' && (
              <div className="mt-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Выберите модалку
                </label>
                {modalImages.length > 0 ? (
                  <select
                    name="modal_image_id"
                    value={formData.modal_image_id || ''}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  >
                    <option value="">Выберите модалку...</option>
                    {modalImages.map((modal) => (
                      <option key={modal.id} value={modal.id}>
                        {modal.filename}
                      </option>
                    ))}
                  </select>
                ) : (
                  <div className="text-center py-4 text-gray-500">
                    <Image className="w-8 h-8 mx-auto mb-2" />
                    <p>Модалки не загружены</p>
                    <p className="text-sm">Перейдите в раздел "Модалки" для загрузки</p>
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
              <h3 className="font-medium text-green-800">Загрузка завершена успешно!</h3>
            </div>
            <div className="mt-2 text-sm text-green-700">
              <p><strong>ID загрузки:</strong> {uploadResult.upload_id}</p>
              <p><strong>Название видео:</strong> {uploadResult.video_title}</p>
              <p><strong>Ссылка на YouTube:</strong> 
                <a 
                  href={uploadResult.youtube_url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-primary-600 hover:text-primary-800 ml-1"
                >
                  {uploadResult.youtube_url}
                </a>
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default VideoUpload;
