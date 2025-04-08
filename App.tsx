/**
 * Sample React Native App
 * https://github.com/facebook/react-native
 *
 * @format
 */

import React from 'react';
import type {PropsWithChildren} from 'react';
import OptionsBar from './src/OptionsBar';
import { SafeAreaView, ScrollView,StatusBar, StyleSheet, Text,useColorScheme, View,} from 'react-native';
import { Colors, DebugInstructions, LearnMoreLinks, ReloadInstructions,} from 'react-native/Libraries/NewAppScreen';
import { NavigationContainer } from '@react-navigation/native';
import HomeScreen from './src/HomeScreen';
import DetailsScreen from './src/DetailsScreen';
import { createStackNavigator } from '@react-navigation/stack';


type SectionProps = PropsWithChildren<{
  title: string;
}>;

function Section({children, title}: SectionProps): React.JSX.Element {
  const isDarkMode = useColorScheme() === 'dark';
  return (
    <View style={styles.sectionContainer}>
      <Text
        style={[
          styles.sectionTitle,
          {
            color: isDarkMode ? Colors.white : Colors.black,
          },
        ]}>
        {title}
      </Text>
      <Text
        style={[
          styles.sectionDescription,
          {
            color: isDarkMode ? Colors.light : Colors.dark,
          },
        ]}>
        {children}
      </Text>
    </View>
  );
}

type RootStackParamList = {
  Home: undefined;
  Details: { detailId: string };
};

const Stack = createStackNavigator<RootStackParamList>();






function App(): React.JSX.Element {
  const isDarkMode = useColorScheme() === 'dark';

  const backgroundStyle = {
    backgroundColor: isDarkMode ? Colors.darker : Colors.lighter,
  };

  return (
    <SafeAreaView style={backgroundStyle}>
      <StatusBar barStyle={isDarkMode ? 'light-content' : 'dark-content'} backgroundColor={backgroundStyle.backgroundColor} />
       
      <ScrollView contentInsetAdjustmentBehavior="automatic" style={backgroundStyle}>
        
        <View style={{ backgroundColor: isDarkMode ? Colors.black : Colors.white, }}>

            {/* <OptionsBar/> */}

            {/* <View style={{ height: '8%', backgroundColor: 'red'}} />
            <View style={{ height: '10%', backgroundColor: 'darkorange'}} />
            <View style={{ height: '12%', backgroundColor: 'green' }} /> */}

            {/* <Section title="Step One">
              Edit <Text style={styles.highlight}>App.tsx</Text> to change this
              screen and then come back to see your edits.
            </Section>
            <Section title="See Your Changes">
              <ReloadInstructions />
            </Section>
            <Section title="Debug">
              <DebugInstructions />
            </Section>
            <Section title="Learn More">
              Read the docs to discover what to do next:
            </Section>

            <LearnMoreLinks /> */}

          <NavigationContainer>
                <Stack.Navigator initialRouteName="Home">
                <Stack.Screen name="Home" component={OptionsBar} />
                  {/* <Stack.Screen name="Home" component={HomeScreen} />
                  <Stack.Screen name="Details" component={DetailsScreen} /> */}
                </Stack.Navigator>
          </NavigationContainer>


        </View>

      </ScrollView>
    </SafeAreaView>
  );
}


const styles = StyleSheet.create({
  sectionContainer: {
    marginTop: 32,
    paddingHorizontal: 24,
  },
  sectionTitle: {
    fontSize: 24,
    fontWeight: '600',
  },
  sectionDescription: {
    marginTop: 8,
    fontSize: 18,
    fontWeight: '400',
  },
  highlight: {
    fontWeight: '700',
  },
});

export default App;
