import React, { useRef, useState } from 'react';
import { Text, Image, StyleSheet, FlatList, Pressable, Dimensions, View } from 'react-native';

const IMAGE_BASE_URL = 'https://image.tmdb.org/t/p/w500';

const screenWidth = Dimensions.get('window').width;
const posterMargin = 8 // adjust as needed
const numColumns = 6;   // your desired number of columns
const posterWidth = (screenWidth - posterMargin * 2 * numColumns) / numColumns;

export type Movie = {
  first_air_date: string;
  name: string;
  id: number;
  title: string;
  release_date: string;
  poster_path: string | null;
};

type Props = {
  data: Movie[];
  onEndReached: () => void;
};

const MoviePage: React.FC<Props> = ({ data, onEndReached }) => {
  // const [focusedIndex, setFocusedIndex] = useState<number | null>(null); // Naviagtion 
  const focusedIndex = useRef<number | null>(null);
  const [, forceUpdate] = useState(0);
  const triggerUpdate = () => forceUpdate((x) => x + 1);

  const itemRefs = useRef<Array<any>>([]);

  const renderItem = ({ item, index }: { item: Movie; index: number }) => {
    if (!item.poster_path) return null; // ⛔ Skip rendering if poster path is missing

    const isFocused = focusedIndex.current === index;

    return (
      <Pressable
        ref={(ref) => {
          itemRefs.current[index] = ref;
        }}
        focusable={true}
        nextFocusLeft={index > 0 ? itemRefs.current[index - 1] : undefined}
        nextFocusRight={index < data.length - 1 ? itemRefs.current[index + 1] : undefined}
        style={[
          styles.posterContainer,
          isFocused && styles.focusedPoster,
        ]}
        onFocus={() => {
          focusedIndex.current = index;
          triggerUpdate();
        }}
        onBlur={() => {
          focusedIndex.current = null;
          triggerUpdate();
        }}
      >
        <Image
          source={{ uri: IMAGE_BASE_URL + item.poster_path }}
          style={styles.poster}
          resizeMode="cover"
        />
        <Text style={styles.title}>
          {item.title || item.name || 'N/A'}
        </Text>
        <Text style={styles.date}>
          {(item.release_date || item.first_air_date)?.split('-')[0] || 'N/A'}
        </Text>
      </Pressable>
    );
  };

  // 🧪 Fallback UI when no data is available (avoids blank screens)
  if (!data || data.length === 0) {
    return (
      <View style={styles.fallbackContainer}>
        <Text style={styles.fallbackText}>No movies to display</Text>
      </View>
    );
  }

  return (
    <FlatList
      data={data}
      renderItem={renderItem}
      keyExtractor={(item, idx) => (item.id ? item.id.toString() + '-' + idx.toString() : idx.toString())} // ✅ Combine ID and index for guaranteed uniqueness
      horizontal={false}
      numColumns={numColumns}
      key={numColumns}  // ✅ This forces FlatList to fully re-render if column count changes, In React (including React Native), the key prop is used to uniquely identify elements — especially in lists — so React knows how to efficiently re-render things.
      contentContainerStyle={styles.list}
      onEndReached={onEndReached}
      onEndReachedThreshold={0.5}

      // ✅ Performance tuning
      windowSize={5} // how many items outside of render window to preload
      initialNumToRender={20} // how many items to render initially
      removeClippedSubviews={true} // remove off-screen items from memory (Android only)
      maxToRenderPerBatch={10} // number of items to render per batch
      updateCellsBatchingPeriod={50} // time (ms) between rendering batches
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
    height: 200,
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
  fallbackContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 40,
  },
  fallbackText: {
    color: 'white',
    fontSize: 16,
  },
});

export default MoviePage;
