// MoviesPage_Tier3.tsx (and TVShowsPage_Tier3.tsx)

import React, { useRef, useState } from 'react';
// Make sure View is imported from react-native
import { Text, Image, FlatList, Pressable, View } from 'react-native';
import { DisplayItem, MediaPageProps } from './BrowseScreen_Tier2';

const MoviesPage: React.FC<MediaPageProps> = ({
  data,
  onEndReached,
  numColumns,
  listContentContainerStyle,
  posterContainerStyle,
  focusedPosterStyle,
  posterStyle,
  titleTextStyle,
  dateStyle,
  fallbackContainerStyle,
  fallbackTextStyle
}) => {
  const focusedIndex = useRef<number | null>(null);
  const [, forceUpdate] = useState(0);
  const triggerUpdate = () => forceUpdate((x) => x + 1);

  // --- FIX IS HERE ---
  // Change Pressable to View in the type annotation
  const itemRefs = useRef<Array<View | null>>([]);
  // --- END OF FIX ---


  const renderItem = ({ item, index }: { item: DisplayItem; index: number }) => {
    if (!item.poster_url) return null;
    const isFocused = focusedIndex.current === index;

    return (
      // The ref prop passes the underlying View instance to the callback
      <Pressable
        ref={(ref) => (itemRefs.current[index] = ref)} // This assignment is now type-correct
        style={[posterContainerStyle, isFocused && focusedPosterStyle]}
        onFocus={() => {
          focusedIndex.current = index;
          triggerUpdate();
        }}
        onBlur={() => {
           setTimeout(() => {
               if (focusedIndex.current === index) {
                    focusedIndex.current = null;
                    triggerUpdate();
               }
           }, 0);
        }}
      >
        <Image source={{ uri: item.poster_url }} style={posterStyle} resizeMode="cover" />
        <Text style={titleTextStyle}>{item.title || 'N/A'}</Text>
        <Text style={dateStyle}>{item.year || 'N/A'}</Text>
      </Pressable>
    );
  };

  // ... rest of the component remains the same
  if (!data || data.length === 0) {
     return (
       <View style={fallbackContainerStyle}>
         <Text style={fallbackTextStyle}>No Movies to display</Text>
       </View>
     );
   }

  return (
    <FlatList
      // ... FlatList props
      data={data}
      renderItem={renderItem}
      keyExtractor={(item, idx) => `movie-${item.id}-${idx}`}
      numColumns={numColumns}
      key={numColumns.toString()}
      contentContainerStyle={listContentContainerStyle}
      onEndReached={onEndReached}
      onEndReachedThreshold={0.5}
      windowSize={11}
      initialNumToRender={numColumns * 4}
      maxToRenderPerBatch={numColumns * 2}
      updateCellsBatchingPeriod={50}
      removeClippedSubviews={true}
    />
  );
};

export default MoviesPage;