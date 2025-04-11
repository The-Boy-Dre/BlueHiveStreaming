// src/BrowseScreen.tsx
import React, { useEffect, useState } from 'react';
import { View, StyleSheet } from 'react-native';
import OptionsBar from './OptionsBar_Tier3';
import MoviePage from './MoviePage_Tier3';
import { Movie } from './MoviePage_Tier3'; 
import axios from 'axios';



const API_KEY = '09043a3c24de9d07b1d0f710f1b29a3d'; // or your real key
const BASE_URL = `https://api.themoviedb.org/3/trending/movie/day?api_key=${API_KEY}`;

const BrowseScreen = () => {
  const [movies, setMovies] = useState<Movie[]>([]);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);

  const fetchMovies = async (pageNumber: number) => {
    if (loading) return; // prevent multiple calls
    setLoading(true);
    try {
      const res = await axios.get(`${BASE_URL}&page=${pageNumber}`);
      setMovies(prev => [...prev, ...res.data.results]);
      setPage(pageNumber);
    } catch (err) {
      console.error('🔥 Fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMovies(1); // initial load
  }, []);

  const handleEndReached = () => {
    fetchMovies(page + 1);
  };

  return (
    <View style={styles.container}>
      <OptionsBar />
      <MoviePage data={movies} onEndReached={handleEndReached} />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000',
  },
});

export default BrowseScreen;