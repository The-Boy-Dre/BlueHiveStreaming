import React from 'react';
import { StyleSheet, View, Text, SafeAreaView, StatusBar } from 'react-native';
// 1. Import the LinearGradient component
import LinearGradient from 'react-native-linear-gradient';

// --- Your Chosen Colors ---
// Let's define the "bright blue" and a suitable "gray"
const GRADIENT_COLORS = {
    // A nice vibrant blue shade like the accent you used before
    brightBlue: 'rgb(41, 98, 255)',
    // A medium-dark gray that provides a soft contrast in a dark theme
    softGray: 'rgb(45, 45, 45)', // Hex: #2d2d2d
    // Or maybe an even darker charcoal for a subtler effect: 'rgb(28, 28, 28)' // Hex: #1c1c1c
};

// Example component using the gradient background
const GradientBackgroundScreen = () => {
  return (
    // SafeAreaView ensures content isn't hidden by notches/status bars
    <SafeAreaView style={styles.safeArea}>
      <StatusBar barStyle="light-content" />

      {/* 2. Use LinearGradient as the main container */}
      <LinearGradient
        // 3. Define the colors for the gradient stops
        colors={[GRADIENT_COLORS.brightBlue, GRADIENT_COLORS.softGray]}

        // 4. Define the direction (start/end points)
        //    {x: 0, y: 0} is top-left, {x: 1, y: 1} is bottom-right
        //    This creates a diagonal gradient from top-left blue to bottom-right gray
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}

        // You can also experiment with other directions:
        // Top to bottom: start={{ x: 0.5, y: 0 }} end={{ x: 0.5, y: 1 }}
        // More top-heavy blue: start={{ x: 0.5, y: 0 }} end={{ x: 0.5, y: 0.7 }}

        // 5. Style the gradient view itself (make it fill the screen)
        style={styles.gradientContainer}
      >
        {/* --- Your Actual Screen Content Goes Here --- */}
        {/* Example Content */}
        <View style={styles.content}>
          <Text style={styles.text}>Your App Content Here</Text>
          {/* Add buttons, lists, etc. */}
        </View>
        {/* --- End of Screen Content --- */}

      </LinearGradient>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    // Set a fallback background color in case the gradient takes time to render
    backgroundColor: GRADIENT_COLORS.softGray,
  },
  gradientContainer: {
    flex: 1, // Make the gradient fill the SafeAreaView
    justifyContent: 'center', // Example: center content vertically
    alignItems: 'center', // Example: center content horizontally
  },
  content: {
    // Styles for your content wrapper if needed
    padding: 20,
  },
  text: {
    fontSize: 20,
    color: '#FFFFFF', // White text usually looks good on dark gradients
    textAlign: 'center',
  },
});

export default GradientBackgroundScreen;