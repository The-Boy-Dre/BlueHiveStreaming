import React, { useRef, useState } from 'react';
import {  View, TextInput, StyleSheet, Text,  Image, Pressable} from 'react-native';


const OptionsBar = () => {
  const [activeTab, setActiveTab] = useState<'Movies' | 'TV Series'>(); // ensures that activeTab can only be either of two string values, 'movies' or 'tvshows'
  const [focused, setFocused] = useState<string | null>(null); //This initializes a state value with a type annotation. The state can hold either a string or null. By passing null as the initial value, you're indicating that the default state is null
  const searchInputRef = useRef<TextInput>(null);
  

  return (
    <View style={styles.container}>

        <Pressable  onPress={() => console.log('Open popup')} onFocus={() => setFocused('menu')} onBlur={() => setFocused(null)} style={[styles.menuButton, focused === 'menu' && styles.focusedOutline]}>
            <Text style={styles.menuIcon}>≡</Text>
        </Pressable>

        {/* Since you're working on Fire TV navigation with focus borders, Pressable is the right choice for you! Introduced in React Native 0.63+  Handles TV remote focus (perfect for your Fire TV app).*/}
        <Pressable  onPress={() => searchInputRef.current?.focus()} hasTVPreferredFocus={true} onFocus={() => setFocused('search')} onBlur={() => setFocused(null)} style={[styles.searchWrapper,focused === 'search' && styles.searchFocused]}>
            <TextInput ref={searchInputRef} style={styles.searchInput}  placeholder="Search"  placeholderTextColor="#aaa"  returnKeyType="search" />
        </Pressable>
  
            <Pressable onFocus={() => setFocused('movies')} onBlur={() => setFocused(null)} onPress={() => setActiveTab('Movies')}>    
                <Text style={[styles.whiteTab, focused === 'movies' && styles.goldTab]}> Movies </Text>  
            </Pressable>

            <Pressable onFocus={() => setFocused('tv')}  onBlur={() => setFocused(null)} onPress={() => setActiveTab('TV Series')}>   
               <Text style={[styles.whiteTab, focused === 'tv' && styles.goldTab]}> TV Series </Text>  
            </Pressable>

            <Pressable  onFocus={() => setFocused('avatar')} onBlur={() => setFocused(null)} >
                <Image source={require('../assets/ProfileIcon.png')} style={[ styles.avatar, focused === 'avatar' && styles.avatarSelected ]} />
            </Pressable>

    </View>
  );
};





const styles = StyleSheet.create({
  container: {
    height: 50,
    width: '100%',
    backgroundColor: '#2c2c2e',
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 10,
    justifyContent: 'space-between',
  },
  menuButton: {
    padding: 10,
  },
  menuIcon: {
    fontSize: 24,
    color: 'white',
  },
  searchWrapper: {
    flex: 1,
    marginHorizontal: 10,
    borderRadius: 10,
    backgroundColor: '#3a3a3c',
  },
  searchInput: {
    height: 30,
    paddingHorizontal: 15,
    paddingTop: 5,
    paddingBottom: 6,
    color: 'white',
    fontSize: 12,
  },
  searchFocused: {
    borderColor: 'gold',
    borderWidth: 2,
  },
  goldTab: {
    color: 'gold',
    marginRight: 15,
    fontWeight: 'bold',
  },
  whiteTab: {
    color: 'white',
    marginRight: 15,
  },
  avatar: {
    width: 30,
    height: 30,
    borderRadius: 15,
  },
  avatarSelected: {
    width: 30,
    height: 30,
    borderWidth: 2,
    borderColor: 'gold',
  },
  focusedOutline: {
    borderWidth: 2,
    borderColor: 'gold',
    borderRadius: 10,
  },
});

export default OptionsBar;
