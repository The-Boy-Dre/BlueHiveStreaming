import React, { useRef, useState } from 'react';
import { View, TextInput, StyleSheet, Text, Image, Pressable } from 'react-native';

// Accepts an onTabChange prop to notify the parent BrowseScreen component of tab switches
const OptionsBar = ({ onTabChange }: { onTabChange: (tab: 'Movies' | 'TV Series') => void }) => {
  const [activeTab, setActiveTab] = useState<'Movies' | 'TV Series'>(); // You would keep the internal activeTab state in OptionsBar if you wanted the OptionsBar itself to visually indicate which tab is currently selected, independently of focus.
  const focused = useRef<string | null>(null); // tracks which UI item is currently focused
  const [, forceUpdate] = useState(0);
  const triggerUpdate = () => forceUpdate((x) => x + 1);
  const searchInputRef = useRef<TextInput>(null);

  return (
    <View style={styles.container}>

      {/* Menu Button */}
      <Pressable onPress={() => console.log('Open popup')} onFocus={() => { focused.current = 'menu'; triggerUpdate(); }} onBlur={() => { focused.current = null; triggerUpdate(); }} style={[styles.menuButton, focused.current === 'menu' && styles.focusedOutline]}>
        <Text style={styles.menuIcon}>≡</Text>
      </Pressable>

      {/* Search Input */}
      <Pressable onPress={() => searchInputRef.current?.focus()} hasTVPreferredFocus={true} onFocus={() => { focused.current = 'search'; triggerUpdate(); }} onBlur={() => { focused.current = null; triggerUpdate(); }} style={[styles.searchWrapper, focused.current === 'search' && styles.searchFocused]}>
        <TextInput ref={searchInputRef} style={styles.searchInput} placeholder="Search" placeholderTextColor="#aaa" returnKeyType="search" />
      </Pressable>

      {/* Movies Tab */}
      <Pressable onPress={() => { setActiveTab('Movies'); onTabChange('Movies'); }} onFocus={() => { focused.current = 'movies'; triggerUpdate(); }} onBlur={() => { focused.current = null; triggerUpdate(); }}>
        <Text style={[styles.whiteTab, focused.current === 'movies' && styles.goldTab]}>Movies</Text>
      </Pressable>

      {/* TV Series Tab */}
      <Pressable onPress={() => { setActiveTab('TV Series'); onTabChange('TV Series'); }} onFocus={() => { focused.current = 'tv'; triggerUpdate(); }} onBlur={() => { focused.current = null; triggerUpdate(); }}>
        <Text style={[styles.whiteTab, focused.current === 'tv' && styles.goldTab]}>TV Shows</Text>
      </Pressable>

      {/* Avatar/Profile Icon */}
      <Pressable onFocus={() => { focused.current = 'avatar'; triggerUpdate(); }} onBlur={() => { focused.current = null; triggerUpdate(); }}>
        <Image source={require('../assets/ProfileIcon.png')} style={[styles.avatar, focused.current === 'avatar' && styles.avatarSelected]} />
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
