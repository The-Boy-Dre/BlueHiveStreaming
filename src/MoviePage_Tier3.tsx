import React, { useState } from 'react';
import { View, Text, Image, StyleSheet, FlatList, Pressable } from 'react-native';
import { Dimensions } from 'react-native';



const IMAGE_BASE_URL = 'https://image.tmdb.org/t/p/w500';

const screenWidth = Dimensions.get('window').width;
const posterMargin = 8 // adjust as needed
const numColumns = 6;   // your desired number of columns
const posterWidth = (screenWidth - posterMargin * 2 * numColumns) / numColumns;


export type Movie = {
  id: number;
  title: string;
  release_date: string;
  poster_path: string;
};

type Props = {
  data: Movie[];
  onEndReached: () => void;
};



const MoviePage: React.FC<Props> = ({ data, onEndReached })=> {
  const [focusedIndex, setFocusedIndex] = useState<number | null>(null); // Naviagtion 
  
  const renderItem = ({ item, index }: { item: Movie; index: number }) => (
    <Pressable style={[ styles.posterContainer, focusedIndex === index && styles.focusedPoster ]} onFocus={() => setFocusedIndex(index)}  onBlur={() => setFocusedIndex(null)}>

        <Image source={{ uri: IMAGE_BASE_URL + item.poster_path }} style={styles.poster} resizeMode="cover"/>
        <Text style={styles.title}>{item.title}</Text>
        <Text style={styles.date}>{item.release_date?.split('-')[0]}</Text>

    </Pressable>
  );


  return (
    <FlatList
      data={data}
      renderItem={renderItem}
      keyExtractor={(item) => item.id.toString()}
      horizontal={false}
      numColumns={numColumns}
      key={numColumns} // ✅ This forces FlatList to fully re-render if column count changes, In React (including React Native), the key prop is used to uniquely identify elements — especially in lists — so React knows how to efficiently re-render things.
      contentContainerStyle={styles.list}
      onEndReached={onEndReached}
      onEndReachedThreshold={0.5}
    />
  );
};


const styles = StyleSheet.create({
  list: {
    padding: 16,
  },
  posterContainer: {
    width: posterWidth,
    margin: posterMargin,
    marginLeft: 1,
    alignItems: 'center',
  },
  focusedPoster: {
    borderWidth: 3,
    borderColor: 'gold',
    borderRadius: 8,
  },
  poster: {
    width: '100%',
    height:200,
    borderRadius: 8,
  },
  title: {
    color: 'white',
    marginTop: 5,
    fontSize: 12,
    textAlign: 'center',
  },
  date: {
    color: 'gray',
    fontSize: 10,
  },
});
export default MoviePage;
