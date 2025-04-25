
const express = require('express');
const cors = require('cors');

const app = express();
const PORT = 3000;

const TMDB_API_KEY = '5026dab92925f7cb0e77c59bc1e0b240';
const IMAGE_BASE_URL = 'https://image.tmdb.org/t/p/w500';


app.use(cors());

app.get('/api/movies', async (req, res) => {
  const page = req.query.page || 1;
  const url = `https://api.themoviedb.org/3/trending/movie/day?api_key=${TMDB_API_KEY}&page=${page}`;

  try {
    const response = await fetch(url);
    const data = await response.json();
    const simplified = data.results.map(movie => ({
      id: movie.id,
      title: movie.title || 'N/A',
      year: movie.release_date?.split('-')[0] || 'N/A',
      poster_url: movie.poster_path ? IMAGE_BASE_URL + movie.poster_path : null,
    }));
    res.json(simplified);
  } catch (err) {
    console.error('🔥 Movie Fetch Error:', err.message);
    res.status(500).json({ error: 'Failed to fetch movies' });
  }
});



app.get('/api/tv', async (req, res) => {
  const page = req.query.page || 1;
  const url = `https://api.themoviedb.org/3/trending/tv/day?api_key=${TMDB_API_KEY}&page=${page}`;

  try {
    const response = await fetch(url);
    const data = await response.json();
    const simplified = data.results.map(show => ({
      id: show.id,
      title: show.name || 'N/A',
      year: show.first_air_date?.split('-')[0] || 'N/A',
      poster_url: show.poster_path ? IMAGE_BASE_URL + show.poster_path : null,
    }));
    res.json(simplified);
  } catch (err) {
    console.error('🔥 TV Fetch Error:', err.message);
    res.status(500).json({ error: 'Failed to fetch TV shows' });
  }
});



app.listen(PORT, () => {
  console.log(`✅ Server running at http://localhost:${PORT}`);
});
