import { StackNavigationProp } from '@react-navigation/stack';

export type RootStackParamList = {
  Home: undefined;
  Details: { message: string };
};

export type HomeScreenNavigationProp = StackNavigationProp<RootStackParamList, 'Home'>;
