import React, { useState } from 'react';
import { View, TextInput, StyleSheet, TouchableOpacity, Text, Image } from 'react-native';






const OptionsBar = () => {

  const [activeTab, setActiveTab] = useState<'Movies' | 'TV Series'>('Movies');

  return (
    <View style={styles.container}>
          <TouchableOpacity style={styles.menuButton} onPress={() => console.log('Open popup')}>
            {/* Placeholder icon/text; you can replace with an actual icon component */}
            <Text style={styles.menuIcon}>≡</Text>
          </TouchableOpacity>

          <TextInput
            style={styles.searchInput}
            placeholder="Search"
            placeholderTextColor="#aaa"
          />

          <View style={styles.rightContainer}>

            <TouchableOpacity onPress={() => setActiveTab('Movies')}>
              <Text style={activeTab === 'Movies' ? styles.activeTab : styles.tab}>Movies</Text>
            </TouchableOpacity>

            <TouchableOpacity onPress={() => setActiveTab('TV Series')}>
              <Text style={activeTab === 'TV Series' ? styles.activeTab : styles.tab}>TV Series</Text>
            </TouchableOpacity>

            <Image
              source={{ uri: 'https://via.placeholder.com/30' }}
              style={styles.avatar}
            />
          </View>
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
  searchInput: {
    flex: 1,
    backgroundColor: '#3a3a3c',
    borderRadius: 10,
    height: 30,
    paddingHorizontal: 15,
    paddingTop: 5,    
    paddingBottom: 6,  
    color: 'white',
    marginHorizontal: 10,
    fontSize: 12, 
  },
  rightContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  activeTab: {
    color: 'white',
    marginRight: 15,
    fontWeight: 'bold',
  },
  tab: {
    color: '#aaa',
    marginRight: 15,
  },
  avatar: {
    width: 30,
    height: 30,
    borderRadius: 15,
  },
});

export default OptionsBar;
