const express = require('express');
const multer = require('multer');
const path = require('path');
const cors = require('cors');
const { spawn } = require('child_process');  // 正确引入 spawn


const app = express();
const port = 5000;

// 允许跨域请求
app.use(cors());

// 创建存储配置，支持图片和压缩文件
const storage = multer.diskStorage({
    destination: function (req, file, cb) {
        cb(null, 'uploads/'); // 所有文件都存到 uploads 目录
    },
    filename: function (req, file, cb) {
        cb(null, Date.now() + path.extname(file.originalname)); // 生成唯一文件名
    }
});

// 过滤上传文件类型，允许图片和压缩包
const fileFilter = (req, file, cb) => {
    const allowedTypes = ['.jpg', '.jpeg', '.png', '.gif', '.zip', '.rar'];
    const ext = path.extname(file.originalname).toLowerCase();
    
    if (allowedTypes.includes(ext)) {
        cb(null, true); // 允许上传
    } else {
        cb(new Error('Unsupported file type'), false); // 拒绝上传
    }
};

// 创建上传实例
const upload = multer({ storage: storage, fileFilter: fileFilter });

// 处理文件上传的路由
app.post('/upload', upload.single('file'), (req, res) => {
    if (!req.file) {
        return res.status(400).json({ message: 'No file uploaded or unsupported file type' });
    }
        // 文件上传成功，开始调用 Python 脚本处理文件
    const filePath = path.join(__dirname, 'uploads', req.file.filename);
    console.log(`Uploaded file path: ${filePath}`);
    
    // 在 LOFTR 环境中调用 Python 脚本
    const pythonPath = 'D:/Program/anaconda/envs/loftr/python.exe';  // LOFTR 环境下的 Python 可执行路径
    const pythonScript = 'E:/code/QD/python/zip2pdf.py';  // Python 脚本路径

    const pythonProcess = spawn(pythonPath, [pythonScript, filePath]);

    pythonProcess.stdout.on('data', (data) => {
        console.log(`Python Output: ${data}`);
    });

    pythonProcess.stderr.on('data', (data) => {
        console.error(`Python Error: ${data}`);
    });

    pythonProcess.on('close', (code) => {
        console.log(`Python process exited with code ${code}`);
        res.json({ message: 'File uploaded and processed', filePath: `/uploads/${req.file.filename}` });
    });

    // res.json({ message: 'File uploaded successfully', filePath: `/uploads/${req.file.filename}` });
});

// 启动服务器
app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
});
