// OverviewPage.tsx
import React from 'react';
import {
  View,
  Text,
  Image,
  StyleSheet,
  ScrollView,
  Pressable,
  FlatList,
  Platform,
  SafeAreaView, // *** ADDED: Import SafeAreaView ***
  StatusBar,      // *** ADDED: Import StatusBar ***
} from 'react-native';
import { useRoute, useNavigation, RouteProp } from '@react-navigation/native';
import LinearGradient from 'react-native-linear-gradient'; // *** ADDED: Import LinearGradient ***

// --- Color Palette ---
const COLORS = {
  background: 'rgb(13, 13, 13)',
  cardBackground: 'rgb(16, 15, 15)',
  textPrimary: 'rgb(248, 248, 248)',
  textSecondary: 'rgb(170, 170, 170)',
  accent: 'rgb(41, 98, 255)',
  // --- ADDED: Gradient Colors ---
  gradientBlue: 'rgb(41, 98, 255)',
  gradientGray: 'rgb(28, 28, 28)', // Using a darker gray for subtle effect
};

// --- Define the shape of the data we expect for cast ---
type CastMember = {
  id: number;
  name: string;
  profile_path: string | null; // URL path for actor image
  character?: string; // Optional: character name
};

// --- Define the shape of the route params ---
// This assumes you navigate using these param names. Adjust if needed.
type OverviewPageRouteParams = {
  Overview: {
    id: number;
    title: string;
    year: string;
    poster_url: string | null;
    rating?: number; // Make rating optional, TMDB might not always have it
    overview?: string;
    cast?: CastMember[]; // Expecting an array of cast members
    media_type: 'movie' | 'tv'; // Crucial for button logic
    // Add any other relevant data from TMDB/your backend here
    // backdrop_path?: string | null; // For a background image?
  };
};

// --- Define the props using the RouteProp type ---
type OverviewPageProps = {}; // This component uses route params, not direct props

