// import React from 'react';
// import { NavigationContainer } from '@react-navigation/native';
// import { createStackNavigator } from '@react-navigation/stack';
// import HomeScreen from '../src/HomeScreen';
// import DetailsScreen from '../src/DetailsScreen';
// import { RootStackParamList } from '../src/types/navigation';

// const Stack = createStackNavigator<RootStackParamList>();

// const App = () => {
//   return (
//     <NavigationContainer>
//       <Stack.Navigator initialRouteName="Home">
//         <Stack.Screen
//           name="Home"
//           component={HomeScreen}
//           options={{ title: 'Home' }}
//         />
//         <Stack.Screen
//           name="Details"
//           component={DetailsScreen}
//           options={{ title: 'Details' }}
//         />
//       </Stack.Navigator>
//     </NavigationContainer>
//   );
// };

// export default App;



import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import HomeScreen from '../src/HomeScreen';
import DetailsScreen from '../src/DetailsScreen';

type RootStackParamList = {
  Home: undefined;
  Details: { detailId: string };
};

const Stack = createStackNavigator<RootStackParamList>();

const App = () => {
  return (
    <NavigationContainer>
      <Stack.Navigator initialRouteName="Home">
        <Stack.Screen name="Home" component={HomeScreen} />
        <Stack.Screen name="Details" component={DetailsScreen} />
      </Stack.Navigator>
    </NavigationContainer>
  );
};

export default App;
