// TVShowsPage_Tier3.tsx

import React, { useRef, useState } from 'react';
// View is already imported, which is needed for the ref type fix below
import { Text, Image, StyleSheet, FlatList, Pressable, View } from 'react-native';
// Import the common types from BrowseScreen (or a dedicated types file)
import { DisplayItem, MediaPageProps } from './BrowseScreen_Tier2';

// Use the props defined in BrowseScreen
const TVShowsPage: React.FC<MediaPageProps> = ({
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
  fallbackTextStyle,
  onEndReachedThreshold,
  windowSize,
  initialNumToRender,
  maxToRenderPerBatch,
  updateCellsBatchingPeriod,
  removeClippedSubviews,
}) => {
  // Focus logic remains local to this list
  const focusedIndex = useRef<number | null>(null);
  // state used to force re-renders when focus changes to update styles
  const [, forceUpdate] = useState(0);
  const triggerUpdate = () => forceUpdate((x) => x + 1);

  // --- TYPE FIX ---
  // The ref attached to a Pressable usually points to the underlying View instance.
  // Therefore, the type for the ref array elements should be 'View | null', not 'Pressable | null'.
  const itemRefs = useRef<Array<View | null>>([]);
  // --- END TYPE FIX ---

  const renderItem = ({ item, index }: { item: DisplayItem; index: number }) => {
    // Don't render if we lack essential data (poster image)
    if (!item.poster_url) return null;

    // Check if the current item is the one that has focus
    const isFocused = focusedIndex.current === index;

    return (
      // Use Pressable for handling focus and press events
      <Pressable
        // Assign the DOM node (the underlying View) to the corresponding index in our refs array
        ref={(ref) => (itemRefs.current[index] = ref)}
        // Apply styles passed down from BrowseScreen. Apply focused style conditionally.
        style={[posterContainerStyle, isFocused && focusedPosterStyle]}
        // When this item receives focus...
        onFocus={() => {
          // Update the ref tracking the currently focused index
          focusedIndex.current = index;
          // Force a re-render to apply the focused style
          triggerUpdate();
        }}
        // When this item loses focus...
        onBlur={() => {
           // Use a slight delay with setTimeout. This helps prevent visual glitches
           // if focus moves quickly to another item within the same list.
           // It checks if the focus hasn't already moved to a *different* item
           // before nullifying the focusedIndex.
           setTimeout(() => {
               // Only clear the focus state if this *specific* item is still
               // marked as the focused one (meaning focus didn't jump elsewhere instantly)
               if (focusedIndex.current === index) {
                    focusedIndex.current = null;
                    triggerUpdate(); // Force re-render to remove focused style
               }
           }, 0); // Minimal delay
        }}
        // Set accessibility role (optional but good practice)
        accessibilityRole="button" // Acts like a button
        accessibilityLabel={`${item.title} (${item.year})`} // Describe for screen readers
      >
        {/* Display the poster image */}
        <Image source={{ uri: item.poster_url }} style={posterStyle} resizeMode="cover" />
        {/* Display the title text */}
        <Text style={titleTextStyle}>{item.title || 'N/A'}</Text>
        {/* Display the year text */}
        <Text style={dateStyle}>{item.year || 'N/A'}</Text>
      </Pressable>
    );
  };

  // Fallback UI Rendered when the data array is empty or not yet loaded
  if (!data || data.length === 0) {
     // This avoids rendering an empty FlatList and shows a user-friendly message
     return (
       <View style={fallbackContainerStyle}>
         <Text style={fallbackTextStyle}>No TV Shows to display</Text>
       </View>
     );
   }

  // Main UI: Render the FlatList containing the grid of TV Shows
  return (
    <FlatList
      data={data} // The array of TV show items to render
      renderItem={renderItem} // Function to render each item
      // Generate a unique key for each item. Using 'tv-' prefix for potential debugging.
      keyExtractor={(item, idx) => `tv-${item.id}-${idx}`}
      numColumns={numColumns} // Use the number of columns passed from BrowseScreen
      // The 'key' prop here is essential: changing numColumns forces FlatList to re-render fully
      key={numColumns.toString()}
      // Apply container styling (like padding) passed from BrowseScreen
      contentContainerStyle={listContentContainerStyle}
      onEndReached={onEndReached} // Callback function when scroll nears the end
      onEndReachedThreshold={onEndReachedThreshold} // How far from the end (0.5 = 50% of visible length) to trigger onEndReached
      // --- Performance Optimizations for FlatList ---
      windowSize={windowSize} // Render items this many viewports ahead/behind the visible area
      initialNumToRender={initialNumToRender} // Render enough items initially to fill ~4 rows
      maxToRenderPerBatch={maxToRenderPerBatch} // Render items in batches of ~2 rows during scroll
      updateCellsBatchingPeriod={updateCellsBatchingPeriod} // Delay (ms) between rendering batches
      removeClippedSubviews={removeClippedSubviews} // Optimization (mainly Android): removes views outside viewport from native hierarchy
      // --- End Performance Optimizations ---
    />
  );
};

// No local StyleSheet needed anymore - all styles are passed as props!

export default TVShowsPage;