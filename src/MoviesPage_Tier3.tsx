// MoviesPage_Tier3.tsx

import React, { useRef, useState } from 'react';
// Make sure View is imported from react-native
import { Text, Image, FlatList, Pressable, View } from 'react-native';
import { useNavigation } from '@react-navigation/native';
// *** ADDED: Import navigation prop type helper and ParamList definition ***
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
// Note: Adjust the import path based on where you defined RootStackParamList
// Assuming it's defined in App_Tier1.tsx for now, or a central types file like '../../navigation/types'
import { RootStackParamList } from '../App_Tier1'; // <--- ADJUST THIS PATH AS NEEDED

import { DisplayItem, MediaPageProps } from './BrowseScreen_Tier2';

// *** ADDED: Define the specific navigation prop type for this screen context ***
type MoviesScreenNavigationProp = NativeStackNavigationProp<
  RootStackParamList,
  'Browse' // Assuming MoviesPage is rendered within the 'Browse' screen route context
>;


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
    // onEndReachedThreshold // Uncomment if passed as prop
}) => {

  const focusedIndex = useRef<number | null>(null);
  const [, forceUpdate] = useState(0);
  const triggerUpdate = () => forceUpdate((x) => x + 1);

  // *** ADDED: Get the typed navigation object ***
  const navigation = useNavigation<MoviesScreenNavigationProp>();


  // --- FIX IS HERE ---
  // Change Pressable to View in the type annotation
  const itemRefs = useRef<Array<View | null>>([]);
  // --- END OF FIX ---

  // *** ADDED: Handler for when a movie item is pressed ***
  const handlePressItem = (itemData: DisplayItem) => {
     // Navigate to OverviewPage, passing required ID and media_type,
     // plus basic info for initial display.
     console.log(`Navigating to Overview with Movie ID: ${itemData.id}`);
     navigation.navigate('Overview', {
        id: itemData.id,
        media_type: 'movie', // Identify the content type
        title: itemData.title,
        year: itemData.year,
        poster_url: itemData.poster_url,
     });
  };


  const renderItem = ({ item, index }: { item: DisplayItem; index: number }) => {
    // Don't render if we lack essential data (poster image) 
    if (!item.poster_url) return null;
    // Check if the current item is the one that has focus 
    const isFocused = focusedIndex.current === index;

    return (
      // The ref prop passes the underlying View instance to the callback
      <Pressable
            ref={(ref) => (itemRefs.current[index] = ref)} // This assignment is now type-correct
            style={[posterContainerStyle, isFocused && focusedPosterStyle]}
            onFocus={() => {
              focusedIndex.current = index; // Update the ref tracking the currently focused index
              triggerUpdate(); // Force a re-render to apply the focused style 
            }}
            onBlur={() => {
              setTimeout(() => {  // Use a slight delay with setTimeout. This helps prevent visual glitches 
                  if (focusedIndex.current === index) {  // Only clear the focus state if this *specific* item is still 
                        focusedIndex.current = null;
                        triggerUpdate();  // Force re-render to remove focused style 
                  }
              }, 0); // Minimal delay 
            }}
            // *** ADDED: Trigger navigation when the item is pressed ***
            onPress={() => handlePressItem(item)}
            // Set accessibility role (optional but good practice) 
            accessibilityRole="button" // Acts like a button 
            accessibilityLabel={`${item.title} (${item.year})`} // Describe for screen readers 
          >
            
            <Image source={{ uri: item.poster_url }} style={posterStyle} resizeMode="cover" />  {/* Display the poster image */}
            <Text style={titleTextStyle}>{item.title || 'N/A'}</Text>  {/* Display the title text */}
            <Text style={dateStyle}>{item.year || 'N/A'}</Text>  {/* Display the year text */}
      </Pressable>
    );
  };

  
  // Fallback UI Rendered when the data array is empty or not yet loaded
  // ... rest of the component remains the same
  if (!data || data.length === 0) {
     // This avoids rendering an empty FlatList and shows a user-friendly message 
     return (
       <View style={fallbackContainerStyle}>
         <Text style={fallbackTextStyle}>No Movies to display</Text>
       </View>
     );
   }

   // Main UI: Render the FlatList containing the grid of Movies
  return (
    <FlatList
      // ... FlatList props
      data={data} // The array of Movie items to render 
      renderItem={renderItem} // Function to render each item 
      // Generate a unique key for each item. Using 'movie-' prefix for potential debugging. 
      keyExtractor={(item, idx) => `movie-${item.id}-${idx}`}
      // Use the number of columns passed from BrowseScreen 
      numColumns={numColumns}
      // The 'key' prop here is essential: changing numColumns forces FlatList to re-render fully
      key={numColumns.toString()}
      // Apply container styling (like padding) passed from BrowseScreen 
      contentContainerStyle={listContentContainerStyle}
      // Callback function when scroll nears the end 
      onEndReached={onEndReached}
      // How far from the end (0.5 = 50% of visible length) to trigger onEndReached 
      onEndReachedThreshold={0.5} // Or use prop if passed: onEndReachedThreshold={onEndReachedThreshold}
      // --- Performance Optimizations for FlatList --- 
      windowSize={11} // Render items this many viewports ahead/behind the visible area 
      initialNumToRender={numColumns * 4} // Render enough items initially to fill ~4 rows 
      maxToRenderPerBatch={numColumns * 2} // Render items in batches of ~2 rows during scroll
      updateCellsBatchingPeriod={50} // Delay (ms) between rendering batches 
      removeClippedSubviews={true} // Optimization (mainly Android): removes views outside viewport from native hierarchy
      // --- End Performance Optimizations --- 
    />
  );
};

export default MoviesPage;