const OverviewPage: React.FC<OverviewPageProps> = () => {
  const route = useRoute<RouteProp<OverviewPageRouteParams, 'Overview'>>();
  const navigation = useNavigation();

  // --- Add state for bookmark status (example) ---
  const [isBookmarked, setIsBookmarked] = React.useState(false); // Moved for clarity

  const {
    id, title, year, poster_url, rating, overview, cast = [], media_type,
  } = route.params;

  // --- Placeholder Functions ---
  const handlePlay = () => {
    console.log(`Play pressed for ${media_type} ID: ${id}`);
    // Navigation to Player Screen logic would go here
    // Example: navigation.navigate('Player', { contentId: id, type: media_type });
  };

  const handlePlayNewestEpisode = () => {
    console.log(`Play Newest Episode pressed for TV ID: ${id}`);
    // Logic to find newest episode and navigate to Player
  };

  const handleViewTrailer = () => {
    console.log(`View Trailer pressed for ${media_type} ID: ${id}`);
    // Logic to find and play trailer (might need another API call or data point)
  };

  const handleBookmark = () => {
    setIsBookmarked(prev => !prev);
    console.log(`Bookmark toggled for ${media_type} ID: ${id}`);
    // Add/remove bookmark logic here (update state/API)
  };

  const handleSearch = () => {
    console.log('Search icon pressed');
    // Navigate to Search Screen or show Search UI
  };

  const handleGoBack = () => {
    if (navigation.canGoBack()) {
      navigation.goBack();
    }
  };

  // --- Render Individual Cast Member ---
  const renderCastItem = ({ item }: { item: CastMember }) => (
      <View style={styles.castItem}>
        // Construct full URL for TMDB profile images
        <Image source={ item.profile_path ? { uri: `https://image.tmdb.org/t/p/w185${item.profile_path}`} : require('../../assets/ProfileIcon.png')} style={styles.castImage} />
        <Text style={styles.castName} numberOfLines={2}> {item.name} </Text>
        
        {/* Optional: Display character name
        {item.character && <Text style={styles.castCharacter} numberOfLines={1}>{item.character}</Text>}
        */}
      </View>
  );

  return (
    // *** MODIFIED: Use SafeAreaView as outermost container ***
    <SafeAreaView style={styles.safeArea}>
      <StatusBar barStyle="light-content" />

       {/* *** MODIFIED: Use LinearGradient for the background *** */}
      <LinearGradient
        colors={[COLORS.gradientBlue, COLORS.gradientGray]} // Define gradient colors
        start={{ x: 0, y: 0 }} // Gradient starts top-left
        end={{ x: 0.5, y: 0.6 }} // Ends more towards center-bottom (adjust for desired effect)
        style={styles.gradientContainer} // Apply flex: 1 style
      >
        {/* --- Original Content Starts Here --- */}

        {/* --- Top Bar --- */}
        {/* Keep the existing Top Bar styles - it sits ON TOP of the gradient */}
        <View style={styles.topBar}>
            <Pressable onPress={handleGoBack} style={styles.iconButton}>
              <Image source={require('../../assets/left_arrow.png')} style={{ backgroundColor: COLORS.textPrimary,  borderRadius: 13, marginRight: 5, width: 26, height: 26 }} />
            </Pressable>
            <View style={styles.topBarIconsRight}>
                <Pressable onPress={handleSearch} style={styles.iconButton}>
                  <Image source={require('../../assets/search.png')} style={{ backgroundColor: COLORS.accent,  borderRadius: 13, marginRight: 5, width: 26, height: 26 }} />
                </Pressable>
                <Pressable onPress={handleBookmark} style={styles.iconButton}>
                  <Image source={isBookmarked ? require('../../assets/bookmark_filled.png') : require('../../assets/bookmark.png')} style={{ backgroundColor: COLORS.accent,  borderRadius: 13, marginRight: 5, width: 26, height: 26 }} />
                  {/* Assumed you have bookmark_filled.png */}
                </Pressable>
            </View>
        </View>

        {/* --- ScrollView contains the rest of the content --- */}
        {/* Keep the existing ScrollView styles */}
        <ScrollView contentContainerStyle={styles.scrollContainer}>
            {/* --- Header Section (Poster + Details) --- */}
             {/* Keep existing header section */}
             <View style={styles.headerSection}>
                 {/* ... Poster Image ... */}
                 <Image source={ poster_url ? { uri: poster_url } : require('../../assets/poster_placeholder.png')} style={styles.poster}/>
                 {/* ... Header Details View ... */}
                 <View style={styles.headerDetails}>
                     {/* ... Title Text ... */}
                     <Text style={styles.title}>{title}</Text>
                    {/* ... Meta Row View ... */}
                    <View style={styles.metaRow}>
                         {/* ... Year Text ... */}
                         <Text style={styles.metaText}>{year}</Text>
                        {/* ... Rating conditional rendering ... */}
                        {rating !== undefined && rating > 0 && ( <> /* ... rating items ... */ </> )}
                    </View>
                    {/* ... Button Row View ... */}
                    <View style={styles.buttonRow}>



              {/* --- Play Button --- */}
              <Pressable
                // *** RESTORED: Correct style function ***
                style={({ pressed }) => [
                  styles.buttonBase,
                  styles.buttonPrimary,
                  pressed && styles.buttonPressed, // Apply pressed style conditionally
                ]}
                onPress={handlePlay}
              >
                 <Image source={require('../../assets/play_button.png')} style={{ marginRight: 5, width: 20, height: 20 }} />
                 <Text style={styles.buttonText}>Play</Text>
              </Pressable>


              {/* --- Play Newest Button (Conditional) --- */}
              {media_type === 'tv' && (
                <Pressable
                  // *** RESTORED: Correct style function ***
                  style={({ pressed }) => [
                    styles.buttonBase,
                    styles.buttonSecondary,
                    pressed && styles.buttonPressed, // Apply pressed style conditionally
                  ]}
                  onPress={handlePlayNewestEpisode}
                >
                  <Text style={styles.buttonText}>Play Newest</Text>
                </Pressable>
              )}
              

              {/* --- Trailer Button --- */}
              <Pressable
                // *** RESTORED: Correct style function ***
                style={({ pressed }) => [
                    styles.buttonBase,
                    styles.buttonSecondary,
                    pressed && styles.buttonPressed, // Apply pressed style conditionally
                  ]}
                onPress={handleViewTrailer}
               >
                  <Text style={styles.buttonText}>Trailer</Text>
               </Pressable>

            </View>
                 </View>
             </View>

            {/* --- Overview Section --- */}
             {/* Keep existing overview section */}
            {overview && ( <View style={styles.section}> /* ... */ </View> )}

            {/* --- Cast Section --- */}
             {/* Keep existing cast section */}
            {cast.length > 0 && ( <View style={styles.section}> /* ... */ </View> )}

        </ScrollView>

        {/* --- Original Content Ends Here --- */}

      </LinearGradient>
    </SafeAreaView> // *** ADDED: Closing SafeAreaView ***
  );
};

