// OverviewPage.tsx
import React from 'react';
import { View, Text, Image, StyleSheet, ScrollView, Pressable, FlatList, Platform,} from 'react-native';
import { useRoute, useNavigation, RouteProp } from '@react-navigation/native';

// --- Color Palette ---
const COLORS = {
  background: 'rgb(13, 13, 13)',         // Very dark grey/off-black
  cardBackground: 'rgb(16, 15, 15)',     // Slightly lighter grey (for buttons)
  textPrimary: 'rgb(248, 248, 248)',    // White/Off-white
  textSecondary: 'rgb(170, 170, 170)',  // Grey for secondary text
  accent: 'rgb(41, 98, 255)',           // Blue accent (icons, focus)
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

  // Extract data from route params
  const {
    id,
    title,
    year,
    poster_url,
    rating,
    overview,
    cast = [], // Default to empty array if cast is not provided
    media_type,
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
    <View style={styles.screenContainer}>
      {/* --- Top Bar --- */}
      <View style={styles.topBar}>
            <Pressable onPress={handleGoBack} style={styles.iconButton}>
              <Image source={require('../../assets/left_arrow.png')} style={{ backgroundColor: COLORS.textPrimary,  borderRadius: 13, marginRight: 5, width: 26, height: 26 }} />
            </Pressable>

            <View style={styles.topBarIconsRight}>
                <Pressable onPress={handleSearch} style={styles.iconButton}>
                  <Image source={require('../../assets/search.png')} style={{ backgroundColor: COLORS.accent,  borderRadius: 13, marginRight: 5, width: 26, height: 26 }} />
                </Pressable>
                {/* Add isBookmarked state later */}
                <Pressable onPress={handleBookmark} style={styles.iconButton}>
                  <Image source={require('../../assets/bookmark.png')} style={{ backgroundColor: COLORS.accent,  borderRadius: 13, marginRight: 5, width: 26, height: 26 }} />
                  {/* Use 'bookmark' icon if it IS bookmarked */}
                </Pressable>
            </View>
      </View>

      <ScrollView contentContainerStyle={styles.scrollContainer}>
        {/* --- Header Section (Poster + Details) --- */}
        <View style={styles.headerSection}>
          <Image source={ poster_url ? { uri: poster_url } : require('../../assets/poster_placeholder.png')} style={styles.poster}/>
          <View style={styles.headerDetails}>
            <Text style={styles.title}>{title}</Text>
            <View style={styles.metaRow}>
              <Text style={styles.metaText}>{year}</Text>
              {rating !== undefined && rating > 0 && ( 
                <>
                  <Text style={[styles.metaText, { marginHorizontal: 8 }]}>|</Text>
                  <Image source={require('../../assets/star.png')} style={{ backgroundColor: 'gold',  borderRadius: 13, marginRight: 5, width: 16, height: 16 }} />
                  <Text style={[styles.metaText, { marginLeft: 4 }]}>
                    {rating.toFixed(1)}
                  </Text>
                </>
              )}
            </View>


            {/* --- Action Buttons --- */}
            <View style={styles.buttonRow}>
              <Pressable style={({ pressed }) => [ styles.buttonBase, styles.buttonPrimary, pressed && styles.buttonPressed, ]} onPress={handlePlay}>
                 <Image source={require('../../assets/play_button.png')} style={{ marginRight: 5, width: 20, height: 20 }} />
                 <Text style={styles.buttonText}>Play</Text>
              </Pressable>

              {media_type === 'tv' && (
                <Pressable
                  style={({ pressed }) => [
                    styles.buttonBase,
                    styles.buttonSecondary,
                    pressed && styles.buttonPressed,
                  ]}
                  onPress={handlePlayNewestEpisode}
                >
                  <Text style={styles.buttonText}>Play Newest</Text>
                </Pressable>
              )}

              {/* Consider adding Trailer button if data available */}
              <Pressable
                style={({ pressed }) => [
                    styles.buttonBase,
                    styles.buttonSecondary,
                    pressed && styles.buttonPressed,
                  ]}
                onPress={handleViewTrailer}
               >
                  <Text style={styles.buttonText}>Trailer</Text>
               </Pressable>

            </View>
          </View>
        </View>



        {/* --- Overview Section --- */}
        {overview && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Overview</Text>
            <Text style={styles.overviewText}>{overview}</Text>
          </View>
        )}

        {/* --- Cast Section --- */}
        {cast.length > 0 && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Cast</Text>
            <FlatList
              data={cast}
              renderItem={renderCastItem}
              keyExtractor={(item) => item.id.toString()}
              horizontal={true}
              showsHorizontalScrollIndicator={false}
              contentContainerStyle={styles.castListContainer}
            />
          </View>
        )}

        {/* Add Seasons / See Also sections here later if needed */}

      </ScrollView>
    </View>
  );
};

// --- Styles ---
const styles = StyleSheet.create({
  screenContainer: {
    flex: 1,
    backgroundColor: 'rgb(17, 17, 22)',
    paddingTop: Platform.OS === 'android' ? 10 : 40, // Adjust status bar spacing
  },
  topBar: {
    alignItems: 'center',
    marginTop: -10,
    paddingHorizontal: 15,
    paddingVertical: 8,
    justifyContent: 'space-between',
    height: 40,
    width: '100%',
    backgroundColor: '#2c2c2e',
    flexDirection: 'row',
  },
  topBarIconsRight: {
    flexDirection: 'row',
  },
  iconButton: {
    padding: 8, // Clickable area
  },
  scrollContainer: {
    paddingBottom: 40, // Space at the bottom
  },
  headerSection: {
    flexDirection: 'row',
    paddingHorizontal: 20,
    paddingTop: 20, // Space below top bar
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