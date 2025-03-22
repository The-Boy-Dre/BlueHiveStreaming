export const parser = '@babel/eslint-parser';
export const parserOptions = {
  requireConfigFile: false, // Disable Babel config file checking
  babelOptions: {
    presets: ['module:@react-native/babel-preset'],
    plugins: ['react-native-reanimated/plugin'],
  },
};



