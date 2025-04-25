// BrowseScreen_Tier2.tsx (Functions restored, original user styles kept)

import React, { useState, useRef, useEffect } from 'react';
import { View, StyleSheet, Dimensions, Text, ActivityIndicator, StyleProp, ViewStyle, TextStyle, ImageStyle } from 'react-native';
import OptionsBar from './OptionsBar_Tier3';
import MoviesPage from './MoviesPage_Tier3';
import TVShowsPage from './TVShowsPage_Tier3';

// --- 1) Centralized Layout Calculations ---
const screenWidth = Dimensions.get('window').width;
const posterMargin = 8;
const numColumns = 6;
const posterWidth = (screenWidth - posterMargin * 2.6 * numColumns) / numColumns;
const onEndReachedThreshold = 0.5;
const windowSize = 11;
const initialNumToRender = numColumns * 4;
const maxToRenderPerBatch = numColumns * 2;
const updateCellsBatchingPeriod = 50;
const removeClippedSubviews = true;




const BrowseScreen = () => {
  const [activeTab, setActiveTab] = useState<'Movies' | 'TV Series'>('Movies');
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<DisplayItem[]>([]);
  const cache = useRef<{ movies: DisplayItem[]; tv: DisplayItem[] }>({ movies: [], tv: [] });
  
  // --- FUNCTION IMPLEMENTATION RESTORED ---
  const fetchContent = async (pageNumber: number, type: 'Movies' | 'TV Series', isInitialLoad = false) => {
    if (loading && !isInitialLoad) return;
    if (!isInitialLoad && pageNumber === 1) {
      const cachedData = type === 'Movies' ? cache.current.movies : cache.current.tv;
      if (cachedData.length > 0) {
            console.log(`Using cache for ${type}`);
            setData(cachedData);
            return;
        }
    }
    console.log(`Fetching ${type} page ${pageNumber}...`);
    setLoading(true);
    const endpoint = type === 'Movies' ? 'movies' : 'tv';
    const currentDataInCache = type === 'Movies' ? cache.current.movies : cache.current.tv;
    try {
      const apiUrl = `http://10.0.2.2:3000/api/${endpoint}?page=${pageNumber}`;
      console.log('API URL:', apiUrl);
      const res = await fetch(apiUrl);
       if (!res.ok) {
         throw new Error(`HTTP error! status: ${res.status} ${res.statusText}`);
       }
       const json = await res.json();
      console.log(`Received data for ${type} page ${pageNumber}:`, JSON.stringify(json, null, 2).substring(0, 300) + '...');
      const newItems: DisplayItem[] = Array.isArray(json) ? json : [];
       console.log(`Processed ${newItems.length} new items for ${type} page ${pageNumber}`);
      const updatedData = pageNumber === 1 ? newItems : [...currentDataInCache, ...newItems];
      if (type === 'Movies') {
        cache.current.movies = updatedData;
      } else {
        cache.current.tv = updatedData;
      }
      setData(updatedData);
      setPage(pageNumber);
    } catch (err) {
      console.error('🔥 Fetch error:', err);
    } finally {
      setLoading(false);
    }
  };
  // --- END FUNCTION IMPLEMENTATION RESTORED ---
  

  // --- UseEffect IMPLEMENTATION RESTORED ---
  useEffect(() => {
    console.log(`Effect triggered: activeTab is ${activeTab}`);
    setPage(1);
    const cached = activeTab === 'Movies' ? cache.current.movies : cache.current.tv;
    if (cached.length === 0) {
      console.log(`Cache empty for ${activeTab}, initiating fetch.`);
      fetchContent(1, activeTab, true);
    } else {
       console.log(`Loading ${activeTab} from cache.`);
       setData(cached);
    }
  }, [activeTab]);
 // --- END UseEffect IMPLEMENTATION RESTORED ---
 

 // --- handleTabChange IMPLEMENTATION RESTORED ---
 const handleTabChange = (tab: 'Movies' | 'TV Series') => {
    if (tab !== activeTab) {
      console.log(`Tab changed to: ${tab}`);
        setActiveTab(tab);
      }
  };
  // --- END handleTabChange IMPLEMENTATION RESTORED ---

  // --- handleEndReached IMPLEMENTATION RESTORED ---
  const handleEndReached = () => {
    if (!loading && data.length > 0) {
        const nextPage = page + 1;
        console.log(`End reached for ${activeTab}, attempting to fetch page ${nextPage}`);
        fetchContent(nextPage, activeTab);
    } else if (loading) {
        console.log('End reached but already loading, skipping fetch.');
      } else {
         console.log('End reached but no data loaded yet, skipping fetch.');
        }
      };
  // --- END handleEndReached IMPLEMENTATION RESTORED ---
  
  
  // 2) Listing which Props are for the Child Components
  const mediaPageProps: Omit<MediaPageProps, 'data' | 'onEndReached'> = {
    numColumns: numColumns,
    listContentContainerStyle: styles.list,
    posterContainerStyle: styles.posterContainer, 
      focusedPosterStyle: styles.focusedPoster, 
      posterStyle: styles.poster, 
      titleTextStyle: styles.title, 
      dateStyle: styles.date, 
      fallbackContainerStyle: styles.fallbackContainer,
      fallbackTextStyle: styles.fallbackText, 
      onEndReachedThreshold: onEndReachedThreshold,
      windowSize: windowSize,
      initialNumToRender: initialNumToRender,
      maxToRenderPerBatch: maxToRenderPerBatch,
      updateCellsBatchingPeriod: updateCellsBatchingPeriod,
      removeClippedSubviews: removeClippedSubviews,
  };
  
  return (
    <View style={styles.container}>
       <OptionsBar onTabChange={handleTabChange} />
       {activeTab === 'Movies' ? (
         <MoviesPage data={data} onEndReached={handleEndReached} {...mediaPageProps} />
       ) : (
         <TVShowsPage data={data} onEndReached={handleEndReached} {...mediaPageProps} />
       )}
       {loading && (!data || data.length === 0) && (
         <View style={styles.loadingOverlay}>
             <ActivityIndicator size="large" color="gold" />
          </View>
       )}
    </View>
  );
};
        // --- Centralized Stylesheet ---
        // Using the exact styles from your previous code snippet where functions were missing
        const styles = StyleSheet.create({
            container: { flex: 1, backgroundColor: '#000', },
            list: { padding: 16, paddingTop: 10, }, // Your original list style
            posterContainer: { width: posterWidth, margin: posterMargin, marginBottom: posterMargin + 10, marginLeft: posterMargin, marginRight: posterMargin, alignItems: 'center', }, // Your original posterContainer style
            focusedPoster: { borderWidth: 3, borderColor: 'gold', borderRadius: 12, margin: posterMargin - 3, }, // Your original focusedPoster style
            poster: { // Your original poster style
                width: '100%',
                height: posterWidth * 1.5,
                borderRadius: 8,
                backgroundColor: '#333',
              },
            title: { color: 'white', marginTop: 6, fontSize: 12, fontWeight: '500', textAlign: 'center', width: '100%', }, // Your original title style
            date: { color: 'gray', fontSize: 10, marginTop: 2, textAlign: 'center', width: '100%', }, // Your original date style
            fallbackContainer: { flex: 1, justifyContent: 'center', alignItems: 'center', marginTop: 40, }, // Your original fallbackContainer style
            fallbackText: { color: 'gray', fontSize: 16, }, // Your original fallbackText style
            loadingOverlay: { position: 'absolute', left: 0, right: 0, top: 50, bottom: 0, alignItems: 'center', justifyContent: 'center', }, // Your original loadingOverlay style
          });
    




  export default BrowseScreen;
  
  // --- Central Type Definition ---
  export type DisplayItem = {
    id: number;
    title: string;
    year: string;
    poster_url: string | null;
  };
  
  // --- 3) Now exporting props to child component ---
  //! --- make sure to list the variable DATA TYPES when exporting ---
  export type MediaPageProps = {
    data: DisplayItem[];
    onEndReached: () => void;
    numColumns: number;
    listContentContainerStyle: StyleProp<ViewStyle>;
    posterContainerStyle: StyleProp<ViewStyle>;
    focusedPosterStyle: StyleProp<ViewStyle>;
    posterStyle: StyleProp<ImageStyle>;
    titleTextStyle: StyleProp<TextStyle>;
    dateStyle: StyleProp<TextStyle>;
    fallbackContainerStyle: StyleProp<ViewStyle>;
    fallbackTextStyle: StyleProp<TextStyle>;
    onEndReachedThreshold: number;
    windowSize: number;
    initialNumToRender: number;
    maxToRenderPerBatch: number;
    updateCellsBatchingPeriod: number
    removeClippedSubviews: boolean
  };
  
