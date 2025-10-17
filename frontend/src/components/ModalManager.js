import React, { useState, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, Image, Trash2, Eye } from 'lucide-react';
import axios from 'axios';
import toast from 'react-hot-toast';

const ModalManager = () => {
  const [modalImages, setModalImages] = useState([]);
  const [isUploading, setIsUploading] = useState(false);

  useEffect(() => {
    fetchModalImages();
  }, []);

  const fetchModalImages = async () => {
    try {
      const response = await axios.get('http://localhost:8000/modals');
      setModalImages(response.data.modals);
    } catch (error) {
      console.error('Ошибка загрузки модалок:', error);
      toast.error('Ошибка загрузки списка модалок');
    }
  };

  const onDrop = async (acceptedFiles) => {
    const files = acceptedFiles.filter(file => file.type.startsWith('image/'));
    
    if (files.length === 0) {
      toast.error('Пожалуйста, выберите изображения');
      return;
    }

    setIsUploading(true);

    try {
      for (const file of files) {
        const formData = new FormData();
        formData.append('image', file);

        const response = await axios.post('http://localhost:8000/upload/modal', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });

        if (response.data.success) {
          toast.success(`Модалка "${file.name}" загружена`);
        } else {
          toast.error(`Ошибка загрузки "${file.name}": ${response.data.error}`);
        }
      }

      // Обновляем список после загрузки
      await fetchModalImages();
    } catch (error) {
      console.error('Ошибка загрузки модалок:', error);
      toast.error('Ошибка загрузки модалок');
    } finally {
      setIsUploading(false);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    },
    multiple: true
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

  return (
    <div className="max-w-6xl mx-auto">
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">
          Управление модалками
        </h2>

        {/* Загрузка новых модалок */}
        <div className="mb-8">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Загрузить новые модалки
          </h3>
          
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
              isDragActive
                ? 'border-primary-400 bg-primary-50'
                : 'border-gray-300 hover:border-primary-400'
            } ${isUploading ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            <input {...getInputProps()} disabled={isUploading} />
            <Upload className="w-12 h-12 mx-auto mb-4 text-gray-400" />
            {isUploading ? (
              <div>
                <p className="text-gray-600 font-medium">Загрузка...</p>
                <p className="text-sm text-gray-500">Пожалуйста, подождите</p>
              </div>
            ) : (
              <div>
                <p className="text-gray-600 font-medium">
                  {isDragActive
                    ? 'Отпустите файлы здесь'
                    : 'Перетащите изображения сюда или нажмите для выбора'}
                </p>
                <p className="text-sm text-gray-500 mt-2">
                  Поддерживаемые форматы: JPG, PNG, GIF, WebP
                </p>
                <p className="text-sm text-gray-500">
                  Можно выбрать несколько файлов одновременно
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Список загруженных модалок */}
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Загруженные модалки ({modalImages.length})
          </h3>

          {modalImages.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <Image className="w-16 h-16 mx-auto mb-4 text-gray-300" />
              <p className="text-lg font-medium">Модалки не загружены</p>
              <p className="text-sm">Загрузите изображения модалок для использования в креативах</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {modalImages.map((modal) => (
                <div
                  key={modal.id}
                  className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                >
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-medium text-gray-900 truncate">
                      {modal.filename}
                    </h4>
                    <div className="flex space-x-2">
                      <button
                        className="p-1 text-gray-400 hover:text-gray-600 transition-colors"
                        title="Просмотр"
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                      <button
                        className="p-1 text-red-400 hover:text-red-600 transition-colors"
                        title="Удалить"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                  
                  <div className="text-sm text-gray-500">
                    <p>ID: {modal.id}</p>
                    <p>Загружено: {formatDate(modal.upload_date)}</p>
                  </div>

                  {/* Превью изображения */}
                  <div className="mt-3 bg-gray-100 rounded-lg p-4 text-center">
                    <Image className="w-8 h-8 mx-auto text-gray-400" />
                    <p className="text-xs text-gray-500 mt-1">Превью</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Информация о модалках */}
        <div className="mt-8 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <h4 className="font-medium text-blue-900 mb-2">Как использовать модалки</h4>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• Загрузите изображения модалок в формате JPG, PNG, GIF или WebP</li>
            <li>• Модалки будут накладываться на первый кадр видео при создании миниатюры</li>
            <li>• Выберите модалку при загрузке видео в разделе "Загрузка видео"</li>
            <li>• Рекомендуется использовать "мягкие" модалки для избежания блокировок</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default ModalManager;
