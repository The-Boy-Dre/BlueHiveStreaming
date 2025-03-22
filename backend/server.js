// backend/server.js
const express = require('express');
const cors = require('cors');
const { scrapeMovies } = require('./scraper');
const { connectDB } = require('./db');

const app = express();
app.use(cors());
app.use(express.json());

// Connect to MongoDB (if needed for further use)
connectDB();

// Endpoint to get movies list
app.get('/movies', async (req, res) => {
  try {
    const movies = await scrapeMovies();
    res.json(movies);
  } catch (error) {
    console.error('Error fetching movies:', error);
    res.status(500).json({ error: 'Failed to fetch movies' });
  }
});

// Endpoint to get a single movie's details by ID
app.get('/movies/:id', async (req, res) => {
  // For demonstration, you can extend this to query MongoDB
  // For now, just return a dummy movie or filter from scraped data
  const movieId = req.params.id;
  // Replace this with real logic
  res.json({
    id: movieId,
    title: `Movie ${movieId}`,
    videoUrl: 'https://example.com/path/to/movie.mp4',
  });
});

const PORT = 3000;
app.listen(PORT, () => console.log(`Backend server running on http://localhost:${PORT}`));