// --- Styles ---
const styles = StyleSheet.create({
  // *** ADDED: Style for SafeAreaView ***
  safeArea: {
    flex: 1,
    backgroundColor: COLORS.gradientGray, // Fallback background color
  },
  // *** MODIFIED: Renamed and repurposed screenContainer for gradient ***
  gradientContainer: {
    flex: 1, // Make gradient fill the safe area
    // REMOVED backgroundColor from here
    // REMOVED paddingTop from here (handled by SafeAreaView)
  },
  // --- Keep ALL OTHER original styles from your previous OverviewPage ---
  // styles.topBar, styles.topBarIconsRight, styles.iconButton, styles.scrollContainer,
  // styles.headerSection, styles.poster, styles.headerDetails, styles.title,
  // styles.metaRow, styles.metaText, styles.buttonRow, styles.buttonBase,
  // styles.buttonPrimary, styles.buttonSecondary, styles.buttonText, styles.buttonPressed,
  // styles.section, styles.sectionTitle, styles.overviewText,
  // styles.castListContainer, styles.castItem, styles.castImage, styles.castName,
  // styles.castCharacter
  // (Copying just a few below for context, but keep them all)
  topBar: {
    alignItems: 'center',
    // marginTop: -10, // Removed marginTop, let SafeArea handle top spacing
    paddingHorizontal: 15,
    paddingVertical: 8,
    justifyContent: 'space-between',
    height: 40,
    // width: '100%', // No longer needed if it's not absolute
    // backgroundColor: '#2c2c2e', // Keep or remove based on desired look over gradient
    flexDirection: 'row',
    position: 'absolute', // Make topBar float over the ScrollView
    top: Platform.OS === 'android' ? StatusBar.currentHeight : 0, // Position below status bar dynamically
    left: 0,
    right: 0,
    zIndex: 1, // Ensure it's above the ScrollView content
    backgroundColor: 'rgba(16, 15, 15, 0.6)', // Semi-transparent background
  },
  topBarIconsRight: {
    flexDirection: 'row',
  },
  iconButton: {
    padding: 8, // Clickable area
  },
  scrollContainer: {
    paddingBottom: 40,
    paddingTop: 50, // *** ADDED/ADJUSTED: Add padding to push content below absolute topBar ***
  },
  headerSection: {
    flexDirection: 'row',
    paddingHorizontal: 20,
   // paddingTop: 20, // Removed, handled by scrollContainer paddingTop
    marginBottom: 20,
    alignItems: 'flex-start', // Align items to the top
  },
  poster: {
    width: 120,
    height: 180, // Adjust aspect ratio as needed (120 * 1.5)
    borderRadius: 8,
    backgroundColor: COLORS.cardBackground, // Placeholder color
    marginRight: 15,
  },
  headerDetails: {
    flex: 1, // Take remaining width
    paddingTop: 5, // Align text slightly below poster top
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: COLORS.textPrimary,
    marginBottom: 8,
  },
  metaRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 15,
  },
  metaText: {
    fontSize: 14,
    color: COLORS.textSecondary,
  },
  buttonRow: {
    flexDirection: 'row',
    marginTop: 10, // Spacing above buttons
    flexWrap: 'wrap', // Allow buttons to wrap on smaller screens if needed
  },
  buttonBase: {
    flexDirection: 'row',
    paddingVertical: 10,
    paddingHorizontal: 15,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 10,
    marginBottom: 10, // Spacing for wrapping
    minWidth: 80, // Minimum button width
  },
  buttonPrimary: {
     // Using the accent color directly for the primary button
     backgroundColor: COLORS.accent, // Blue for primary action
     // Or use cardBackground and accent for text/icon
     // backgroundColor: COLORS.cardBackground,
  },
  buttonSecondary: {
     backgroundColor: COLORS.cardBackground, // Darker grey for secondary
  },
  buttonText: {
     color: COLORS.textPrimary,
     fontSize: 14,
     fontWeight: '600',
     // If using cardBackground for primary button, make text accent color:
     // color: COLORS.accent,
  },
  buttonPressed: {
    opacity: 0.7, // Visual feedback on press
  },
  section: {
    paddingHorizontal: 20,
    marginBottom: 25,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: COLORS.textPrimary,
    marginBottom: 12,
  },
  overviewText: {
    fontSize: 14,
    color: COLORS.textSecondary,
    lineHeight: 20,
  },
  castListContainer: {
    paddingLeft: 0, // Align first item with section padding
  },
  castItem: {
    marginRight: 15,
    width: 80, // Fixed width for cast items
    alignItems: 'center',
  },
  castImage: {
    width: 70,
    height: 70,
    borderRadius: 35, // Circular images
    backgroundColor: COLORS.cardBackground, // Placeholder
    marginBottom: 6,
  },
  castName: {
    fontSize: 12,
    color: COLORS.textPrimary,
    textAlign: 'center',
  },
  castCharacter: { // Optional style for character name
    fontSize: 10,
    color: COLORS.textSecondary,
    textAlign: 'center',
  },
});

export default OverviewPage;