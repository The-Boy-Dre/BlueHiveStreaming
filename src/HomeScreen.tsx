import React, { useEffect, useState } from 'react';
import { View, FlatList, Button, StyleSheet, useTVEventHandler } from 'react-native';
import axios from 'axios';
import { LRUCache } from 'lru-cache';
import { NavigationProp } from '@react-navigation/native';

// Define the navigation parameters
type RootStackParamList = {
  Home: undefined;
  Movie: { movieId: string };
};

// Define the type for the navigation prop
type HomeScreenNavigationProp = NavigationProp<RootStackParamList, 'Home'>;

// Define the props for the HomeScreen component
type HomeScreenProps = {
  navigation: HomeScreenNavigationProp;
};

const cache = new LRUCache({ max: 100, ttl: 1000 * 60 * 5 });

const HomeScreen = ({ navigation }: HomeScreenProps) => {
  const [movies, setMovies] = useState<{ id: string; title: string }[]>([]);

  useEffect(() => {
    const fetchMovies = async () => {
      const cachedMovies = cache.get('movies') as { id: string; title: string }[] | undefined;
      if (cachedMovies) {
        setMovies(cachedMovies);
        return;
      }
      const response = await axios.get<{ id: string; title: string }[]>('http://your-backend-api/movies');
      cache.set('movies', response.data);
      setMovies(response.data);
    };

    fetchMovies();
  }, []);

  // Handle TV remote events using useTVEventHandler hook
  useTVEventHandler((evt) => {
    if (evt.eventType === 'up') {
      console.log('Up button pressed');
    } else if (evt.eventType === 'down') {
      console.log('Down button pressed');
    }
    // You can add other event cases here if needed.
  });

  return (
    <View style={styles.container}>
      <FlatList
        data={movies}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => (
          <Button
            title={item.title}
            onPress={() => navigation.navigate('Movie', { movieId: item.id })}
          />
        )}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
  },
});

export default HomeScreen;
