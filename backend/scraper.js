// backend/scraper.js
const axios = require('axios');
const puppeteer = require('puppeteer');
const cheerio = require('cheerio');
const { LRUCache } = require('lru-cache');

// Set up an LRU cache to avoid repeated scraping
const cache = new LRUCache({ max: 100, ttl: 1000 * 60 * 5 });

async function scrapeMovies() {
  // Check cache first
  if (cache.has('movies')) {
    return cache.get('movies');
  }

  // Launch Puppeteer for dynamic content
  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();

  // Replace with the actual URL of the site you want to scrape
  const targetUrl = 'https://example-torrent-site.com/movies';
  await page.goto(targetUrl, { waitUntil: 'domcontentloaded' });

  // Get page content and use Cheerio to parse it
  const html = await page.content();
  const $ = cheerio.load(html);
  let movies = [];

  $('.movie-item').each((i, elem) => {
    const title = $(elem).find('.movie-title').text().trim();
    const link = $(elem).find('a').attr('href');
    movies.push({ id: `${i}`, title, link });
  });

  await browser.close();

  // Cache and return the scraped movies
  cache.set('movies', movies);
  return movies;
}

module.exports = { scrapeMovies };
