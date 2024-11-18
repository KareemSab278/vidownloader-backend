const express = require('express');
const { exec } = require('child_process');

const app = express();
app.use(express.json());

app.post('/get-download-info', (req, res) => {
  const url = req.body.url;

  if (!url) {
    return res.status(400).json({ error: 'No URL provided' });
  }

  // Use yt-dlp to fetch the direct video URL without downloading
  const ytDlpPath = path.join(__dirname, 'bin', 'yt-dlp');
  const pluginPath = path.join(__dirname, 'youtube_agb_plugin.py');
  const command = `"${ytDlpPath}" --plugin "${pluginPath}" --get-url "${url}"`;

  exec(command, (error, stdout, stderr) => {
    if (error) {
      console.error('Error:', stderr);
      return res.status(500).json({ error: stderr });
    }

    // Send the direct video URL to the client
    const videoUrl = stdout.trim();
    res.json({ videoUrl });
  });
});

app.listen(3000, () => {
  console.log('Server is running on http://localhost:3000');
});
