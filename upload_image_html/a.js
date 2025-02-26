document.getElementById('uploadButton').addEventListener('click', function () {
    const fileInput = document.getElementById('file-upload');
    const file = fileInput.files[0];

    if (!file) {
        alert('请先选择文件');
        return;
    }

    // 允许的文件扩展名
    const allowedExtensions = ['.zip', '.rar'];
    const fileExtension = file.name.slice(file.name.lastIndexOf('.')).toLowerCase();

    if (!allowedExtensions.includes(fileExtension)) {
        alert('仅支持上传 .eip 和 .rar 文件');
        return;
    }

    const formData = new FormData();
    formData.append('file', file); // 修改为 'file'，具体字段名根据后端 API 要求

    fetch('http://localhost:5000/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.filePath) {
            alert('上传成功！');
            console.log('文件保存路径:', data.filePath);
        } else {
            alert('上传失败');
        }
    })
    .catch(error => {
        console.error('上传出错:', error);
    });
});



function displayFileInfo() {
    const fileInput = document.getElementById('file-upload');
    const fileInfo = document.getElementById('file-info');
    if (fileInput.files.length > 0) {
        const file = fileInput.files[0];
        fileInfo.textContent = `文件名: ${file.name} | 类型: ${file.type || '未知'}`;
    } else {
        fileInfo.textContent = '未选择文件';
    }
}