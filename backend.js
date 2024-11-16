const express = require('express');
const { exec } = require('child_process');
const path = require('path');
const fs = require('fs');

const app = express();
app.use(express.json());

app.post('/download', (req, res) => {
  const url = req.body.url;

  if (!url) {
    return res.status(400).json({ error: 'No URL provided' });
  }

  // Set a temporary path for the downloaded file
  const outputPath = path.join(__dirname, 'downloads', `video_${Date.now()}.mp4`);
  
  // Use yt-dlp standalone script and plugin
  const ytDlpPath = path.join(__dirname, 'bin', 'yt-dlp');
  const pluginPath = path.join(__dirname, 'youtube_agb_plugin.py');
  const command = `"${ytDlpPath}" --plugin "${pluginPath}" -o "${outputPath}" "${url}"`;

  exec(command, { maxBuffer: 1024 * 500 }, (error, stdout, stderr) => {
    if (error) {
      console.error('Error:', stderr);
      return res.status(500).json({ error: stderr });
    }

    // Check if the file exists before sending the response
    if (fs.existsSync(outputPath)) {
      const publicURL = 'https://vidownloader-backend.onrender.com';
      res.json({ downloadLink: `${publicURL}/download-file?path=${encodeURIComponent(outputPath)}` });
    } else {
      res.status(500).json({ error: 'Failed to download video.' });
    }
  });
});

app.get('/download-file', (req, res) => {
  const filePath = req.query.path;

  if (fs.existsSync(filePath)) {
    res.setHeader('Content-Disposition', `attachment; filename="${path.basename(filePath)}"`);
    res.setHeader('Content-Type', 'video/mp4');
    res.sendFile(filePath);
  } else {
    res.status(404).send('File not found');
  }
});

app.listen(3000, () => {
  console.log('Server is running on http://localhost:3000');
});
