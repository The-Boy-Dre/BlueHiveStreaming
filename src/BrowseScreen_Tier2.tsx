// src/BrowseScreen_Tier2.tsx
import React, { useEffect, useRef, useState } from 'react';
import { View, StyleSheet } from 'react-native';
import OptionsBar from './OptionsBar_Tier3';
import MoviePage from './MoviesPage_Tier3';
import { Movie } from './MoviesPage_Tier3';

// 🧠 Point this to your local backend (update IP if needed)
// swap out 10.0.2.2 for your home IP address when testing on actual fire stick if your server is still located on your machine
const MOVIE_API = 'http://10.0.2.2:3000/api/movies'; 
const TV_API = 'http://10.0.2.2:3000/api/tv';

const BrowseScreen = () => {
  const [activeTab, setActiveTab] = useState<'Movies' | 'TV Series'>('Movies');
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<Movie[]>([]);

  const cache = useRef<{ movies: Movie[]; tv: Movie[] }>({ movies: [], tv: [] });

  const fetchContent = async (pageNumber: number, type: 'Movies' | 'TV Series') => {
    if (loading) return;
    setLoading(true);
    const URL = type === 'Movies' ? MOVIE_API : TV_API;

    try {
      const res = await fetch(`${URL}?page=${pageNumber}`);
      const json = await res.json();
      if (!Array.isArray(json)) throw new Error('Invalid API response');

      const updated = [...(type === 'Movies' ? cache.current.movies : cache.current.tv), ...json];

      if (type === 'Movies') {
        cache.current.movies = updated;
      } else {
        cache.current.tv = updated;
      }

      setData(updated);
      setPage(pageNumber);
    } catch (err: any) {
      console.error('🔥 API Fetch Error:', err.message);
    } finally {
      setLoading(false);
    }
  };




  const handleTabChange = (tab: 'Movies' | 'TV Series') => {
    setActiveTab(tab);
    const cached = tab === 'Movies' ? cache.current.movies : cache.current.tv;
    if (cached.length > 0) {
      setData(cached);
    } else {
      fetchContent(1, tab);
    }
  };

  const handleEndReached = () => {
    fetchContent(page + 1, activeTab);
  };

  // Initial load for Movies
  useEffect(() => {
    fetchContent(1, 'Movies');
  }, []);

  return (
    <View style={styles.container}>
      {/* Pass the tab change handler to OptionsBar */}
      <OptionsBar onTabChange={handleTabChange} />
      <MoviePage data={data} onEndReached={handleEndReached} />
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


