//! This file sets up your navigation using React Navigation:


import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import HomeScreen from './HomeScreen';
import DetailsScreen from './DetailsScreen';

type RootStackParamList = {
  Home: undefined;
  Details: { detailId: string };
};

const Stack = createStackNavigator<RootStackParamList>();

const App = () => {
  return (
    
    <NavigationContainer>
      <p>
      </p>
      <Stack.Navigator initialRouteName="Home">
        <Stack.Screen name="Home" component={HomeScreen} />
        <Stack.Screen name="Details" component={DetailsScreen} />
      </Stack.Navigator>
    </NavigationContainer>
  );
};

export default App;
