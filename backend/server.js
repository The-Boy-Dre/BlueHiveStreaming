
// backend/server.js
const express = require('express');
const cors = require('cors');


const app = express();
const PORT = 3000;

const TMDB_API_KEY = '5026dab92925f7cb0e77c59bc1e0b240';

app.use(cors());

app.get('/api/movies', async (req, res) => {

  const page = req.query.page || 1;
  const url = `https://api.themoviedb.org/3/trending/movie/day?api_key=${TMDB_API_KEY}&page=${page}`;

  try {
    const response = await fetch(url);
    if (!response.ok) {throw new Error(`TMDb responded with ${response.status}`);}

    const data = await response.json();
    res.json(data.results); // Only send the movie list to keep the payload clean
  } catch (err) {
    console.error('🔥 Fetch error from TMDb:', err.message);
    res.status(500).json({ error: 'Failed to fetch movies from TMDb' });
  }
});

app.listen(PORT, () => {
  console.log(`✅ Movie proxy running on http://localhost:${PORT}/api/movies`);
});
