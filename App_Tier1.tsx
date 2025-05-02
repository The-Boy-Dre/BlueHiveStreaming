
import React from 'react';
import { StatusBar, useColorScheme, View } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';

// --- Import Screens ---
import BrowseScreen from './src/BrowseScreen_Tier2';
import OverviewPage from './src/NestedPages/OverviewPage'; // *** ADDED: Import OverviewPage ***

// --- Define Param List for Type Safety ---
// Describe all screens in this stack and the parameters they expect.
// 'undefined' means the screen expects no parameters.
export type RootStackParamList = {
  Browse: undefined; // Your main browse screen
  // *** ADDED: Definition for Overview screen and its expected params ***
  Overview: {
    // Required params:
    id: number;
    media_type: 'movie' | 'tv';
    // Optional params (useful for initial display while full details load):
    title?: string;
    year?: string;
    poster_url?: string | null;
    // Add any other simple params Overview might receive directly
  };
  // Add other screens like 'Player' or 'Search' here later if needed
  // Player: { contentId: number, streamUrl: string };
};

// --- Create the Stack Navigator with the defined Param List ---
const Stack = createStackNavigator<RootStackParamList>();


function App(): React.JSX.Element {
  const isDarkMode = useColorScheme() === 'dark';
  // Use a consistent background color (e.g., black) instead of dynamic Colors
  const backgroundColor = 'rgb(13, 13, 13)'; // Match OverviewPage background

  return (
    // Use flex: 1 on the main View to ensure it takes full screen height
    <View style={{ flex: 1, backgroundColor }}>
      <StatusBar
        barStyle={'light-content'} // Force light content for dark background
        backgroundColor={backgroundColor}
      />
      {/* NavigationContainer wraps the entire navigation structure */}
      <NavigationContainer>
        {/* Stack.Navigator manages the stack of screens */}
        <Stack.Navigator initialRouteName="Browse" screenOptions={{ headerShown: false }}> 
            <Stack.Screen name="Browse" component={BrowseScreen}/>
            {/* options={{ headerShown: false }}  Already set globally by screenOptions */}
            
            <Stack.Screen
              name="Overview" // Matches the key in RootStackParamList
              component={OverviewPage} // Use the imported component
              // options={{ headerShown: false }} // Already set globally
             />
        </Stack.Navigator>
      </NavigationContainer>
    </View>
  );
}

export default App;