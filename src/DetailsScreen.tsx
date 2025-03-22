//!This screen fetches details for a selected movie and plays the video:


import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet } from 'react-native';
import Video from 'react-native-video';
import axios from 'axios';
import { RouteProp } from '@react-navigation/native'; // Import RouteProp

// Define the type for your route parameters
type RootStackParamList = {
  Details: { detailId: string }; // Adjust this to match your navigation structure
};

// Define the type for the route prop
type DetailsScreenRouteProp = RouteProp<RootStackParamList, 'Details'>;

// Define the Movie type
type Movie = {
  id: string;
  title: string;
  videoUrl: string;
};

// Define the props for the DetailsScreen component
type DetailsScreenProps = {
  route: DetailsScreenRouteProp;
};

const DetailsScreen = ({ route }: DetailsScreenProps) => {
  const { detailId } = route.params;
  const [movie, setMovie] = useState<Movie | null>(null);

  useEffect(() => {
    const fetchMovie = async () => {
      const response = await axios.get<Movie>(`http://your-backend-api/movies/${detailId}`);
      setMovie(response.data);
    };

    fetchMovie();
  }, [detailId]);

  if (!movie) {
    return <Text>Loading...</Text>;
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>{movie.title}</Text>
      <Video
        source={{ uri: movie.videoUrl }}
        controls={true}
        style={styles.video}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
  },
  title: {
    fontSize: 24,
    marginBottom: 20,
  },
  video: {
    width: '100%',
    height: 300,
  },
});

export default DetailsScreen;
