document.addEventListener('DOMContentLoaded', function() {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('photo');
    const photoPreview = document.getElementById('photoPreview');
    const previewImg = photoPreview.querySelector('img');
    const removeButton = photoPreview.querySelector('.remove-photo');

    // Обработка клика по зоне загрузки
    dropZone.addEventListener('click', () => fileInput.click());

    // Drag and Drop
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('drag-over');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('drag-over');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('drag-over');

        if (e.dataTransfer.files.length) {
            fileInput.files = e.dataTransfer.files;
            handleFileSelect(e.dataTransfer.files[0]);
        }
    });

    // Обработка выбора файла
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length) {
            handleFileSelect(e.target.files[0]);
        }
    });

    // Удаление фото
    removeButton.addEventListener('click', () => {
        fileInput.value = '';
        photoPreview.style.display = 'none';
        previewImg.src = '';
    });

    function handleFileSelect(file) {
        if (file.type.startsWith('image/')) {
            const reader = new FileReader();

            reader.onload = function(e) {
                previewImg.src = e.target.result;
                photoPreview.style.display = 'block';
            };

            reader.readAsDataURL(file);
        } else {
            alert('Пожалуйста, выберите изображение');
        }
    }
});

