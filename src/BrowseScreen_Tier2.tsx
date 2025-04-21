// src/BrowseScreen_Tier2.tsx
import React, { useEffect, useState } from 'react';
import { View, StyleSheet } from 'react-native';
import OptionsBar from './OptionsBar_Tier3';
import MoviePage from './MoviePage_Tier3';
import { Movie } from './MoviePage_Tier3';

// 🧠 Point this to your local backend (update IP if needed)
const BrowseScreen = () => {
  const [movies, setMovies] = useState<Movie[]>([]);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);


  const fetchMovies = async (pageNumber: number) => {
    if (loading) return;
    setLoading(true);
    try {
      // swap out 10.0.2.2 for your home IP address when testing on actual fire stick if your server is still located on your machine
      const response = await fetch(`http://10.0.2.2:3000/api/movies?page=${pageNumber}`);
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const data = await response.json();
  
      console.log('✅ Proxy fetch response:', data);
      setMovies((prev) => [...prev, ...data]);
      setPage(pageNumber);
    } catch (err: any) {
      console.error('🔥 Fetch Error:', err.message);
    } finally {
      setLoading(false);
    }
  };
  

  useEffect(() => {
    fetchMovies(1);
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


