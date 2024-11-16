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

  // Full path to yt-dlp (corrected for Linux environment)
  const ytDlpPath = './yt-dlp'; // Updated to point to the root folder
  const cookiesPath = './cookies.txt'; // If you're using cookies for authentication

  // Command to download video using yt-dlp with higher speed settings
  const command = `"${ytDlpPath}" --cookies "${cookiesPath}" -o "${outputPath}" --concurrent-fragments 16 --fragment-retries 10 --socket-timeout 15 --user-agent "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3" "${url}"`;

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

// Endpoint to serve the downloaded file
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
